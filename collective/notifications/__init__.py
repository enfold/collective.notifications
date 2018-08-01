from zope.i18nmessageid import MessageFactory
MessageFactory = MessageFactory('collective.notifications')


def initialize(context):
    """Initializer called when used as a Zope 2 product."""
