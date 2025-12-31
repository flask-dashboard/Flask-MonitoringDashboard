Change Log
=========================================================================

All notable changes to this project will be documented in this file.
This project adheres to `Semantic Versioning <http://semver.org/>`_.
Please note that the changes before version 1.10.0 have not been documented.

v5.1.0
----------
**Minor Release - Exception Alerting**

Added
^^^^^
- Optional, configurable alerting on uncaught or user-defined exceptions
- 3 types of possible alerting channels:

  - Email via SMTP
  - Chat platforms (Slack, Microsoft Teams, Rocket.Chat)
  - Issue tracker (Github Issues)
- Configuration parameters visualized on the "Alerting settings" page

Changed
^^^^^^^
- Added several alerting configuration parameters
- Added jinja2 to requirements-micro.txt for email template rendering
- Endpoint-specific exception pages now support URL anchor-based navigation

v5.0.2
----------
**Bug Fix Release**

Note: v5.0.1 publish to PyPI failed due to test failures. This release includes all fixes from 5.0.1 plus additional corrections.

Fixed
^^^^^
- **Build**: Fixed broken 5.0.0 release - Angular frontend is now properly built before publishing to PyPI
- **Deprecation**: Replaced deprecated ``datetime.utcnow()`` with ``datetime.now(timezone.utc)`` throughout codebase
- **Deprecation**: Replaced deprecated ``datetime.utcfromtimestamp()`` with ``datetime.fromtimestamp(..., tz=timezone.utc)``
- **Deprecation**: Replaced ``datetime.UTC`` with ``datetime.timezone.utc`` for Python 3.11+ compatibility
- **Timezone**: Fixed timezone-aware datetime handling in reporting and database operations
- **Timezone**: Fixed missing timezone info in hourly load heatmap calculations (controllers/requests.py)
- **Tests**: Updated test fixtures to properly handle timezone-aware datetimes

Contributors
^^^^^^^^^^^^
Special thanks to: Alex Knop (@aknopper) for identifying and fixing the deprecated datetime usage, and @klnyzzz33 for fixing datetime conversion errors

v5.0.0
----------
**Major Release - Exception Monitoring & Stability Improvements**

Added
^^^^^
- **Exception Monitoring**

  - Automatic capture of uncaught exceptions across all endpoints
  - User-defined exception capture with context
  - Exception grouping by stack trace and endpoint
  - Detailed stack trace visualization with syntax highlighting
  - Exception occurrence tracking and statistics
  - Database schema additions: ExceptionInfo, ExceptionFrame, FunctionLocation, FilePath, ExceptionType, ExceptionMessage
- Exception dashboard with filterable views
- Endpoint-specific exception pages
- Exception pruning as part of database maintenance

Changed
^^^^^^^
- **BREAKING**: Minimum Python version raised from 3.8 to 3.10
- **Security**: Updated requests dependency from 2.32.0 to 2.32.4 (addresses CVE-2024-35195)
- **Database**: UTF-8 collation support for exception messages with emoji and special characters
- **Timezone**: Fixed UTC timezone handling issues
- **UI**: Improved sorting on Overview table (now works correctly with median request durations)
- **UI**: Resolved sorting issues in Google Chrome browser
- **UI**: Enhanced pagination on Overview page
- **Performance**: Optimized exception stack trace storage to reduce redundancy
- Flask 2.3+ compatibility (replaced deprecated `before_app_first_request`)
- SQLAlchemy 2.0 compatibility improvements

Fixed
^^^^^
- Telemetry consent can be properly dismissed
- MySQL query compatibility for exception monitoring
- Loading spinner placement on Overview page
- Sorting now compares numbers correctly (not as strings)
- Password hash column size increased to support newer Werkzeug versions

Contributors
^^^^^^^^^^^^
Special thanks to: Natalie, Carmen, Albert, and all community contributors

v4.0.5
----------
Changed

- Security: Updated requests dependency from 2.32.0 (yanked) to 2.32.4 to address CVE-2024-35195
- Fixed: Removed hard pin on requests dependency to allow for security updates

v4.0.4
----------
Changed

Natalie, Carmen, and Albert
- Bugfix: the "fixed" sorting from last version compared numbers as strings.

v4.0.3
----------
Changed

Natalie, Carmen, and Albert
- Bugfix: the sorting on the Overview table works for median request durations.
- Bugfix: resolved sorting issues with the Overview table in Google Chrome.
- Fixed placement of loading spinner on Overview page.

v4.0.2
----------
Changed

Natalie, Carmen, and Albert
- Bugfix: the telemetry consent can be dismissed again
- New and nicer pagination of the Overview table



v4.0.1
----------
Changed

Natalie, Carmen, and Albert
- Bugfix: queries work also with MySQL now


v4.0.0
----------
Changed

- Natalie, Carmen and Albert added support for monitoring exceptions



v3.3.2
----------
Changed

- Changed functools.cache to lru_cache to support python 3.8
- Added python version to telemetry


v3.3.1
----------
Changed

- Telemetry now uses dynamic server-ip  
- Removed survey
- FollowUp questions refactored

v3.3.0
----------
Changed

- Added database pruning feature

v3.2.2
----------
Changed

- Fixed Sphinx documentation

v3.2.1
----------
Changed

- Removed sentry artifacts in code

v3.2.0
----------
Changed

- Upgraded multiple frontend packages for enhanced security and performance.
- Added survey alert
- Added telemetry alert and functionality


v3.1.2
----------
Changed

- Compatibility with Flask>=2.x Removed the call to `before_app_first_request` and replaced it with `record_once` as per the PR of [@FlorianRhiem](https://github.com/FlorianRhiem).

v3.1.0
----------
Changed

- Added support for Python 3.8
- Started using pytest instead of python's unittest
- Started using Webpack for frontend packaging
- Improved reports
- Moved to Github Actions from Travis for CI/CD
- Improved docstrings
- Various bug fixes


v3.0.9
----------
Changed

- Fixed upgrade message bug
- Fixed Heroku deployment


v3.0.8
----------
Changed

- Fixed the changelog; functionality is the same as 3.0.7 :)


v3.0.7 
----------
Changed

- Added a first version of the Reporting functionality
- Improved usability of the overview table
- Fixed the issue with some table columns being sorted as text as opposed to numbers
- A few other bug fixes


v3.0.6
----------
Changed

- Removed profiler feature from monitoring level 2
- Added outlier detection feature to monitoring level 3
- Configurable profiler sampling period, with 5 ms default
- Implemented an in-memory cache for performance improvements

v3.0.0
----------
Changed

- Tracking also status codes
- Display times as numbers to make them sortable
- Add leading slash to blueprint paths
- Added status codes with corresponding views

v2.1.1
----------
Changed

- Default monitoring level is now 1
- Fixed bug causing config file not being parsed
- Monitoring level can be set from the 'detail' section
- Improved README

v2.1.0
----------
Changed

- Frontend is now using AngularJS
- Removed TestMonitor
- Added Custom graphs
- Fixed Issue #206
- Added support for Python 3.7
- Updated documentation
- Updated unit tests

v2.0.7
----------
Changed

- Fixed Issue #174

- Fixed issue with profiler not going into code

- Implemented a Sunburst visualization of the Grouped Profiler

- Improved test coverage

- Improved python-doc

- Added functionality to download the outlier data

- Dropped support for Python 3.3 and 3.4


v2.0.0
----------
Changed

- Added a configuration option to prefix a table in the database

- Optimize queries, such that viewing data is faster

- Updated database scheme

- Implemented functionality to customize time window of graphs

- Implemented a profiler for Request profiling

- Implemented a profiler for Endpoint profiling

- Refactored current code, which improves readability

- Refactoring of Test-Monitoring page

- Identify testRun by Travis build number


v1.13.0
----------
Changed

- Added boxplot of CPU loads

- Updated naming scheme of all graphs

- Implemented two configuration options: the local timezone and the option to automatically monitor new endpoints

- Updated the Test-Monitoring initialization

- Updated Database support for MySQL

v1.12.0
-------
Changed

- Removed two graphs: hits per hour and execution time per hour

- New template design

- Refactored backhand of the code

- Updated Bootstrap 3.0 to 4.0

- Setup of Code coverage


v1.11.0
-------
Changed

- Added new graph: Version usage

- Added column (Hits in past 7 days) in Measurements Overview

- Fixed bug with configuration

- Changed rows and column in outlier-table

- Added TODO List

- Updated functionality to retrieve the stacktrace of an Outlier

- Fixed bug with white colors from the config option


v1.10.0
----------
Changed

- Added security for automatic endpoint-data retrieval.

- Added test for export_data-endpoints

- Added MIT License.

- Added documentation
