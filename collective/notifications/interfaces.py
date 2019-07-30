from zope.i18nmessageid import MessageFactory
from zope.interface import Interface
from zope.interface.declarations import implementer
from zope.interface.interface import Attribute


_ = MessageFactory('collective.notifications')


class IExternalNotificationService(Interface):
    """An external service to send notifications."""


class INotificationStorage(Interface):
    """A persistent storage for notifications."""


class INotificationRequestedEvent(Interface):
    """An event for signaling requests for notifications."""

    object = Attribute("The subject of the event.")
    note = Attribute("Additional information for the event.")
    recipients = Attribute("List of users to notify.")
    user = Attribute("The user who triggered the event.")
    url = Attribute("URL for notification action.")
    first_read = Attribute("Mark as read for all recipients on first read.")
    external = Attribute("List of external services to notify.")
    email_subject = Attribute('Optional subject for notification email')
    email_body = Attribute('Optional body for notification email')
    email_content_type = Attribute('Optional value for the Content-Type '
                                   'header of the notification email')


@implementer(INotificationRequestedEvent)
class NotificationRequestedEvent(object):

    def __init__(self,
                 object,
                 note,
                 recipients,
                 user=None,
                 url=None,
                 first_read=False,
                 external=None,
                 email_subject=None,
                 email_body=None,
                 email_content_type=None):
        self.object = object
        self.note = note
        self.recipients = recipients
        self.user = user
        self.url = url
        self.first_read = first_read
        self.external = external
        self.email_subject = email_subject
        self.email_body = email_body
        self.email_content_type = email_content_type
