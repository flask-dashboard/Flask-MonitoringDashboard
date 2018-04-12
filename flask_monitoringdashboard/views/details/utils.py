from flask import url_for, request
from flask_monitoringdashboard.database.endpoint import get_monitor_rule
from flask_wtf import FlaskForm
from werkzeug.routing import BuildError
from wtforms import SelectMultipleField, SubmitField

BUBBLE_SIZE_RATIO = 1250


def get_details(endpoint):
    return {
        'endpoint': endpoint,
        'rule': get_monitor_rule(endpoint),
        'url': get_url(endpoint)
    }


def formatter(ms):
    """
    formats the ms into seconds and ms
    :param ms: the number of ms
    :return: a string representing the same amount, but now represented in seconds and ms.
    """
    sec = int(ms) // 1000
    ms = int(ms) % 1000
    if sec == 0:
        return '{0}ms'.format(ms)
    return '{0}.{1}s'.format(sec, ms)


def get_url(end):
    """
    Returns the URL if possible.
    URL's that require additional arguments, like /static/<file> cannot be retrieved.
    :param end: the endpoint for the url.
    :return: the url_for(end) or None,
    """
    try:
        return url_for(end)
    except BuildError:
        return None


def get_form(data):
    # create a form to make a selection
    choices = []
    for d in list(data):
        choices.append((d, d))

    class SelectionForm(FlaskForm):
        selection = SelectMultipleField(
            'Pick Things!',
            choices=choices,
        )
        submit = SubmitField('Render graph')

    form = SelectionForm(request.form)
    selection = []
    if request.method == 'POST':
        selection = [str(item) for item in form.data['selection']]

    return form, selection
