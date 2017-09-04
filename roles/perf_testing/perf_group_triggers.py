"""
Copyright 2015-2017 Red Hat, Inc. and/or its affiliates
and other contributors as indicated by the @author tags.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License
"""
from hawkular.alerts import Trigger, TriggerMode, HawkularAlertsClient, ConditionType, Operator, Condition, GroupConditionsInfo, FullTrigger, GroupMemberInfo, Severity
from hawkular.client import HawkularMetricsConnectionError
from locust import HttpLocust, TaskSet, task
import json
import hashlib
import random
import os

global triggers_values
triggers_values= []

class ManageIQBehavior(TaskSet):

    def service_url(self,object):
        return self.base._service_url(object)

    def serialize_object(self,object):
        return self.base._serialize_object(object)

    def headers(self):
        headers = {
            'authorization': "Basic amRvZTpwYXNzd29yZA==",
            'content-type': "application/json"
        }

        headers['hawkular-tenant'] = "hawkular"

        return headers


    def initialize_sample_group_member(self, group_trigger, dataId, dataId2, server_name):

        # Generate Member Trigger ID with MD5 from Trigger Id
        m = hashlib.md5()
        m.update(group_trigger.id)

        member = GroupMemberInfo()
        member.group_id = group_trigger.id
        member.member_id = "my-member-trigger-for-" + server_name
        member.member_name = group_trigger.name + " for " + server_name
        data_map = {}
        data_map[dataId] =  "hm_g_" + dataId + "_" + server_name
        data_map[dataId2] = "hm_g_" + dataId2 + "_" + server_name

        member.data_id_map = data_map
        return member

    def initialize_sample_group_condition(self, dataId, dataId2):
        condition1 = Condition()
        condition1.trigger_mode = TriggerMode.FIRING
        condition1.type = ConditionType.COMPARE
        condition1.data_id = dataId
        condition1.data2_id = dataId2
        condition1.operator = Operator.GT
        condition1.data2_multiplier=0.8



        condition2 = Condition()
        condition2.trigger_mode = TriggerMode.FIRING
        condition2.type = ConditionType.COMPARE
        condition2.data_id = dataId
        condition2.data2_id = dataId2
        condition2.operator = Operator.LT
        condition2.data2_multiplier = 0.2


        gc = GroupConditionsInfo()
        gc.addCondition(condition1)
        gc.addCondition(condition2)

        return gc


    def initialize_sample_group_trigger(self, metric_name):

        trigger =  Trigger()
        trigger.id = self.trigger_id
        trigger.description = 'Test-Alert1'
        trigger.name = metric_name
        trigger.firing_match = 'ANY'
        trigger.event_type = 'EVENT'
        trigger.severity = Severity.MEDIUM
        trigger.tags = { "miq.event_type": "hawkular_alert", "miq.resource_type": "MiddlewareServer"}
        trigger.enabled = True
        return trigger


    @task(1)
    def create_load(self):

        port = os.environ['HAWKULAR_PORT']
        host = os.environ['HAWKULAR_HOST']
        username = os.environ['HAWKULAR_USERNAME']
        password = os.environ['HAWKULAR_PASSWORD']
        servers = int(os.environ['HAWKULAR_SERVERS'])

        self.base = HawkularAlertsClient(tenant_id='dummy', host=host, port=port,
        username=username, password=password)

        self.trigger_id =  str(random.getrandbits(128))

        # Sample of Metric which use COMPARE
        dataId = 'mw_heap_used'

        dataId2 = 'mw_heap_max'

        # Sample Metric Name
        metric_name =  'WildFly Memory Metrics~Heap Used'

        triggers_values.append(self.trigger_id)

        # Generate Group Trigger
        group_trigger =self.initialize_sample_group_trigger(metric_name)

        print (self.trigger_id)

        # Generate Group Conditions
        group_conditions =  self.initialize_sample_group_condition(dataId, dataId2)

        # Send the Post Request (Group Trigger)
        with  self.client.post(url=self.service_url(['triggers', 'groups']) ,
        data=self.serialize_object(group_trigger), headers=self.headers(),  catch_response=True) as response:
              if response.status_code == 400:
                 print(response.content)

       # Send the Post Request (Group Conditions)
        with self.client.put(url=self.service_url(['triggers', 'groups', self.trigger_id, 'conditions', TriggerMode.FIRING]),
        data=self.serialize_object(group_conditions), headers=self.headers(),  catch_response=True) as response:
              if response.status_code == 400:
                 print(response.content)

         # Generate Group Members
        for i in range(servers):
             server_name = "server-" + str(i)
             group_member = self.initialize_sample_group_member(group_trigger, dataId, dataId2, server_name)
             with self.client.post(url=self.service_url(['triggers', 'groups', 'members']),
             data=self.serialize_object(group_member),
             headers=self.headers(), catch_response=True) as response:
                if response.status_code == 400:
                    print(response.content)


class HawkularUser(HttpLocust):
    task_set =  ManageIQBehavior
