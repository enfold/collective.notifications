import email

from plone import api
from zope.interface import implementer

from .interfaces import IExternalNotificationService


@implementer(IExternalNotificationService)
class EmailNotifier(object):

    def send(self, notification):
        portal = api.portal.get()
        subject = "Notification from {}".format(portal.title)
        msg = email.message_from_string(notification.note)
        msg.set_charset('utf-8')
        name = api.portal.get_registry_record('plone.email_from_name')
        address = api.portal.get_registry_record('plone.email_from_address')
        mfrom = email.utils.formataddr((name, address))
        mailhost = portal.MailHost
        for recipient in notification.recipients:
            user = api.user.get(userid=recipient)
            address = user.getProperty('email', None)
            if address is None:
                continue
            mailhost.send(msg,
                          subject=subject,
                          mfrom=mfrom,
                          mto=address,
                          immediate=True,
                          charset='utf-8')
