# coding=utf-8
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.testing import z2
from zope.configuration import xmlconfig

try:
    from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FIXTURE
    BASE_FIXTURE = PLONE_APP_CONTENTTYPES_FIXTURE
except ImportError:
    from plone.app.testing import PLONE_FIXTURE
    BASE_FIXTURE = PLONE_FIXTURE


class Notifications(PloneSandboxLayer):
    defaultBases = (BASE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # load ZCML
        import collective.notifications
        import z3c.jbot
        xmlconfig.file('configure.zcml', z3c.jbot,
                       context=configurationContext)
        xmlconfig.file('configure.zcml', collective.notifications,
                       context=configurationContext)
        z2.installProduct(app, 'collective.notifications')

    def setUpPloneSite(self, portal):
        # install into the Plone site
        applyProfile(portal, 'collective.notifications:default')
        setRoles(portal, TEST_USER_ID, ('Member', 'Manager'))


Notifications_FIXTURE = Notifications()
Notifications_INTEGRATION_TESTING = IntegrationTesting(
    bases=(Notifications_FIXTURE,), name="Notifications:Integration")
Notifications_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(Notifications_FIXTURE,), name="Notifications:Functional")
