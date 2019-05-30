FROM python:3.7.3-stretch
ADD /flask_monitoringdashboard /fmd/flask_monitoringdashboard
ADD requirements.txt /fmd/flask_monitoringdashboard
WORKDIR /fmd/flask_monitoringdashboard
RUN pip install -r requirements.txt
CMD ["flask", "run", "-h", "0.0.0.0"]
