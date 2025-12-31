Alerting
=============

FMD provides an alerting mechanism that notifies developers when uncaught, or manually captured exceptions
occur during application runtime. When alerting is enabled, FMD collects information
about the exception and sends it to one or more configured alerting channels.

Supported alerting channels include email notifications, chat platforms, and issue
tracking systems. Each channel requires additional configuration, which is described
in the sections below.

To enable alerting, the following base configuration options must be set:

.. code-block:: python

    [alerting]
    ENABLED=True
    TYPE=<comma_separated_alert_types>

The **ENABLED** option globally activates or deactivates alerting.

The **TYPE** option defines which alerting channels are used. Multiple alerting types
can be specified in a comma-separated list. Available alerting types are:

- "email": send alerts via SMTP email
- "chat": send alerts to supported chat platforms
- "issue": create issues in a GitHub repository

Alerting through Emails
--------------------------

Email alerting sends exception notifications via SMTP. An SMTP server must be
configured to deliver alert messages to one or more recipients.

In addition to the base alerting configuration, the following options are required
to enable email alerting:

.. code-block:: python

    [alerting]
    TYPE=email

    SMTP_HOST=<example_host>
    SMTP_PORT=<example_port>
    SMTP_USER=<example_email_address>
    SMTP_PASSWORD=<example_password>
    SMTP_TO=<comma_separated_recipient_emails>

**SMTP_HOST** and **SMTP_PORT** define the SMTP server connection.

**SMTP_USER** and **SMTP_PASSWORD** are used for authentication.

**SMTP_TO** specifies the list of recipient email addresses.

Alerting through Chat Platforms
--------------------------
Chat alerting delivers exception notifications to supported chat platforms using
incoming webhooks. Currently supported platforms include Slack, Microsoft Teams,
and Rocket.Chat.

In addition to the base alerting configuration, the following options are required
to enable chat alerting:

.. code-block:: python

    [alerting]
    TYPE=chat

    CHAT_PLATFORM=<TEAMS | SLACK | ROCKET_CHAT>
    CHAT_WEBHOOK_URL=<example_webhook_url>

**CHAT_PLATFORM** specifies the chat platform used to deliver alerts and must be set
to exactly one of the listed values.

**CHAT_WEBHOOK_URL** defines the webhook endpoint used to send alerts.


Alerting through Github Issues
--------------------------
Issue alerting automatically creates a new GitHub issue for each exception.

In addition to the base alerting configuration, the following options are required
to enable issue creation:

.. code-block:: python

    [alerting]
    TYPE=issue

    GITHUB_TOKEN=<example_github_token>
    REPOSITORY_OWNER=<example_repo_owner>
    REPOSITORY_NAME=<example_repo_name>

**GITHUB_TOKEN** is used to authenticate with the GitHub API. It should be a personal access token with read and write
permissions for issues on the target repository.

**REPOSITORY_OWNER** and **REPOSITORY_NAME** specify the target repository where issues will be created.
