0.6
---

- Remove support for plone.app.async.

- Add python 3 support

- Support supplying separate text for email notifications.

- Don't fail if there is no site from email address configured.


0.5
---

- Add tests.

- #2612401: Don't fail if the user can't be found.
  [JL 2019-02-28]

- #2745054: Show Notifications menu item if there are read notifications and no
  unread notifications.
  [JL 2019-05-29]

- #2745050: Only send one notification to a user.
  [JL 2019-05-29]

- #2755049: If notification url does not start with http append it to portal_url on display.
  [JL 2019-05-30]
