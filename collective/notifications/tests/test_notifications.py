from plone.app.testing import SITE_OWNER_NAME

from .base import BaseTestCase
from ..notifications import Notification


class TestNotifications(BaseTestCase):

    def setUp(self):
        super(TestNotifications, self).setUp()
        self.login_as_portal_owner()

    def test_create_notification(self):
        notification = Notification(self.portal,
                                    "this is a notification",
                                    ['user1', 'user2'])

        self.assertEqual(
            self.portal.id,
            notification.context,
            'Unexpected context value for notification'
        )

        self.assertEqual(
            ['user1', 'user2'],
            notification.recipients,
            'Notification recipients do not match'
        )

        self.assertEqual(
            SITE_OWNER_NAME,
            notification.user,
            'Unexpected user value for notification'
        )

        self.assertEqual(
            '',
            notification.url,
            'Unexpected URL value for notification'
        )

        self.assertEqual(
            "this is a notification",
            notification.note,
            'Unexpected note value for notification'
        )

        self.assertEqual(
            None,
            notification.external,
            'Unexpected external value for notification'
        )

        self.assertEqual(
            False,
            notification.first_read,
            'Unexpected first_read value for notification'
        )
