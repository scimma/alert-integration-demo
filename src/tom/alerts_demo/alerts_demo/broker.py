from tom_alerts.alerts import GenericQueryForm, GenericAlert, GenericBroker
from tom_alerts.models import BrokerQuery
from tom_targets.models import Target
from django import forms
import os
import json
from hop import stream, io
from hop.subscribe import print_message
from hop import models
from datetime import datetime


class AlertsDemoBrokerForm(GenericQueryForm):
    kn_score = forms.FloatField(required=True)
    time_published = forms.CharField(required=True)


class AlertsDemoBroker(GenericBroker):
    name = 'Alerts Integration Demo'
    form = AlertsDemoBrokerForm

    def fetch_alerts(self, parameters):
        hop_kafka_url = os.getenv('HOP_URL_ALERTS')
        start_at = io.StartPosition.EARLIEST
        stream = io.Stream(auth=True, start_at=start_at, until_eos=True)
        alerts = []
        with stream.open(hop_kafka_url, "r") as hop_stream:
            for message, metadata in hop_stream.read(metadata=True):
                ## Parse headers
                try:
                    headers = {}
                    for header in metadata.headers:
                        headers[header[0]] = header[1].decode('utf-8')
                    print(json.dumps(headers))
                except Exception as e:
                    print(f'''Error parsing headers: "{e}". metadata.headers: {metadata.headers}''')
                ## Construct alert object
                alert = {
                    'headers': headers,
                    'message': message,
                }
                try:
                    ## Insert alert data into the database
                    if 'sender' in headers and 'schema' in headers \
                        and headers['sender'] == 'alert-integration-demo' \
                        and headers['schema'] == 'scimma.alert-integration-demo/broker/v1':
                        print_message(message, json_dump=False)
                        alerts.append(alert)
                    else:
                        print('Invalid alert message. Skipping...')
                        continue
                except Exception as e:
                    print(f'''Error parsing alert: {e}. Alert: {json.dumps(alert['message'])}''')
                print(alert['headers']['time'])
                print(parameters['time_published'])
                alert_time = datetime.strptime(alert['headers']['time'], "%Y-%m-%d %H:%M:%S.%f")
                time_published = datetime.strptime(parameters['time_published'], "%Y-%m-%d %H:%M:%S.%f")
                print(alert_time)
                print(time_published)
        return iter([alert for alert in alerts if \
            float(alert['message']['kn_score']) >= float(parameters['kn_score']) and \
                alert['headers']['time'] >= parameters['time_published']])

    def to_generic_alert(self, alert):
        print(alert)
        return GenericAlert(
            timestamp=alert['message']['time_obs'],
            id=alert['headers']['id'],
            name=alert['message']['candidate'],
            ra=alert['message']['ra'],
            dec=alert['message']['dec'],
            mag=alert['headers']['id'],
            score=alert['message']['kn_score'],
            url='#',
        )
