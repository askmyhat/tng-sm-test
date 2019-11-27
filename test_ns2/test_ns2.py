import time
import datetime
import pytest
import paho.mqtt.client as mqtt
import smbclient

from tangotest.vim import vim_from_env


@pytest.fixture(scope='module')
def ns2():
    with vim_from_env() as vim:
        vim.add_instances_from_package('eu.5gtango.tng-smpilot-ns2-emulator.0.1.tgo')
        time.sleep(20)
        yield vim


def test_samba(ns2):
    samba_ip = ns1.instances['smpilot-cc'].get_ip('samba139')
    share = 'guest'
    user = 'guest'
    password = 'guest'
    smb = smbclient.SambaClient(server=samba_ip, share=share, username=user, password=password)
    assert smb.info('/')


@pytest.mark.skip(reason='Only one service is supported by VnV. Cannot use broker.')
def test_mdc(ns2):
    samba_ip = ns1.instances['smpilot-cc'].get_ip('samba139')
    share = 'guest'
    user = 'guest'
    password = 'guest'
    smb = smbclient.SambaClient(server=samba_ip, share=share, username=user, password=password)
    
    request_filename = 'SESS0001.REQ'
    with smb.open(request_filename) as f:
        request = f.read()
    
    job_number = request.split()[-1][1:-2].split('.')[0]

    current_datetime = str(datetime.datetime.now())
    current_date = current_datetime.split()[0].replace('-', '')
    current_time = current_datetime.split()[1].split('.')[0]
    
    response = 'DATE,TIME,@ActSimPara1,@ActSimPara2,ActCntCyc,ActCntPrt,ActStsMach,ActTimCyc,SetCntMld,SetCntPrt\n'
    response += '{},{},5,1.8287,1000,10000,1C000,5.0000,10,10000'.format(current_date, current_time)
    
    dat_filename = '{}.DAT'.format(job_number)
    with smb.open(dat_filename, mode='w') as f:
        f.write(response)
