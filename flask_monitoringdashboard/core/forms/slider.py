from flask import request
from flask_wtf import FlaskForm
from wtforms import SubmitField
from wtforms.fields.html5 import IntegerRangeField

DEFAULT_SLIDER_VALUE = 10


class SliderForm(FlaskForm):
    """
        Class for generating a slider that can be used to reduce the graph.
    """
    slider = IntegerRangeField()
    submit = SubmitField('Update')
    title = 'Select a number below for reducing the size of the graph'

    def get_slider_value(self):
        """
        :return: the value from the slider
        """
        if 'slider' in request.form:
            return request.form['slider']
        return self.start_value

    def content(self):
        return '''
          <div class="row">
            <div class="col-sm-3"><span>{}</span></div>
            <div class="col-sm-3" style="text-align: center"><output id="outputValue">{}</output></div>
            <div class="col-sm-3" style="text-align: right"><span>{}</span></div>
          </div>
          <div class="row">
            <div class="col-sm-9">{}</div>
            <div class="col-sm-3">{}</div>
          </div>'''.format(self.min_value, self.start_value, self.max_value,
                           self.slider(style="width: 100%;", oninput="outputValue.value=this.value",
                                       min=self.min_value, max=self.max_value, value=self.start_value),
                           self.submit(class_="btn btn-primary btn-block"))


def get_slider_form(slider_max=100, title=None):
    """
    Return a SliderForm with the range from 0 to slider_max
    :param slider_max: maximum value for the slider
    :param title: override the default title
    :return: a SliderForm with the range (0 ... slider_max)
    """
    form = SliderForm(request.form)
    form.min_value = 1
    form.max_value = slider_max
    if title:
        form.title = title
    if 'slider' in request.form:
        form.start_value = request.form['slider']
    else:
        form.start_value = min(DEFAULT_SLIDER_VALUE, slider_max)
    return form
