from datetime import datetime
from BTrees.OOBTree import OOBTree
from Persistence import Persistent
from persistent.list import PersistentList

from zope.interface import implements
from zope.component import adapts
from zope.component import getUtilitiesFor
from zope.component import getUtility
from zope.component.hooks import getSite
from zope.annotation.interfaces import IAnnotations

from plone import api
from plone.app.layout.navigation.interfaces import INavigationRoot
from plone.uuid.interfaces import IUUIDGenerator

from .async import queueJob
from .interfaces import INotificationStorage
from .interfaces import IExternalNotificationService


NOTIFICATION_KEY = 'collective.notifications'
MAIN = '__notifications__'


class NotificationStorage(object):

    adapts(INavigationRoot)
    implements(INotificationStorage)

    def __init__(self, context):
        self.annotations = IAnnotations(context)

    def check_initialized(self, userid=None):
        if NOTIFICATION_KEY not in self.annotations:
            self.annotations[NOTIFICATION_KEY] = OOBTree()
            self.annotations[NOTIFICATION_KEY][MAIN] = PersistentList()
        if userid is not None:
            if userid not in self.annotations[NOTIFICATION_KEY]:
                self.annotations[NOTIFICATION_KEY][userid] = PersistentList()

    def get_notifications(self):
        if NOTIFICATION_KEY not in self.annotations:
            return []
        return self.annotations[NOTIFICATION_KEY][MAIN]

    def add_notification(self, notification):
        self.check_initialized()
        self.annotations[NOTIFICATION_KEY][MAIN].append(notification)

    def get_notifications_for_user(self, userid):
        if NOTIFICATION_KEY not in self.annotations:
            return []
        return self.annotations[NOTIFICATION_KEY][userid]

    def add_notification_for_user(self, userid, uid):
        self.check_initialized(userid)
        self.annotations[NOTIFICATION_KEY][userid].append((uid, False))

    def clear_notifications_for_users(self, users, uids):
        if not isinstance(users, list):
            users = [users]
        if not isinstance(uids, list):
            uids = [uids]
        for user in users:
            notifications = self.get_notifications_for_user(user)
            for notification, read in notifications[:]:
                if notification in uids:
                    notifications.remove((notification, read))

    def get_notification(self, uid):
        notifications = self.get_notifications()
        notification = None
        for notification in notifications:
            if notification.uid == uid:
                break
        return notification

    def mark_read_for_users(self, users, uids):
        if not isinstance(users, list):
            users = [users]
        if not isinstance(uids, list):
            uids = [uids]
        for user in users:
            notifications = self.get_notifications_for_user(user)
            for index, notification in enumerate(notifications):
                notification_uid, read = notification
                if notification_uid in uids:
                    notifications[index] = (notification_uid, True)

    def mark_unread_for_users(self, users, uids):
        if not isinstance(users, list):
            users = [users]
        if not isinstance(uids, list):
            uids = [uids]
        for user in users:
            notifications = self.get_notifications_for_user(user)
            for index, notification in enumerate(notifications):
                notification_uid, read = notification
                if notification_uid in uids:
                    notifications[index] = (notification_uid, False)

    def remove_notifications(self, uids):
        if not isinstance(uids, list):
            uids = [uids]
        notifications = self.get_notifications()
        for notification in notifications[:]:
            if notification.uid in uids:
                for user in notification.recipients:
                    self.clear_notifications_for_users(user, notification.uid)
                notifications.remove(notification)


class Notification(Persistent):

    def __init__(self,
                 context,
                 note,
                 recipients,
                 user=None,
                 url=None,
                 first_read=False,
                 external=None):
        uid = getUtility(IUUIDGenerator)()
        self.uid = uid
        self.date = datetime.now()
        self.context = getattr(context, 'UID', False) and context.UID() or context.id
        self.note = note
        self.recipients = self.get_recipients(recipients)
        self.first_read = first_read
        self.external = external
        if user is None:
            user = api.user.get_current()
            if user is not None:
                user = user.id
        self.user = user
        if url is None:
            url = context.absolute_url()
        self.url = url

    def get_recipients(self, recipients):
        recipient_list = []
        if not isinstance(recipients, list):
            recipients = [recipients]
        for recipient in recipients:
            if recipient.startswith('group:'):
                group = recipient.split(':')[1]
                if group == 'Members':
                    users = [u.id for u in api.user.get_users()]
                else:
                    users = [u.id for u in api.user.get_users(groupname=group)]
                for user in users:
                    recipient_list.append(user)
            else:
                recipient_list.append(recipient)
        return recipient_list

    def notify(self):
        site = getSite()
        storage = INotificationStorage(site)
        for userid in self.recipients:
            storage.add_notification_for_user(userid, self.uid)

    def notify_external(self):
        external = self.external
        if external is not None:
            if not isinstance(external, list):
                external = [external]
            services = getUtilitiesFor(IExternalNotificationService)
            for name, service in services:
                if name in external:
                    service.send(self)


def handle_notification_requested(event):
    notification = Notification(event.object,
                                event.note,
                                event.recipients,
                                event.user,
                                event.url,
                                event.first_read,
                                event.external)
    site = getSite()
    storage = INotificationStorage(site)
    storage.add_notification(notification)
    notification.notify()
    queueJob(notification.uid)
