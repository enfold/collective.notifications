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

    user = Attribute("The user who triggered the event.")
    object = Attribute("The subject of the event.")
    note = Attribute("Additional information for the event.")
    recipients = Attribute("List of users to notify.")
    url = Attribute("URL for notification action.")
    first_read = Attribute("Mark as read for all recipients on first read.")
    external = Attribute("List of external services to notify.")


@implementer(INotificationRequestedEvent)
class NotificationRequestedEvent(object):

    def __init__(self,
                 user,
                 object,
                 note,
                 recipients,
                 url=None,
                 first_read=False,
                 external=None):
        self.user = user
        self.object = object
        self.note = note
        self.recipients = recipients
        self.url = url
        self.first_read = first_read
        self.external = external
