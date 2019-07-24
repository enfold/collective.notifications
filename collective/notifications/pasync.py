# coding=utf-8
from zope.component.hooks import getSite

from .interfaces import INotificationStorage

try:
    from collective.notifications.tasks import queue_job
    from celery.utils.log import get_task_logger
    logger = get_task_logger(__name__)
except ImportError:
    queue_job = None
    import logging
    logger = logging.getLogger('collective.notifications')


def runJob(notification_uid):
    site = getSite()
    storage = INotificationStorage(site)
    notification = storage.get_notification(notification_uid)
    notification.notify_external()


def queueJob(notification_uid):
    """
    queue a job async if available.
    otherwise, just run normal
    """
    if queue_job:
        queue_job.delay(notification_uid)
    else:
        runJob(notification_uid)
