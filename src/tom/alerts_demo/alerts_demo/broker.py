from tom_alerts.alerts import GenericQueryForm, GenericAlert, GenericBroker
from tom_alerts.models import BrokerQuery
from tom_targets.models import Target
from django import forms
import requests
import json
from hop import stream, io
from hop.subscribe import print_message
from hop import models


class AlertsDemoBrokerForm(GenericQueryForm):
    target_name = forms.CharField(required=True)


class AlertsDemoBroker(GenericBroker):
    name = 'Alerts Integration Demo'
    form = AlertsDemoBrokerForm

    def fetch_alerts(self, parameters):
        hop_kafka_url = 'kafka://kafka.scimma.org/circuses-demo.dev_tom'
        start_at = io.StartPosition.EARLIEST
        stream = io.Stream(auth=True, start_at=start_at, until_eos=True)
        alerts = []
        with stream.open(hop_kafka_url, "r") as s:
            for message in s:
                print('\n\n')
                print_message(message, json_dump=False)
                try:
                    ## Copying pattern from hop.subscribe.print_message()
                    if isinstance(message, models.MessageModel):
                        alert = json.loads(message.asdict())
                    else:
                        alert = json.loads(message)
                    if 'type' in alert and alert['type'] == 'alerts-integration-demo':
                        alerts.append(alert)
                    else:
                        print('Skipping invalid alert type.')
                        continue
                except:
                    print('ERROR: Failed to parse message.')
        return iter([alert for alert in alerts if alert['name'] == parameters['target_name']])

    def to_generic_alert(self, alert):
        return GenericAlert(
            timestamp=alert['timestamp'],
            url='#',
            id=alert['id'],
            name=alert['name'],
            ra=alert['ra'],
            dec=alert['dec'],
            mag=alert['mag'],
            score=alert['score']
        )
