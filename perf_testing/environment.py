
import os
from hawkular.alerts import HawkularAlertsClient
from hawkular.metrics import HawkularMetricsClient

class Environment(object):
    def __init__(self):
        super(Environment, self).__init__()
        self.hawkular_port = os.environ['HAWKULAR_PORT']
        self.hawkular_host = os.environ['HAWKULAR_HOST']
        self.hawkular_username = os.environ['HAWKULAR_USERNAME']
        self.hawkular_password = os.environ['HAWKULAR_PASSWORD']
        self.hawkular_tenant_id = os.environ['HAWKULAR_TENANT']


        self.mock_port = os.environ['MOCK_PORT']
        self.mock_host = os.environ['MOCK_HOST']
        self.mock_tenant_id = os.environ['MOCK_TENANT']
        self.mock_username= os.environ['MOCK_USERNAME']
        self.mock_password = os.environ['MOCK_PASSWORD']

        self.mimic_metric_used = "MI~R~[" + os.environ['POD_NAME'] +"/Local DMR~~]~MT~WildFly Memory Metrics~Heap Used"
        self.mimic_metric_max = "MI~R~[" + os.environ['POD_NAME'] +"/Local DMR~~]~MT~WildFly Memory Metrics~Heap Max"

        self.num_servers = 100


    def hawkular_parameters(self):

        return {'port':  self.hawkular_port, 'host':  self.hawkular_host,  'username': self.hawkular_username, 'password':  self.hawkular_password, 'tenant_id': self.hawkular_tenant_id}

    def mock_parameters(self):
        return {'port':  self.mock_port, 'host':  self.mock_host,  'username': self.mock_username, 'password':  self.mock_password, 'tenant_id': self.mock_tenant_id}


    def create_hawkular_metrics_connection(self, parameters):
        return HawkularMetricsClient(**parameters)

    def create_hawkular_alerts_connection(self, parameters):
        return HawkularAlertsClient(**parameters)
