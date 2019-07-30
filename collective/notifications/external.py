import email
import email.policy
from Acquisition import aq_base
from plone import api
from zope.interface import implementer

from .interfaces import IExternalNotificationService


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
        mfrom = email.utils.formataddr((name, address))
        mailhost = portal.MailHost
        for recipient in notification.recipients:
            user = api.user.get(userid=recipient)
            address = user.getProperty('email', None)
            if not address:
                continue
            mailhost.send(msg,
                          subject=subject,
                          mfrom=mfrom,
                          mto=address,
                          immediate=True,
                          charset='utf-8')
