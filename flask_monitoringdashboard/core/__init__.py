"""
    Core files for the Flask Monitoring Dashboard. It contains the following packages:
    - config handles the configuration-file
    - forms handles generating and processing WTF-forms
    - plot handles the plotly library
    - profiler handles profiling requests

    It also contains the following files
    - auth.py handles authentication
    - colors.py handles color-hash
    - group_by.py handles the group_by functionality
    - info_box.py handles the generation of information box, one for each graph
    - measurements.py contains a number of wrappers, one for each monitoring level
    - rules.py includes a function that retrieves all rules of the entire Flask
      application, or for a specific endpoint.
    - timezone: handles utc-timezone <==> local-timezone
    - utils: for other functions
"""
