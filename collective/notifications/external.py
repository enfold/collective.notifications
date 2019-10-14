import email
from Acquisition import aq_base
from plone import api
from zope.interface import implements

from .interfaces import IExternalNotificationService


class EmailNotifier(object):

    implements(IExternalNotificationService)

    def send(self, notification):
        portal = api.portal.get()
        base_notification = aq_base(notification)
        subject = getattr(base_notification, 'email_subject', None)
        if not subject:
            subject = "Notification from {}".format(portal.title)
        email_body = getattr(base_notification, 'email_body', None)
        if not email_body:
            email_body = notification.note
        msg = email.message_from_string(email_body)
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
