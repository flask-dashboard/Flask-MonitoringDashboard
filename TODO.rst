TODO List
=========================================================================

All things that can improved in Flask Monitoring Dashboard are listed below.

Features to be implemented
--------------------------
- [ ] Pagination of results. See this page: http://flask.pocoo.org/snippets/44/

  This process is especially useful for the following results:

  - Page '/measurements/overview'
  - Page '/measurements/heatmap' - Heatmap for each week
  - Page '

- [ ] Updating the Outlier-object, as it now works by writing all stack-traces to a file.
  Once  this is done, read everything from it.
  This is a security flaw, and doesn't produce the right value if multiple requests are using this file at the same
  time.

Work in progress
----------------
*Use this section if someone is already working on an item above.*
