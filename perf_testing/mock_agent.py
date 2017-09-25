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


        def mimic_from_eap_server(self,client,environment):
            used_dict =client .query_metric(MetricType.Gauge, environment.mimic_metric_used, **{'limit': 1, 'order': 'desc'})
            max_dict = client .query_metric(MetricType.Gauge, environment.mimic_metric_max, **{'limit': 1, 'order': 'desc'})
            return {'used':  used_dict[0]['value'], 'max': max_dict[0]['value']}

        def send_data_alert(metric_used, metric_max, environment, values):

            url = environment.url_alerts20()
            time = datetime.now()
            max_value = create_datapoint(float(values['max']), time)
            usded_value = create_datapoint(float(values['used']), time)


            with self.client.post(url=url, headers=self.environment_alerts20(),
            catch_response=True, data = max_value) as response:
                  if response.status_code == 200:
                      response_json = json.loads(response.content)
                  else:
                     raise StopLocust()


              with self.client.post(url=url, headers=self.environment_alerts20(),
              catch_response=True, data = used_value) as response:
                    if response.status_code == 200:
                        response_json = json.loads(response.content)
                    else:
                       raise StopLocust()



        def send_data_services(client_mock, metric_used, metric_max, values):

             print ("Inserting Value for {0}".format(metric_used))
             client_mock.push(MetricType.Gauge, metric_used, values['used'])

             print ("Inserting Value for {0}".format(metric_max))
             client_mock.push(MetricType.Gauge, metric_max,  values['max'])


        @task(1)
        def send_data(self):

            client = environment.create_hawkular_metrics_connection(environment.hawkular_parameters())
            client_mock = environment.create_hawkular_metrics_connection(environment.mock_parameters())

            # Mimic from a EAP Server Running on Openshift
            values = self.mimic_from_eap_server(client,environment)

            i = servers[0]
            servers.pop(0)

            metric_used ='mw_heap_used_server-' + str(i)
            metric_max = 'mw_heap_max_server-' + str(i)

            if environment.is_alerts20():
                  send_data_services(client_mock, metric_used, metric_max, values)
            else:
               # For 2.0 method
                send_data_alert(client,metric_used, metric_max, environment, values)

            servers.append(i)

class HawkularAgent(HttpLocust):
    task_set =  GenerateMetricsBehavior
