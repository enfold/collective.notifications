from celery.utils.log import get_task_logger
from collective.celery import task


logger = get_task_logger(__name__)


@task(name="notify")
def queue_job(notification_uid):
    from collective.notifications.async import runJob
    logger.warn('Sending notification')
    runJob(notification_uid)
