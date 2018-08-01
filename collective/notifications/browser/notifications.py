import urllib

from Products.Five.browser import BrowserView

from plone.api import portal
from plone.api import user
from plone.protect.utils import addTokenToUrl

from ..interfaces import INotificationStorage


class NotificationsView(BrowserView):

    def list_notifications(self):
        current_user = user.get_current()
        site = portal.get()
        storage = INotificationStorage(site)
        notifications = storage.get_notifications_for_user(current_user.id)
        return [(storage.get_notification(n), r) for n, r in notifications]

    def mark_read_url(self, notification):
        site = portal.get()
        url = "{}/@@notification-read?uid={}&url={}"
        url = url.format(site.absolute_url(),
                         notification.uid,
                         urllib.quote(notification.url))
        url = addTokenToUrl(url)
        return url

    def __call__(self):
        selected = self.request.get('selected', None)
        if selected is not None:
            current_user = user.get_current()
            site = portal.get()
            storage = INotificationStorage(site)
            read = self.request.get('read', None)
            if read is not None:
                storage.mark_read_for_users(current_user.id, selected)
            unread = self.request.get('unread', None)
            if unread is not None:
                storage.mark_unread_for_users(current_user.id, selected)
            clear = self.request.get('clear', None)
            if clear is not None:
                storage.clear_notifications_for_users(current_user.id, selected)
        return super(NotificationsView, self).__call__()


class SiteNotificationsView(BrowserView):

    def list_notifications(self):
        site = portal.get()
        storage = INotificationStorage(site)
        return storage.get_notifications()

    def __call__(self):
        selected = self.request.get('selected', None)
        if selected is not None:
            site = portal.get()
            storage = INotificationStorage(site)
            remove = self.request.get('remove', None)
            if remove is not None:
                storage.remove_notifications(selected)
        return super(SiteNotificationsView, self).__call__()


class NotificationReadView(BrowserView):

    def __call__(self):
        current_user = user.get_current()
        site = portal.get()
        storage = INotificationStorage(site)
        uid = self.request.get('uid', None)
        if uid is not None:
            storage.mark_read_for_users(current_user.id, uid)
            notification = storage.get_notification(uid)
            if notification is not None and notification.first_read:
                storage.mark_read_for_users(notification.recipients, uid)
        url = self.request.get('url', None)
        if url is not None:
            self.request.response.redirect(url)


class NotificationsWaitingView(BrowserView):

    def __call__(self):
        current_user = user.get_current()
        site = portal.get()
        storage = INotificationStorage(site)
        notifications = storage.get_notifications_for_user(current_user.id)
        notifications = [n for (n, r) in notifications if not r]
        return str(len(notifications))
