import urllib.parse

from Products.Five.browser import BrowserView
from z3c.form import button
from z3c.form import form
from zope import schema
from zope.component import adapts
from zope.component import getUtilitiesFor
from zope.interface import Interface
from zope.interface import implementer
from zope.interface import provider
from zope.event import notify
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleVocabulary

from plone.api import portal
from plone.api import user
from plone.autoform.form import AutoExtensibleForm
from plone.protect.utils import addTokenToUrl

from ..interfaces import IExternalNotificationService
from ..interfaces import INotificationStorage
from ..interfaces import _
from ..interfaces import NotificationRequestedEvent


def _user_display_name(username):
    obj = user.get(userid=username)
    if obj is None:
        return username
    display = obj.getProperty('fullname')
    if not display:
        display = username
    return display


def _adjust_url(url):
    if not url.startswith('http'):
        site = portal.get()
        portal_url = site.absolute_url()
        if url.startswith('/'):
            url = portal_url + url
        else:
            url = portal_url + '/' + url
    return url


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
                         urllib.parse.quote(self.adjust_url(notification.url)))
        url = addTokenToUrl(url)
        return url

    def user_display_name(self, username):
        return _user_display_name(username)

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

    def adjust_url(self, url):
        return _adjust_url(url)


class SiteNotificationsView(BrowserView):

    def list_notifications(self):
        site = portal.get()
        storage = INotificationStorage(site)
        notifications = [n for n in storage.get_notifications()]
        return sorted(notifications, key=lambda n: n.date, reverse=True)

    def user_display_name(self, username):
        return _user_display_name(username)

    def recipient_display_names(self, recipients):
        return [self.user_display_name(userid) for userid in recipients]

    def __call__(self):
        selected = self.request.get('selected', None)
        if selected is not None:
            site = portal.get()
            storage = INotificationStorage(site)
            remove = self.request.get('remove', None)
            if remove is not None:
                storage.remove_notifications(selected)
        return super(SiteNotificationsView, self).__call__()

    def adjust_url(self, url):
        return _adjust_url(url)


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


class NotificationCountView(BrowserView):

    def __call__(self):
        current_user = user.get_current()
        site = portal.get()
        storage = INotificationStorage(site)
        notifications = storage.get_notifications_for_user(current_user.id)
        return str(len(notifications))


@provider(IVocabularyFactory)
def services_vocabulary_factory(object):
    services = getUtilitiesFor(IExternalNotificationService)
    services = [name for name, service in services]
    vocabulary = SimpleVocabulary.fromValues(services)
    return vocabulary


class SendNotificationSchema(Interface):

    note = schema.Text(
        title=_(u'Notification Text'),
    )

    recipients = schema.Text(
        title=_(u'Recipients'),
        description=_(u"Type in a user or group id on each line. Groups "
                      u"need to have the 'group:' prefix"),
    )

    url = schema.URI(
        title=_(u'Notification URL'),
        description=_(u"URL associated with the notification. Will use "
                      u"context URL if not provided"),
        required=False,
    )

    external = schema.Set(
        title=_(u'External Services'),
        description=_(u"Also send notification using selected external "
                      u"services"),
        required=False,
        value_type=schema.Choice(
            vocabulary='collective.notifications.external_services',
        ),
    )

    first_read = schema.Bool(
        title=_(u'Mark Read After First View'),
        description=_(u"If checked, notification will be marked read for "
                      u"all users after first view"),
        default=False,
    )


@implementer(SendNotificationSchema)
class SendNotificationFormAdapter(object):
    adapts(Interface)

    def __init__(self, context):
        self.note = None
        self.recipients = None
        self.url = None
        self.external = None
        self.first_read = None


class SendNotificationForm(AutoExtensibleForm, form.Form):

    schema = SendNotificationSchema
    form_name = 'send_notification_form'

    label = _(u'Send Notification')
    description = _(u"Send a notification to specific site users or groups")

    @button.buttonAndHandler(_(u'Send'))
    def handleSend(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        context = self.context
        notify(NotificationRequestedEvent(context,
                                          data['note'],
                                          data['recipients'],
                                          url=data['url'],
                                          external=list(data['external']),
                                          first_read=data['first_read']
                                          )
               )
        self.status = "Notification sent!"
