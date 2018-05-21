import datetime

from flask import request
from flask_wtf import FlaskForm
from wtforms import validators, SubmitField
from wtforms.fields.html5 import DateField

from flask_monitoringdashboard.core.timezone import to_local_datetime

DATE_FORMAT = '%Y-%m-%d'


class SelectDateRangeForm(FlaskForm):
    """ Used for selecting two dates, which together specify a range. """
    start_date = DateField('Start date', format=DATE_FORMAT, validators=[validators.data_required()])
    end_date = DateField('End date', format=DATE_FORMAT, validators=[validators.data_required()])
    submit = SubmitField('Update')
    title = 'Select the time interval'

    def get_days(self):
        """
        :return: A list with datetime.date object from form.start_date to (including) form.end_date
        """
        delta = self.end_date.data - self.start_date.data
        return [self.start_date.data + datetime.timedelta(days=i) for i in range(delta.days + 1)]

    def content(self):
        return '''
          <div class="row">
            <div class="col-sm-4"><i class="fa fa-calendar"></i> {} </div>
            <div class="col-sm-4"><i class="fa fa-calendar"></i> {} </div>
          </div>
          <div class="row">
            <div class="col-sm-4"> {} </div>
            <div class="col-sm-4"> {} </div>
            <div class="col-sm-4"> {} </div>
          </div>'''.format(self.start_date.label, self.end_date.label,
                           self.start_date(class_="form-control", required=True),
                           self.end_date(class_="form-control", required=True),
                           self.submit(class_="btn btn-primary btn-block"))


def get_daterange_form(num_days=20):
    """
    Returns a SelectDateRangeForm with two dates:
    - end_date is today
    - start_date is the today - numdays
    :param num_days: the date for the start_date
    :return: A SelectDateRangeForm object with the required logic
    """
    form = SelectDateRangeForm(request.form)
    if form.validate():
        if form.start_date.data > form.end_date.data:
            form.start_date.data, form.end_date.data = form.end_date.data, form.start_date.data
    else:
        form.end_date.data = to_local_datetime(datetime.datetime.utcnow()).date()
        form.start_date.data = form.end_date.data - datetime.timedelta(days=num_days)
    return form
