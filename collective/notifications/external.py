import email
import email.policy
from Acquisition import aq_base
from plone import api
from zope.interface import implementer

from .interfaces import IExternalNotificationService
try:
    from celery.utils.log import get_task_logger
    logger = get_task_logger(__name__)
except ImportError:
    import logging
    logger = logging.getLogger('collective.notifications')


@implementer(IExternalNotificationService)
class EmailNotifier(object):

    def send(self, notification):
        portal = api.portal.get()
        base_notification = aq_base(notification)
        subject = getattr(base_notification, 'email_subject')
        if not subject:
            subject = "Notification from {}".format(portal.title)
        email_body = getattr(base_notification, 'email_body')
        if not email_body:
            email_body = notification.note
        msg = email.message_from_string(email_body)

        content_type = getattr(base_notification, 'email_content_type')
        if content_type is not None:
            del msg['Content-Type']
            msg['Content-type'] = content_type
        msg.set_charset('utf-8')
        name = api.portal.get_registry_record('plone.email_from_name')
        address = api.portal.get_registry_record('plone.email_from_address')
        if not address:
            logger.warn('Unable to send message. An email from address has '
                        'not been configured for this site.')
            return
        mfrom = email.utils.formataddr((name, address))
        mailhost = portal.MailHost
        for recipient in notification.recipients:
            user = api.user.get(userid=recipient)
            if not user:
                msg = ('Was not able to find user for userid %s. Unable '
                       'to send notification email' % recipient)
                logger.warn(msg)
                continue

            address = user.getProperty('email', '')
            if not address:
                msg = ('The %s user has no email address. Unable to send '
                       'an email to them.')
                logger.warn(msg % recipient)
                continue
            mailhost.send(msg,
                          subject=subject,
                          mfrom=mfrom,
                          mto=address,
                          immediate=True,
                          charset='utf-8')
