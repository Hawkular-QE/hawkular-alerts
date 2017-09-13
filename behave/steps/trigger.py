from behave import *
import os
import random
from hawkular.alerts import Trigger, TriggerMode, HawkularAlertsClient, ConditionType, Operator, Condition, GroupConditionsInfo, FullTrigger, GroupMemberInfo, Severity
from hawkular.client import HawkularMetricsConnectionError, HawkularMetricsError



@given('hawkular alerts is installed and working')
def step_impl(context):
    port = os.environ['HAWKULAR_PORT']
    host = os.environ['HAWKULAR_HOST']
    username = os.environ['HAWKULAR_USERNAME']
    password = os.environ['HAWKULAR_PASSWORD']
    tenant = os.environ['HAWKULAR_TENANT']

    client = HawkularAlertsClient(tenant_id=tenant, host=host, port=port,
    username=username, password=password)
    context.client = client
    status = client.query_status()
    assert status['status'] == 'STARTED'

@when('create a valid trigger')
def step_impl(context):
    trigger =  Trigger()
    global triggerId
    triggerId = str(random.getrandbits(128))
    trigger.id = triggerId
    trigger.enabled = True
    trigger.autodisable = True
    trigger.tags = { "miq.event_type": "hawkular_alert", "miq.resource_type": "MiddlewareServer"}
    trigger.name = 'Valid Trigger Name'
    context.response= context.client.create_trigger(trigger)


@then('trigger will be created')
def step_impl(context):
    assert context.response is not None



@when('create a trigger with a existing ID')
def step_impl(context):
    context.execute_steps(u'''
        when create a valid trigger
    ''')
    trigger =  Trigger()
    trigger.id = context.response.id
    trigger.name = context.response.name
    try:
     context.client.create_trigger(trigger)
    except HawkularMetricsError as h:
       context.response = h

@then("trigger won't be created")
def step_impl(context):
    assert isinstance(context.response.code, int)
    assert context.response.code == 400


@when("update a existing trigger with threshold condition")
def step_impl(context):
    context.execute_steps(u'''
        when create a valid trigger
    ''')
    trigger =  Trigger()
    trigger.id = context.response.id

    condition1 = Condition()
    condition1.type = ConditionType.THRESHOLD
    condition1.data_id = 'gauge1'
    condition1.threshold = 50
    condition1.operator = Operator.GTE
    data = context.client._serialize_object([condition1])
    # TODO Create Method that update conditions on Hawkular Python Client
    response = context.client._put(context.client._service_url(['triggers',  trigger.id, 'conditions', TriggerMode.FIRING]), data=data)
    context.response = response

@then('trigger will have a threshold condition')
def step_impl(context):
   print(context.response)
   assert context.response.code is not None
