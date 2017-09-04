from hawkular.metrics import HawkularMetricsClient, MetricType, create_datapoint, create_metric
import numpy as np
import datetime
import pdb
import os

port = os.environ['HAWKULAR_PORT']
host = os.environ['HAWKULAR_HOST']
username = os.environ['HAWKULAR_USERNAME']
password = os.environ['HAWKULAR_PASSWORD']
seconds = int(os.environ['HAWKULAR_MINUTES']) * 60
servers = int(os.environ['HAWKULAR_SERVERS'])

client = HawkularMetricsClient(tenant_id='hawkular-test', host= host,
port=port, username=username, password=password)

for i in range(servers):

    # Create the Metrics Definitions for Each Server
    client.create_metric_definition(MetricType.Gauge, 'mw_heap_used_server-' + str(i))
    client.create_metric_definition(MetricType.Gauge, 'mw_heap_max_server-' + str(i))



for  
 datapoint_used = create_datapoint(dictionary_used[timestamp], timestamp)
 datapoint_max = create_datapoint(float(70.45), timestamp)

 print("Sending Data for Metric: " 'mw_heap_used_server-' + str(i) + " Data: " + str(datapoint_used))

 client.put(create_metric(MetricType.Gauge, 'mw_heap_used_server-' + str(i), [datapoint_used]))


 print("Sending Max Server: " 'mw_heap_max_server-' + str(i) + " Data: " + str(datapoint_max))

 client.put(create_metric(MetricType.Gauge,  'mw_heap_max_server-' + str(i), [datapoint_max]))
