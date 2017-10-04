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

import base64
import os
import random

from hawkular import HawkularAlertsClient, HawkularMetricsClient, Condition, TriggerMode, ConditionType, Operator,\
    GroupConditionsInfo, Trigger, Severity, GroupMemberInfo
from hawkular.client import HawkularMetricsError


class Environment (object):
    def __init__(self):
        super(Environment, self).__init__()
        self.alertsClient = HawkularAlertsClient(
            **{'port': os.environ['HAWKULAR_PORT'], 'host': os.environ['HAWKULAR_HOST'], 'username':
                os.environ['HAWKULAR_USERNAME'], 'password': os.environ['HAWKULAR_PASSWORD'], 'tenant_id':
                os.environ['HAWKULAR_TENANT']})

        self.headers = {'Authorization': "Basic %s" % base64.b64encode(os.environ[ 'HAWKULAR_USERNAME'] + ":" +
                                                                       os.environ[ 'HAWKULAR_PASSWORD']),
                        "Content-Type": "application/json", 'hawkular-tenant': "%s" % os.environ[ 'HAWKULAR_TENANT']}

        # Metrics to be compared
        self.metricUsed = 'mw_heap_used'
        self.metricMax = 'mw_heap_max'

        # Controlling the Speed https://github.com/locustio/locust/issues/472#issuecomment-244863432
        self.minWait = int(os.environ['MILLISECONDS_REQUEST'])
        self.maxWait = int(os.environ['MILLISECONDS_REQUEST'])

        self.server_name = "server-" + str( random.getrandbits(128))
        print("Creating Group Member for {0}".format(self.server_name))
        group_member = self.initialize_sample_group_member( self.metricMax, self.metricUsed, self.server_name)
        self.alertsClient.create_group_member(group_member)

    @staticmethod
    def url_metrics(metric_name):
        metricsClient = HawkularMetricsClient(
            **{'port': os.environ[ 'HAWKULAR_PORT'], 'host': os.environ[ 'HAWKULAR_HOST'],
               'username': os.environ['HAWKULAR_USERNAME'], 'password': os.environ[ 'HAWKULAR_PASSWORD'],
               'tenant_id': os.environ['HAWKULAR_TENANT']})
        return metricsClient._service_url( ([ 'gauges', metric_name, 'raw']))

    @staticmethod
    def initialize_sample_group_condition(metric, metric2):
        condition1 = Condition()
        condition1.trigger_mode = TriggerMode.FIRING
        condition1.type = ConditionType.COMPARE
        condition1.data_id = metric
        condition1.data2_id = metric2
        condition1.operator = Operator.GT
        condition1.data2_multiplier = 0.2

        condition2 = Condition()
        condition2.trigger_mode = TriggerMode.FIRING
        condition2.type = ConditionType.COMPARE
        condition2.data_id = metric
        condition2.data2_id = metric2
        condition2.operator = Operator.LT
        condition2.data2_multiplier = 0.1

        gc = GroupConditionsInfo()
        gc.addCondition(condition1)
        gc.addCondition(condition2)

        return gc

    @staticmethod
    def initialize_sample_group_trigger(miq_alert_name, trigger_id):
        trigger = Trigger()
        trigger.id = trigger_id
        trigger.description = miq_alert_name
        trigger.name = miq_alert_name
        trigger.firing_match = 'ANY'
        trigger.event_type = 'EVENT'
        trigger.severity = Severity.MEDIUM
        trigger.tags = {"miq.event_type": "hawkular_alert", "miq.resource_type": "MiddlewareServer"}
        trigger.enabled = True
        return trigger

    def initialize_sample_group_member(self, metric1, metric2, server_name):
        # Generate Member Trigger ID with MD5 from Trigger Id
        member = GroupMemberInfo()
        group_trigger = self.check_group_trigger()
        member.group_id = group_trigger.id
        member.member_id = str( random.getrandbits( 128))
        member.member_name = group_trigger.name + " for " + server_name

        if self.is_alerts20():
            data_map = {metric1: metric1 + "_" + server_name, metric2: + metric2 + "_" + server_name}
        else:
            data_map = {metric1: "hm_g_" + metric1 + "_" + server_name, metric2: "hm_g_" + metric2 + "_" + server_name}

        member.data_id_map = data_map
        return member

    @property
    def url_alerts20(self):
        return self.alertsClient._service_url([ 'data'])

    def is_alerts20(self):
        return self.alertsClient.query_semantic_version() >= (2, 0)

    def check_group_trigger(self):
        trigger_id = os.environ[ 'TRIGGER_ID']

        try:
            group_trigger = self.alertsClient.get_trigger(trigger_id)
            print ("Group Trigger exists")
            return group_trigger
        except HawkularMetricsError:
            print ("Group Trigger does not exists. Creating a new one")

            # Sample MIQ-Alert Name
            miq_alert_name = 'MIQ - EAP Memory Metrics~Heap Rate'

            # Generate Group Trigger
            group_trigger = self.initialize_sample_group_trigger(miq_alert_name, trigger_id)

            self.group_trigger = self.alertsClient.create_group_trigger(group_trigger)

            # Saving Group Trigger
            print("Created Group Trigger for {0}".format(miq_alert_name))

            # Generate Group Conditions
            group_conditions = self.initialize_sample_group_condition( self.metricUsed, self.metricMax)

            self.alertsClient.create_group_conditions(trigger_id, TriggerMode.FIRING, group_conditions)

        return group_trigger
