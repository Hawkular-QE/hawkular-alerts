FROM python:2.7

# Copy the application's requirements.txt and run pip to install all
ADD requirements.txt  requirements.txt
RUN pip install -r requirements.txt

COPY manageiq_mock.py .
COPY utils.py .

CMD locust -f manageiq_mock.py --host ${HAWKULAR_HOST} -c 1  --print-stats --no-web
