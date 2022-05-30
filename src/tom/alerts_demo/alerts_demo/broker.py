from tom_alerts.alerts import GenericQueryForm, GenericAlert, GenericBroker
from tom_alerts.models import BrokerQuery
from tom_targets.models import Target
from django import forms
import requests

broker_url = 'https://gist.githubusercontent.com/mgdaily/f5dfb4047aaeb393bf1996f0823e1064/raw/5e6a6142ff77e7eb783892f1d1d01b13489032cc/example_broker_data.json'


class AlertsDemoBrokerForm(GenericQueryForm):
    target_name = forms.CharField(required=True)


class AlertsDemoBroker(GenericBroker):
    name = 'Alerts Integration Demo'
    form = AlertsDemoBrokerForm

    def fetch_alerts(self, parameters):
        response = requests.get(broker_url)
        response.raise_for_status()
        test_alerts = response.json()
        return iter([alert for alert in test_alerts if alert['name'] == parameters['target_name']])

    def to_generic_alert(self, alert):
        return GenericAlert(
            timestamp=alert['timestamp'],
            url=broker_url,
            id=alert['id'],
            name=alert['name'],
            ra=alert['ra'],
            dec=alert['dec'],
            mag=alert['mag'],
            score=alert['score']
        )
