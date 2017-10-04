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

from hawkular import HawkularAlertsClient, Trigger
import os
import base64
from influxdb import InfluxDBClient



class MockMiqUtils(object):
    def __init__(self):
        super(MockMiqUtils, self).__init__()
        self.alertsClient = HawkularAlertsClient(**{'port':  os.environ['HAWKULAR_PORT'], 'host':  os.environ['HAWKULAR_HOST'], 'username': os.environ['HAWKULAR_USERNAME'], 'password':  os.environ['HAWKULAR_PASSWORD'], 'tenant_id': os.environ['HAWKULAR_TENANT']})
        self.headers = { 'Authorization': "Basic %s" % base64.b64encode(os.environ['HAWKULAR_USERNAME'] + ":" + os.environ['HAWKULAR_PASSWORD']), "Content-Type":
            "application/json", 'hawkular-tenant': "%s" % os.environ['HAWKULAR_TENANT']}

        self.influxClient = InfluxDBClient(
        **{'host': os.environ['INFLUX_HOST'], 'username': os.environ['INFLUX_USERNAME'],
           'port': os.environ['INFLUX_PORT'], 'database': os.environ['INFLUX_DATABASE'],
           'password': os.environ['INFLUX_PASSWORD']})

        self.minWait = int(os.environ['MILLISECONDS_REQUEST'])
        self.maxWait = int(os.environ['MILLISECONDS_REQUEST'])

    def miq_url(self, additionalParams):
        return self.alertsClient._service_url(['events']) + "?tags=miq.event_type|*" + additionalParams


    def alerts_version(self):
       return float('.'.join(str(x) for x in self.alertsClient.query_semantic_version()))

    def create_database(self):
        return self.influxClient.query( "CREATE DATABASE " + os.environ[ 'INFLUX_DATABASE'])

    def number_triggers(self):
        # TODO This a quick fix until https://github.com/hawkular/hawkular-client-python/pull/50 is not merged on
        # Hawkular Python Client
        url = self.alertsClient._service_url('triggers')
        triggers_dict = self.alertsClient._get(url)

        # Exclude the Group Trigger from counting (-1) and return 0, if there is only the group trigger
        return max(len(Trigger.list_to_object_list(triggers_dict)) -1, 0)
