def get_rules(endpoint_name=None):
    """
    :param endpoint_name: if specified, only return the available rules to that endpoint
    :return: A list of the current rules in the attached Flask app
    """
    from flask_monitoringdashboard import config, user_app
    try:
        rules = user_app.url_map.iter_rules(endpoint=endpoint_name)
    except KeyError:
        return []
    return [r for r in rules
            if not r.rule.startswith('/' + config.link)
            and not r.rule.startswith('/static-' + config.link)
            and not r.endpoint == 'static']
