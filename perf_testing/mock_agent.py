"""
Copyright 2015-2017 Red Hat, Inc. and/or its affiliates
and other contributors as indicated by the @author tags.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

author Guilherme Baufaker Rego

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License
"""

from hawkular.client import HawkularMetricsConnectionError
from hawkular.metrics import HawkularMetricsClient, MetricType, create_datapoint, create_metric
from locust import HttpLocust, TaskSet, task
from environment import Environment
import random
import time



class GenerateMetricsBehavior(TaskSet):
        global environment
        environment = Environment()
        global servers
        servers = range(environment.num_servers)


        def mimic_from_server(self,client,environment):
            used_dict =client .query_metric(MetricType.Gauge, environment.mimic_metric_used, **{'limit': 1, 'order': 'desc'})
            max_dict = client .query_metric(MetricType.Gauge, environment.mimic_metric_max, **{'limit': 1, 'order': 'desc'})
            return {'used':  used_dict[0]['value'], 'max': max_dict[0]['value']}

        @task(1)
        def send_data(self):

            client = environment.create_hawkular_metrics_connection(environment.hawkular_parameters())
            client_mock = environment.create_hawkular_metrics_connection(environment.mock_parameters())

            # Mimic from a Server Running on Openshift
            values = self.mimic_from_server(client,environment)

            i = servers[0]
            servers.pop(0)

            metric_used ='mw_heap_used_server-' + str(i)
            metric_max = 'mw_heap_max_server-' + str(i)

            print ("Inserting Value for {0}".format(metric_used))
            client_mock.push(MetricType.Gauge, metric_used, values['used'])

            print ("Inserting Value for {0}".format(metric_max))
            client_mock.push(MetricType.Gauge, metric_max,  values['max'])

            servers.append(i)

            # For 2.0 method

class HawkularAgent(HttpLocust):
    task_set =  GenerateMetricsBehavior
