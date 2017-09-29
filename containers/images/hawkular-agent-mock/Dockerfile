FROM python:2.7

# Copy the application's requirements.txt and run pip to install all
ADD requirements.txt  requirements.txt
RUN pip install -r requirements.txt

COPY assets ./assets
COPY environment.py .
COPY hawkular-agent-mock.py .

CMD locust -f hawkular-agent-mock.py --host ${HAWKULAR_HOST} -c 1  --print-stats --no-web
