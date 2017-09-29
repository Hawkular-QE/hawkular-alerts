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

import locust.events
import locust.stats
from utils import MockMiqUtils
from locust import HttpLocust, TaskSet, task
from locust.exception import StopLocust


class ProfileMiqEvents (TaskSet):
    @task(1)
    def check_events(self):
        utils = MockMiqUtils()
        startTime = int((datetime.now() - timedelta( minutes=1)).strftime( "%s")) * 1000
        additionalParams = "&startTime=" + str( startTime) + "&thin=true"

        global response_json

        with self.client.get(url=utils.miq_url( additionalParams), headers=utils.headers, catch_response=True) \
                as response:
            if response.status_code == 200:
                response_json = json.loads( response.content)
            else:
                raise StopLocust()


class ManageIQUser (HttpLocust):
    global client , utils, identifier
    utils = MockMiqUtils()
    client = utils.influxClient
    utils.create_database()

    task_set = ProfileMiqEvents
    min_wait = utils.minWait
    max_wait = utils.maxWait
    identifier = random.getrandbits(128)

    def __init__(self):
        super( ManageIQUser, self).__init__()
        locust.events.request_success += self.hook_request_success
        locust.events.request_failure += self.hook_request_fail

    def hook_request_success(self, request_type, name, response_time, response_length):
        metrics = {}
        tags = {'execution': identifier}
        metrics[ 'measurement'] = "request"
        fields = {'alerts_version': utils.alerts_version(),'triggers': len(utils.alertsClient.list_triggers()) -1,
                  'request_type': request_type,
                  'response_time': response_time, 'response_length': response_length,
                  'events_count': len( response_json), 'name': name}
        metrics[ 'fields'] = fields
        metrics[ 'tags'] = tags
        client.write_points( [ metrics])

    def hook_request_fail(self, request_type, name, response_time, exception):
        metrics = {}
        tags = {'execution': id}
        metrics['measurement'] = "fail"
        fields = {'response_time': response_time, 'exception': exception, 'name': name}
        metrics['fields'] = fields
        metrics['tags'] = tags
        client.write_points([ metrics])
