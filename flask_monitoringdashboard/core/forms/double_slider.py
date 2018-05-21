from flask import request
from flask_wtf import FlaskForm
from wtforms import SubmitField
from wtforms.fields.html5 import IntegerRangeField

from flask_monitoringdashboard.core.forms.slider import DEFAULT_SLIDER_VALUE


class DoubleSliderForm(FlaskForm):
    """
        Class for generating a slider that can be used to reduce the graph.
    """
    slider0 = IntegerRangeField()
    slider1 = IntegerRangeField()
    submit = SubmitField('Update')
    title = 'Select two numbers below for reducing the size of the graph'
    subtitle = ['Subtitle0', 'Subtitle1']

    def get_slider_value(self, index):
        """
        :return: the value from the slider
        """
        name = 'slider{}'.format(index)
        if name in request.form:
            return request.form[name]
        return self.start_value[index]

    def content(self):
        return '''
          <div class="row"><b class="col">{}</b></div>
          <div class="row">  
            <div class="col-sm-3"><span>{}</span></div>
            <div class="col-sm-3" style="text-align: center"><output id="outputValue0">{}</output></div>
            <div class="col-sm-3" style="text-align: right"><span>{}</span></div>
          </div>
          <div class="row">
            <div class="col-sm-9">{}</div>
          </div>
          <div class="row"><b class="col">{}</b></div>
          <div class="row">  
            <div class="col-sm-3"><span>{}</span></div>
            <div class="col-sm-3" style="text-align: center"><output id="outputValue1">{}</output></div>
            <div class="col-sm-3" style="text-align: right"><span>{}</span></div>
          </div>
          <div class="row">
            <div class="col-sm-9">{}</div>
            <div class="col-sm-3">{}</div>
          </div>'''.format(self.subtitle[0], self.min_value[0], self.start_value[0], self.max_value[0],
                           self.slider0(style="width: 100%;", oninput="outputValue0.value=this.value",
                                        min=self.min_value[0], max=self.max_value[0], value=self.start_value[0]),
                           self.subtitle[1], self.min_value[1], self.start_value[1], self.max_value[1],
                           self.slider1(style="width: 100%;", oninput="outputValue1.value=this.value",
                                        min=self.min_value[1], max=self.max_value[1], value=self.start_value[1]),
                           self.submit(class_="btn btn-primary btn-block"))


def get_double_slider_form(slider_max=(100, 100), title=None, subtitle=None):
    """
    Return a SliderForm with the range from 0 to slider_max
    :param slider_max: maximum value for the slider
    :param title: override the default title
    :param subtitle: override the default titles of the 2 sliders
    :return: a SliderForm with the range (0 ... slider_max)
    """
    form = DoubleSliderForm(request.form)
    form.min_value = (1, 1)
    form.max_value = slider_max
    if title:
        form.title = title
    if subtitle:
        form.subtitle = subtitle
    if 'slider0' in request.form:
        form.start_value = [request.form['slider0'], request.form['slider1']]
    else:
        form.start_value = [min(DEFAULT_SLIDER_VALUE, form.max_value[i]) for i in range(2)]
    return form
