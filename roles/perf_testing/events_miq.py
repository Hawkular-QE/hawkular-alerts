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
from hawkular.alerts import Trigger, TriggerMode, HawkularAlertsClient, ConditionType, Operator, Condition, GroupConditionsInfo, FullTrigger, GroupMemberInfo
from hawkular.client import HawkularMetricsConnectionError
from locust import HttpLocust, TaskSet, task
from datetime import datetime, timedelta
from locust.exception import StopLocust
import json
import pdb
import csv
import base64
import os

class ProfileMiqEvents(TaskSet):

    def service_url(self,object):
        return self.base._service_url(object)

    def headers(self, username, password, tenant):

       b64Val=  base64.b64encode(username + ":" + password)
       headers = {
            'Authorization' : "Basic %s" % b64Val,
            'content-type': "application/json"
        }

       headers['hawkular-tenant'] = tenant
       return headers

    @task(1)
    def create_load(self):
        port = os.environ['HAWKULAR_PORT']
        host = os.environ['HAWKULAR_HOST']
        username = os.environ['HAWKULAR_USERNAME']
        password = os.environ['HAWKULAR_PASSWORD']
        tenant = os.environ['HAWKULAR_TENANT']



        startTimeEnabled = json.loads(os.environ['START_TIME'])
        thin = json.loads(os.environ['THIN'])

        additionalParams = ""

        if startTimeEnabled:
            startTime = int((datetime.now() - timedelta(minutes=1)).strftime("%s")) * 1000
            additionalParams = "&startTime=" + str(startTime)

        if thin:
            thin = "&thin=true"
            additionalParams = additionalParams + thin


        self.base = HawkularAlertsClient(tenant_id=tenant, host=host, port=port,
        username=username, password=password)

        tags = "miq.event_type|*"
        url = self.service_url('events') + "?tags=" + tags + additionalParams

        with self.client.get(url= url, headers=self.headers(username, password, tenant),
        catch_response=True) as response:
              if (response.status_code != 200):
                 print(response.content)
                 raise StopLocust()

class ManageIQUser(HttpLocust):
    task_set =  ProfileMiqEvents
