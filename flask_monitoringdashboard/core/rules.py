def get_rules():
    """
    :return: A list of the current rules in the attached Flask app
    """
    from flask_monitoringdashboard import config, user_app

    rules = user_app.url_map.iter_rules()
    return [r for r in rules if not r.rule.startswith('/' + config.link)
            and not r.rule.startswith('/static-' + config.link)]
