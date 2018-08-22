from BTrees.OOBTree import OOBTree
from persistent.list import PersistentList
from zope.annotation.interfaces import IAnnotations

from collective.notifications.notifications import MAIN
from collective.notifications.notifications import NOTIFICATION_KEY


def change_main_storage(context):
    """ Change main notification storage to use btree """
    annotations = IAnnotations(context.__parent__)
    if NOTIFICATION_KEY not in annotations:
        return
    if MAIN not in annotations[NOTIFICATION_KEY]:
        return
    if isinstance(annotations[NOTIFICATION_KEY][MAIN], PersistentList):
        notifications = {n.uid: n for n in annotations[NOTIFICATION_KEY][MAIN]}
        annotations[NOTIFICATION_KEY][MAIN] = OOBTree()
        annotations[NOTIFICATION_KEY][MAIN].update(notifications)
