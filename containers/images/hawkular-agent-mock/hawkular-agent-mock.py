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

import json
import random
from datetime import datetime, timedelta
from hawkular.metrics import create_datapoint
from locust import HttpLocust, TaskSet, task

from environment import Environment

class GenerateMetricsBehavior(TaskSet):
        @staticmethod
        def mimic_from_eap_server():
            with open('assets/used.json', 'r') as f:
                used_dict = json.load(f)

            with open('assets/max.json', 'r') as f:
                max_dict = json.load(f)

            return {'used':  random.choice(used_dict), 'max': random.choice(max_dict)}

        @task(1)
        def send_data(self):
            # Mimic from a EAP Server Running on Openshift
            values = self.mimic_from_eap_server()

            metric_used = environment.metricUsed + "_{0}".format(environment.server_name)
            metric_max = environment.metricMax + "_{0}".format(environment.server_name)

            time = datetime.now()

            max_value = create_datapoint( float( values['max']['value']), time)
            used_value = create_datapoint( float( values['used']['value']), int((time + timedelta(seconds=1)).strftime( "%s")) * 1000)

            if environment.is_alerts20():
                # For 2.0 method
                url = environment.url_alerts20()

                used_value['id'] = metric_used
                max_value['id'] = metric_max
                max_value.pop('tags')
                used_value.pop('tags')

                self.client.post(url=url, headers=environment.headers, data=json.dumps([max_value]))
                self.client.post(url=url, headers=environment.headers, data=json.dumps([used_value]))

            else:
                self.client.post(url=environment.url_metrics(metric_max), headers=environment.headers, data=json.dumps([max_value]))
                self.client.post(url=environment.url_metrics(metric_used), headers=environment.headers, data=json.dumps([used_value]))

class HawkularAgent(HttpLocust):
    global environment
    environment = Environment()
    min_wait = environment.minWait
    max_wait = environment.maxWait
    task_set = GenerateMetricsBehavior
