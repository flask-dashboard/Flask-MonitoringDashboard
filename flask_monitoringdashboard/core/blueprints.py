def get_blueprint(endpoint_name):
    blueprint = endpoint_name
    if '.' in endpoint_name:
        blueprint = endpoint_name.split('.')[0]
    return blueprint
