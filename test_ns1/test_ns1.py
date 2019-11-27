import time
import pytest
import requests
import paho.mqtt.client as mqtt

from tangotest.vim import vim_from_env


@pytest.fixture(scope='module')
def ns1():
    with vim_from_env() as vim:
        vim.add_instances_from_package('eu.5gtango.tng-smpilot-ns1-emulator.0.1.tgo')
        time.sleep(200)
        yield vim


def test_mqtt_connectivity(ns1):
    client = mqtt.Client()
    mqtt_ip = ns1.instances['smpilot-cc'].get_ip('mqtt')
    mqtt_port = 1883
    exec_code = client.connect(mqtt_ip, mqtt_port, 60)
    assert exec_code == 0


def test_data_store(ns1):
    machine = 'WIMMS0'
    topic = '{}/EM63/TestMetricA'.format(machine)
    metric = 'em63_testmetrica'
    value = '123123123'

    mqtt_ip = ns1.instances['smpilot-cc'].get_ip('mqtt')
    mqtt_port = 1883
    client = mqtt.Client()
    client.connect(mqtt_ip, mqtt_port)

    client.data_topic, client.data_payload = None, None

    def receive_message(client, userdata, message):
        client.last_topic, client.last_payload = message.topic, message.payload

    client.on_message = receive_message
    client.subscribe(topic)
    client.loop_start()
    client.publish(topic, value)
    time.sleep(5)
    client.loop_stop()

    assert client.last_topic == topic
    assert client.last_payload == value

    data_store_ip = ns1.instances['smpilot-cc'].get_ip('prometheus')
    data_store_port = '9090'
    url = 'http://{}:{}/api/v1/query'.format(data_store_ip, data_store_port)
    params = {'query': metric}
    response = requests.get(url, params)
    assert response.ok

    response = response.json()
    assert response['status'] == 'success'
    assert response['data']['result'][0]['metric']['machine'] == machine
    assert response['data']['result'][0]['metric']['__name__'] == metric
    assert response['data']['result'][0]['value'][1] == str(value)


def test_edge_analytics_connectivity(ns1):
    ea_ip = ns1.instances['smpilot-eae'].get_ip('grafana')
    ea_port = '13011'
    url = 'http://{}:{}'.format(ea_ip, ea_port)
    response = requests.get(url, allow_redirects=False)
    assert response.ok
    assert 'found' in response.text.lower()


@pytest.mark.skip(reason="not implemented")
def test_enterprise_cloud(ns1):
    pass
