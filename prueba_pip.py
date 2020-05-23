#!/usr/bin/python3
from pip._vendor import requests
import logging

# Configuration for logging #
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] (%(threadName)s) %(message)s')

if __name__ == '__main__':
    requests.urllib3.disable_warnings()
    requests.urllib3.util.ssl_.DEFAULT_CIPHERS += 'HIGH:!DH:!aNULL'
    try:
        requests.packages.urllib3.contrib.pyopenssl.DEFAULT_SSL_CIPHER_LIST += 'HIGH:!DH:!aNULL'
    except AttributeError:
        # no pyopenssl support used / needed / available
        pass
    header = {'Content-Type': 'text/xml', 'charset': 'UTF-8'}
    payload = '''<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:ws="http://ws.gwpagos/">
    <soapenv:Header/>
    <soapenv:Body>
        <ws:consultaCuentaHome>
            <req>
                <cuenta>bancard</cuenta>
                <pass>B4nc4rdT1g041</pass>
                <user>bancard</user>
            </req>
        </ws:consultaCuentaHome>
    </soapenv:Body>
  </soapenv:Envelope>'''
    url = 'https://10.16.202.52:8443/GwPagos/GwPagosWs'
    response = requests.post(url, verify=False, headers=header, data=payload)
    logging.info('Requesting to -> ' + 'tigo')
    print(response.status_code)
    print(response.content)
