def change_group_trigger(self, object):
    trigger = Trigger(object)
    trigger.name = 'WildFly Memory Metrics~Heap Used Modified'
    trigger.tags = {'miq.event_type': 'hawkular-alert', 'miq.resource_type': 'miq_alert', 'miq.event_text': 'trigger-modified'}
    trigger.enabled = False


    return trigger

@task(1)
def update_group_trigger(self):
    self.base = HawkularAlertsClient(tenant_id='dummy', host=self.parent.host)
    try:
        self.random_value = random.choice(values)
        self.trigger_id = "MIQ-" + self.random_value
        with  self.client.get(url=self.service_url(['triggers', self.trigger_id]) ,
        headers=self.headers(),  catch_response=True) as response:
              if response.status_code == 200:
                  group_trigger = self.change_group_trigger(json.loads(response.content))


        with self.client.put(url=self.service_url(['triggers', 'groups', group_trigger.id]),
        headers=self.headers(), data=self.serialize_object(group_trigger), catch_response=True) as response:
              if response.status_code == 200:
                  print()
    except IndexError:
        print("Values is empty for now")

@task(1)
def delete_group_trigger(self):
    self.base = HawkularAlertsClient(tenant_id='dummy', host=self.parent.host)
    self.random_value = random.choice(values)

    # Ensuring there is no colision
    self.random_value = random.choice(values)
    self.trigger_id = "MIQ-" + self.random_value


    with self.client.delete(url=self.service_url(['triggers', 'groups',  self.trigger_id]),
    headers=self.headers(), catch_response=True) as response:
          if response.status_code == 400:
             print(response.status_code)
          if response.status_code == 200:
             print(response.status_code)

    values.remove(self.random_value)
