from zope.annotation.interfaces import IAnnotations

from collective.notifications.notifications import NOTIFICATION_KEY


def uninstall(context):
    if not context.readDataFile('collective.notifications.uninstall.txt'):
        return

    portal = context.getSite()
    annotations = IAnnotations(portal)
    if NOTIFICATION_KEY not in annotations:
        return
    del annotations[NOTIFICATION_KEY]
