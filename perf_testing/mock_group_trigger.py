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
from hawkular.alerts import Trigger, TriggerMode, HawkularAlertsClient, ConditionType, Operator, Condition, GroupConditionsInfo, FullTrigger, GroupMemberInfo, Severity
import pdb
import hashlib
import random
from environment import Environment
import numpy
from benchpy import benchmarked

def initialize_sample_group_member(group_trigger, dataId, dataId2, server_name):

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

def initialize_sample_group_condition(dataId, dataId2):
    condition1 = Condition()
    condition1.trigger_mode = TriggerMode.FIRING
    condition1.type = ConditionType.COMPARE
    condition1.data_id = dataId
    condition1.data2_id = dataId2
    condition1.operator = Operator.GT
    condition1.data2_multiplier=0.2


    condition2 = Condition()
    condition2.trigger_mode = TriggerMode.FIRING
    condition2.type = ConditionType.COMPARE
    condition2.data_id = dataId
    condition2.data2_id = dataId2
    condition2.operator = Operator.LT
    condition2.data2_multiplier = 0.1


    gc = GroupConditionsInfo()
    gc.addCondition(condition1)
    gc.addCondition(condition2)

    return gc


def initialize_sample_group_trigger(miq_alert_name, trigger_id):

    trigger =  Trigger()
    trigger.id = trigger_id
    trigger.description = miq_alert_name
    trigger.name = metric_name
    trigger.firing_match = 'ANY'
    trigger.event_type = 'EVENT'
    trigger.severity = Severity.MEDIUM
    trigger.tags = { "miq.event_type": "hawkular_alert", "miq.resource_type": "MiddlewareServer"}
    trigger.enabled = True
    return trigger

@benchmarked()
def create_group_member(group_trigger, dataId, dataId2, environment):
    for i in range(environment.num_servers):
       server_name = "server-" + str(i)
       group_member = initialize_sample_group_member(group_trigger, dataId, dataId2, server_name)
       client.create_group_member(group_member)

environment = Environment()
client = environment.create_hawkular_alerts_connection(environment.mock_parameters())


trigger_id =  str(random.getrandbits(128))

# Sample of Metric which
dataId = 'mw_heap_used'

dataId2 = 'mw_heap_max'

# Sample MIQ-Alert Name
miq_alert_name =  'EAP Memory Metrics~Heap Rate'


# Generate Group Trigger
group_trigger = initialize_sample_group_trigger(miq_alert_name, trigger_id)

# Saving Group Trigger
client.create_group_trigger(group_trigger)

# Generate Group Conditions
group_conditions =  initialize_sample_group_condition(dataId, dataId2)

client.create_group_conditions(trigger_id, TriggerMode.FIRING, group_conditions)

# Generate Group Members
create_group_member(group_trigger, dataId, dataId2, environment)

print(benchmarked.results('create_group_member'))
print(benchmarked.statistics('create_group_member'))
