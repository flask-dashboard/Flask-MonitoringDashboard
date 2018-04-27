from flask import request
from flask_wtf import FlaskForm
from wtforms import SubmitField
from wtforms.fields.html5 import IntegerRangeField


class SliderForm(FlaskForm):
    """
        Class for generating a slider that can be used to reduce the graph.
    """
    slider = IntegerRangeField()
    submit = SubmitField('Submit')
    type = 'SliderForm'

    def get_slider_value(self):
        """
        :return: the value from the slider
        """
        if 'slider' in request.form:
            return request.form['slider']
        return self.start_value


def get_slider_form(slider_max=100):
    """
    Return a SliderForm with the range from 0 to slider_max
    :param slider_max: maximum value for the slider
    :return: a SliderForm with the range (0 ... slider_max)
    """
    form = SliderForm(request.form)
    form.min_value = 1
    form.max_value = slider_max
    if 'slider' in request.form:
        form.start_value = request.form['slider']
    else:
        form.start_value = min(max(form.min_value, form.min_value + (slider_max - form.min_value) // 2), form.max_value)
    return form
