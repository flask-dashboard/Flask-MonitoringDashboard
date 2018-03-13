TODO List
=========================================================================

All things that can improved in Flask Monitoring Dashboard are listed below.

Features to be implemented
--------------------------
- [ ] Pagination of results. See this page: http://flask.pocoo.org/snippets/44/

  This process is especially useful for the following results:

  - Page '/rules' - Max 20 endpoints per table.
  - Page '/measurements/overview' - Max 20 endpoints per table.
  - Page '/measurements/heatmap' - Heatmap for each week
  - Page '/measurements/requests' - Barplot for each week
  - Page '/measurements/versions' - Max 10 versions per plot
  - Page '/measurements/endpoints' - Max 10 endpoints per plot.
  - Page '/result/<endpoint>/heatmap - Heatmap for each week.
  - Page '/result/<endpoint>/time_per_hour' - barplot for each week.
  - Page '/result/<endpoint>/hits_per_hour' - barplot for each week.
  - Page '/result/<endpoint>/time_per_version' - Max 10 versions per plot.
  - Page '/result/<endpoint>/outliers' - Max 20 results per table.

[ ] Refactor all measurement-endpoints in a Blueprint

Work in progress
----------------
*Use this section if someone is already working on an item above.*
