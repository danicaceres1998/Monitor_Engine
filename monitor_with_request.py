#!/usr/bin/python3
import os
import yaml
import urllib2
import datetime
import subprocess
import pickle
import time
import logging
from threading import Thread
from pip._vendor import requests

# Configuration for logging #
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] (%(threadName)s) %(message)s')

# Constants #
DATA_FILE = 'data/data.pickle'
MAX_TIME_OUTS = 3

## CLASSES ##
class MyThread(Thread):
    ''' My new type of Thread '''
    # Static Constants #
    MAX_TIME = 10
    WAIT_TIME = 5
    QUANT_REQUEST = 3

    def __init__(self, name_thread, name_b_agent, url):
        Thread.__init__(self, name=name_thread, target=MyThread.run)
        self.name_thread = name_thread
        self.name_b_agent = name_b_agent
        self.url_request = url
        self.counter_time_outs = 0
        self.time_begin = None
        self.time_finish = None
        self.list_status_codes = list()

    def run(self):
        ''' Function that calls the test '''
        self.test_request()

    def test_request(self):
        ''' Function that requests 3 times to te Billing Agent '''
        # Configuration of the function POST #
        session = requests.Session()
        session.trust_env = False
        session.verify = False
        session.timeout = self.MAX_TIME
        # Requesting to the server (3 times) #
        self.time_begin = datetime.datetime.now()
        for _ in range(self.QUANT_REQUEST):
            logging.info('Requesting to -> ' + self.name_b_agent)
            initial_time = datetime.datetime.now()
            # Doing the request #
            response = session.post(self.url_request)
            self.list_status_codes.append(response.status_code)
            if response.status_code < 200 or response.status_code > 202:
                if (datetime.datetime.now().second - initial_time.second) < self.MAX_TIME:
                    time.sleep(self.WAIT_TIME)
                self.counter_time_outs += 1
                print('ERROR: ' + str(response.status_code) + ' -> ' + self.name_b_agent)
            else:
                print('SUCCESS: ' + str(response.status_code) + ' -> ' + self.name_b_agent)
                time.sleep(self.WAIT_TIME)
        self.time_finish = datetime.datetime.now()  

class Counter:
    ''' Abstaction for the counter of the Billing Agent '''
    def __init__(self, name_b_agent):
        self.name_b_agent = name_b_agent
        self.counter_both_nodes = 0
        self.counter_local_node = 0
        self.counter_remote_node = 0

    def reset_all_counters(self):
        ''' Function that reset all the counters '''
        self.counter_both_nodes = 0
        self.counter_local_node = 0
        self.counter_remote_node = 0

class BillingAgent:
    ''' Abstraction of the Object Billing Agent '''
    # Functions #
    def __init__(self, name_b_agent, server, port, enable_services, disable_services, local_telnet, remote_telnet, stats_folder, url):
        self.name_b_agent = name_b_agent
        self.server = server
        self.port = port
        self.enable_services = enable_services
        self.disable_services = disable_services
        self.local_telnet = local_telnet
        self.remote_telnet = remote_telnet
        self.stats_folder = stats_folder
        self.url_request = url

    def telnet_local(self):
        ''' Function that telnet the server from local'''
        archive = 'python ' + self.local_telnet
        try:
            stream = os.popen(archive)
        except Exception as e:
            error = 'FATAL ERROR: ' + str(e)
            print(error)
            os.popen("echo '" + error + "' >> logs/history_nc.log").read()
            exit()
        else:
            local_telnet_output = stream.read()
            return local_telnet_output

    def telnet_remote(self):
        ''' Function that telnet the server from remote '''
        archive = 'python ' + self.remote_telnet
        try:
            stream = os.popen(archive)
        except Exception as e:
            error = 'FATAL ERROR: ' + str(e)
            print(error)
            os.popen("echo '" + error + "' >> logs/history_nc.log").read()
            exit()
        else:
            remote_telnet_output = stream.read()
            return remote_telnet_output

    def enable_services_function(self):
        with open(self.enable_services) as f:
            docs = yaml.load_all(f, Loader=yaml.FullLoader)
            for doc in docs:
                for key, value in doc.items():
                    self.name_b_agent = key
                    curl = value["curl"]
                    description = value["description"]
                    print("====================================")
                    print("enabling facturador: " + self.name_b_agent + "...")
                    print("curl: " + curl)
                    print("description: " + description)
                    stream = os.popen(curl)
                    output = stream.read()
                    print(output)

    def disable_services_function(self):
        with open(self.disable_services) as f:
            docs = yaml.load_all(f, Loader=yaml.FullLoader)
            for doc in docs:
                for key, value in doc.items():
                    self.name_b_agent = key
                    curl = value["curl"]
                    description = value["description"]
                    print("====================================")
                    print("disabling facturador: " + self.name_b_agent + "...")
                    print("curl: " + curl)
                    print("description: " + description)
                    print("missing invocation to curl....................")
                    stream = os.popen(curl)
                    output = stream.read()
                    print(output)

    def get_times_out_both_nodes(self):
        ''' Function that get the quantity of time outs of both nodes '''
        # Getting the list of objects
        list_counters = pickle.load(open(DATA_FILE, 'rb'))
        for counter in list_counters:
            if self.name_b_agent == counter.name_b_agent:
                # Returning the counter of de specific b_agent in both nodes
                return counter.counter_both_nodes

    def set_time_out_both_nodes(self):
        ''' Function that increase in 1 the quantity of time outs on the both nodes'''
        # Getting the list of objects
        list_counters = pickle.load(open(DATA_FILE, 'rb'))
        for counter in list_counters:
            if self.name_b_agent == counter.name_b_agent:
                # Adding 1 to the counter
                counter.counter_both_nodes += 1
                break
        # Saving the data
        pickle.dump(list_counters, open(DATA_FILE, 'wb'))

    def get_times_out_local_node(self):
        ''' Function that get the quantity of time outs of the local node '''
        # Getting the list of objects
        list_counters = pickle.load(open(DATA_FILE, 'rb'))
        for counter in list_counters:
            if self.name_b_agent == counter.name_b_agent:
                # Returning the counter of de specific b_agent in the local node
                return counter.counter_local_node

    def set_time_out_local_node(self):
        ''' Function that increase in 1 the quantity of time outs on the local node '''
        # Getting the list of objects
        list_counters = pickle.load(open(DATA_FILE, 'rb'))
        for counter in list_counters:
            if self.name_b_agent == counter.name_b_agent:
                # Adding 1 to the counter
                counter.counter_local_node += 1
                break
        # Saving the data
        pickle.dump(list_counters, open(DATA_FILE, 'wb'))

    def get_times_out_remote_node(self):
        ''' Function that get the quantity of time outs of the remote node '''
        # Getting the list of objects
        list_counters = pickle.load(open(DATA_FILE, 'rb'))
        for counter in list_counters:
            if self.name_b_agent == counter.name_b_agent:
                # Returning the counter of de specific b_agent in the remote node
                return counter.counter_remote_node

    def set_time_out_remote_node(self):
        ''' Function that increase in 1 the quantity of time outs on the remote node '''
        # Getting the list of objects
        list_counters = pickle.load(open(DATA_FILE, 'rb'))
        for counter in list_counters:
            if self.name_b_agent == counter.name_b_agent:
                # Adding 1 to the counter
                counter.counter_remote_node += 1
                break
        # Saving the data
        pickle.dump(list_counters, open(DATA_FILE, 'wb'))

    def restart_time_outs_all_nodes(self):
        # We get the object
        list_counters = pickle.load(open(DATA_FILE, 'rb'))
        # Restarting the all the counters
        for counter in list_counters:
            if self.name_b_agent == counter.name_b_agent:
                counter.reset_all_counters()
                break
        # Saving the data
        pickle.dump(list_counters, open(DATA_FILE, 'wb'))

class Monitor:
    ''' Abstraction of the object Monitor '''
    # Static Atributes #
    cell_phones = {'Aki': '0983524814', 'Jose': '0985775785', 'Dani': '0971160145',\
                    'Nahuel': '0991636345', 'Nati': '0972164527'}
    # Constants #
    CANT_BITS = 5242880
    MAX_TIME_OUTS = 3
    INIT_HOUR = 8
    FINISH_HOUR = 20

    def __init__(self):
        ''' For the instance of the Object '''
        ### Here we put all the agents ###
        self.list_billing_agents = list()
        ### Here we put all the agents to request ###
        self.list_agents_to_request = list()

        ###################################################################################
        ## Put the name, server, port, the directory/name of the .yaml archives, telnets ##
        ## and the url for the request test                                              ##
        ###################################################################################
        # ANDE #
        self.list_billing_agents.append(BillingAgent('ANDE', 'prod1.ande.gov.py', '8580',\
            'conf/ande/enable_services.yaml', 'conf/ande/disable_services.yaml',\
            'bin/ande/telnet_local_server.py', 'bin/ande/telnet_remote_server.py',\
            'stats/ande/', 'http://prod1.ande.gov.py:8580/sigaWs/api/open/v3/suministro/bancoDatos'))

        # TIGO #
        self.list_billing_agents.append(BillingAgent('Tigo', 'apipagos.telecel.net.py', '443',\
            'conf/tigo/enable_services.yaml', 'conf/tigo/disable_services.yaml',\
            'bin/tigo/telnet_local_server.py', 'bin/tigo/telnet_remote_server.py',\
            'stats/tigo/', 'http://apipagos.telecel.net.py:443/wsdl/tigo-prod.wsdl'))

        # COPACO #
        self.list_billing_agents.append(BillingAgent('Copaco', '10.1.11.101', '8080',\
            'conf/copaco/enable_services.yaml', 'conf/copaco/disable_services.yaml',\
            'bin/copaco/telnet_local_server.py', 'bin/copaco/telnet_remote_server.py',\
            'stats/copaco/', 'http://10.1.11.101:8080/wsdl/copaco/copaco_production.wsdl'))

        # VOX PAGO FACTURA #
        self.list_billing_agents.append(BillingAgent('VOX', '10.0.241.1', '8081',\
            'conf/vox_pago_factura/enable_services.yaml', 'conf/vox_pago_factura/disable_services.yaml',\
            'bin/vox_pago_factura/telnet_local_server.py', 'bin/vox_pago_factura/telnet_remote_server.py',\
            'stats/vox_pago_factura/', 'http://10.0.241.1:8081/wsdl/vox.wsdl'))
            
    def send_sms_notifications(self, sms_message):
        # send sms alerting that services are down
        cellphone_keys = self.cell_phones.keys()
        for key in cellphone_keys:
            self.send_sms(self.cell_phones[key], sms_message, key)

    def send_sms(self, cellphone_number, sms_message, name):
        print('Alerting to ' + cellphone_number + ' -> ' + name + ' ...')
        url = 'http://10.30.12.38:9081/courier/api/secure/messages'
        data = '{"channelDestination": "SMS","recipient": "' + cellphone_number + '","message": "' + sms_message + '"}'
        req = urllib2.Request(url, data)
        req.add_header('Cache-Control', 'no-cache')
        req.add_header('Content-Type', 'application/json')
        req.add_header('X-JOKO-AUTH', 'eyJhbGciOiJIUzUxMiJ9.eyJzdWIiOiJNb25pdG9yZW8iLCJleHAiOjE2MDc1MjQ3NjUsImlhdCI6MTU3NTk4ODc2NSwianRpIjoiNUZERjRYN0xGRk9aWllDV1EyTEEiLCJqb2tvIjp7InR5cGUiOiJBQ0NFU1MiLCJyb2xlcyI6WyJCQUNLT0ZGSUNFIl0sInByb2ZpbGUiOiJERUZBVUxUIn19.ycGxxnia6M_quGbyemEGjppp3NeGuwD-Yhg9InXzE-EDcn2xdpx8uGPxtVy5Sl-PZ_0BAA3umwyf0_J0Ol02zw')
        req.get_method = lambda: "POST"
        proxy_handler = urllib2.ProxyHandler({})
        opener = urllib2.build_opener(proxy_handler)
        urllib2.install_opener(opener)
        http_request = urllib2.urlopen(req)
        http_request.close()

    def process_billing_agents(self):
        ''' Function that for ich agent we control '''
        # Testing the netcat to the biller agent
        for b_a in self.list_billing_agents:
            self.process_net_cat(b_a)
        # Testing the request to the biller agent
        self.process_request()

    def process_net_cat(self, b_agent):
        # change directory to script directory - cron ready
        absolute_path = os.path.abspath(__file__)
        directory_name = os.path.dirname(absolute_path)
        os.chdir(directory_name)

        now = datetime.datetime.now()
        print('=============================================================')
        print('Billing Agent: ' + b_agent.name_b_agent)
        print("start: " + now.strftime("%Y-%m-%d %H:%M:%S"))
        os.popen("echo '=============================================================' >> logs/history_nc.log").read()
        os.popen("echo ''Billing Agent: '" + b_agent.name_b_agent + "' >> logs/history_nc.log").read()
        os.popen("echo 'start " + now.strftime("%Y-%m-%d %H:%M:%S")  + "' >> logs/history_nc.log").read()

        current_directory = os.getcwd()
        print("current directory: " + current_directory)
        os.popen("echo 'current directory: " + current_directory + "' >> logs/history_nc.log").read()

        if os.path.getsize("logs/history_nc.log") > self.CANT_BITS: # 5MB.
            os.remove("logs/history_nc.log")
            os.popen("echo 'history file removed...' >> logs/history_nc.log").read()

        local_telnet_output = b_agent.telnet_local()
        remote_telnet_output = b_agent.telnet_remote()

        print("telnet from local dispatcher to " + b_agent.name_b_agent + ": " + local_telnet_output)
        os.popen("echo 'telnet from local dispatcher to " + b_agent.name_b_agent + ": " + local_telnet_output + "' >> logs/history_nc.log").read()
        print("telnet from remote dispatcher to " + b_agent.name_b_agent + ": " + remote_telnet_output)
        os.popen("echo 'telnet from remote dispatcher to " + b_agent.name_b_agent + ": " + remote_telnet_output + "' >> logs/history_nc.log").read()

        if local_telnet_output != "succeeded!" and remote_telnet_output != "succeeded!":
            # Setting the counter
            b_agent.set_time_out_both_nodes()
            # disabling services
            print("ERROR, having problems to connect with " + b_agent.name_b_agent)
            os.popen("echo 'problem, both nodes are having problem connecting with " + b_agent.name_b_agent + "' >> logs/history_nc.log").read()
            # Getting the counter of time outs of both nodes
            if b_agent.get_times_out_both_nodes() <= self.MAX_TIME_OUTS:
                print(b_agent.name_b_agent + ' only have ' + str(b_agent.get_times_out_both_nodes()) + ' times out on both nodes, the service will not be disabled')
                os.popen("echo '" + b_agent.name_b_agent + " only have " + str(b_agent.get_times_out_both_nodes()) + " times out on both nodes, the service will not be disabled' >> logs/history_nc.log").read()
                now = datetime.datetime.now()
                print("end: " + now.strftime("%Y-%m-%d %H:%M:%S"))
                os.popen("echo 'end " + now.strftime("%Y-%m-%d %H:%M:%S")  + "' >> logs/history_nc.log").read()
                return None
            if not os.path.exists(b_agent.stats_folder + 'service_disabled'):
                # disabling services
                stream = os.popen('touch ' + b_agent.stats_folder + 'service_disabled')
                stream.read()
                print("disabling services and turning sms alerts off...")
                os.popen("echo 'disabling services and turning sms alerts off...' >> logs/history_nc.log").read()
                b_agent.disable_services_function()
            # Asking for the hour
            current_hour = int(time.strftime('%H'))
            if current_hour >= self.INIT_HOUR and current_hour <= self.FINISH_HOUR:
                if not os.path.exists(b_agent.stats_folder + 'smsoff'):
                    # Writing the Message
                    sms_message = "Problema con " + b_agent.name_b_agent + " ambos nodos (138 y 151) no conectan al facturador (mas de 3 intentos fallidos),\
                    se apagan las alertas y se deshabilitan los servicios con mensajes personalizados (control corre cada 5 minutos)."
                    stream = os.popen('touch ' + b_agent.stats_folder + 'smsoff')
                    stream.read()
                    # send sms alerting that services are down
                    self.send_sms_notifications(sms_message)
        elif local_telnet_output != "succeeded!":
            # Setting the counter
            b_agent.set_time_out_local_node()
            print("problem with local connection to " + b_agent.name_b_agent)
            os.popen("echo 'problem with local connection to " + b_agent.name_b_agent + "' >> logs/history_nc.log").read()
            # Getting te counter of time outs of the local node
            if b_agent.get_times_out_local_node() <= self.MAX_TIME_OUTS:
                print(b_agent.name_b_agent + ' only have ' + str(b_agent.get_times_out_local_node()) + ' times out on the local node, the monitor will not send an alert')
                os.popen("echo '" + b_agent.name_b_agent + " only have " + str(b_agent.get_times_out_local_node()) + " times out on the local node, the monitor will not send an alert' >> logs/history_nc.log").read()
                now = datetime.datetime.now()
                print("end: " + now.strftime("%Y-%m-%d %H:%M:%S"))
                os.popen("echo 'end " + now.strftime("%Y-%m-%d %H:%M:%S")  + "' >> logs/history_nc.log").read()
                return None
            # Asking for the hour
            current_hour = int(time.strftime('%H'))
            if current_hour >= self.INIT_HOUR and current_hour <= self.FINISH_HOUR:
                # Verifying the alert
                if not os.path.exists(b_agent.stats_folder + 'smsoff_node_1'):
                    if not os.path.exists(b_agent.stats_folder + 'service_disabled'):
                        # Writing the Message
                        sms_message = "Problema con " + b_agent.name_b_agent + ", nodo 138 no conecta al facturador (mas de 3 intentos fallidos, control corre cada 5 minutos)."
                        stream = os.popen('touch ' + b_agent.stats_folder + 'smsoff_node_1')
                        stream.read()
                        # send sms alerting that the service is down in that node
                        self.send_sms_notifications(sms_message)
        elif remote_telnet_output != "succeeded!":
            # Setting the counter
            b_agent.set_time_out_remote_node()
            print("problem with remote server connection to " + b_agent.name_b_agent)
            os.popen("echo 'problem with remote server connection to " + b_agent.name_b_agent + "' >> logs/history_nc.log").read()
            # Getting te counter of time outs of the remote node
            if b_agent.get_times_out_remote_node() <= self.MAX_TIME_OUTS:
                print(b_agent.name_b_agent + ' only have ' + str(b_agent.get_times_out_remote_node()) + ' times out on the remote node, the monitor will not send an alert')
                os.popen("echo '" + b_agent.name_b_agent + " only have " + str(b_agent.get_times_out_remote_node()) + " times out on the remote node, the monitor will not send an alert' >> logs/history_nc.log").read()
                now = datetime.datetime.now()
                print("end: " + now.strftime("%Y-%m-%d %H:%M:%S"))
                os.popen("echo 'end " + now.strftime("%Y-%m-%d %H:%M:%S")  + "' >> logs/history_nc.log").read()
                return None
            # Asking for the hour
            current_hour = time.strftime('%H')
            if current_hour >= self.INIT_HOUR and current_hour <= self.FINISH_HOUR:
                # Verifying the alert
                if not os.path.exists(b_agent.stats_folder + "smsoff_node_2"):
                    if not os.path.exists(b_agent.stats_folder + 'service_disabled'):
                        sms_message = "Problema con " + b_agent.name_b_agent + ", nodo 151 no conecta al facturador (mas de 3 intentos fallidos, control corre cada 5 minutos)."
                        stream = os.popen('touch ' + b_agent.stats_folder + 'smsoff_node_2')
                        stream.read()
                        # send sms alerting that the service is down in that node
                        self.send_sms_notifications(sms_message)
        else:
            # Saving the billing agent for the request
            self.list_agents_to_request.append(b_agent)
            # Asking for the counter
            if b_agent.get_times_out_both_nodes() != 0:
                print('Restarting counter of the Billing Agent to -> 0')
                os.popen("echo 'Restarting counter of the Billing Agent to -> 0' >> logs/history_nc.log").read()
            # Restarting the counter of time outs
            b_agent.restart_time_outs_all_nodes()
            # enabling services
            print(b_agent.name_b_agent + " is online!")
            os.popen("echo '" + b_agent.name_b_agent + " is online!' >> logs/history_nc.log").read()
            # Asking for the hour
            current_hour = time.strftime('%H')
            if current_hour >= self.INIT_HOUR and current_hour <= self.FINISH_HOUR:
                if os.path.exists(b_agent.stats_folder + 'service_disabled'):
                    sms_message = "Facturador " + b_agent.name_b_agent + " en linea en ambos nodos (138 y 151), se habilitan los servicios, se eliminan los  mensajes personalizados."
                    print("enabling services...")
                    os.popen("echo 'enabling services...' >> logs/history_nc.log").read()
                    b_agent.enable_services_function()
                    os.remove(b_agent.stats_folder + 'service_disabled')
                    if (os.path.exists(b_agent.stats_folder + 'smsoff')):
                        os.remove(b_agent.stats_folder + 'smsoff')
                    if (os.path.exists(b_agent.stats_folder + 'smsoff_node_1')):
                        os.remove(b_agent.stats_folder + 'smsoff_node_1')
                    if (os.path.exists(b_agent.stats_folder + 'smsoff_node_2')):
                        os.remove(b_agent.stats_folder + 'smsoff_node_2')
                    # send sms informing that services are online again
                    self.send_sms_notifications(sms_message)
                else:
                    # Deleting the smsoff nodes
                    if os.path.exists(b_agent.stats_folder + 'smsoff_node_1'):
                        sms_message = "Facturador: " + b_agent.name_b_agent + ", recupero la conexion en el nodo 138."
                        message_log = b_agent.name_b_agent + ", recupero la conexion en el nodo 138 -> " + now.strftime("%Y-%m-%d %H:%M:%S")
                        print(message_log)
                        os.popen("echo '" + message_log +"' >> logs/history_nc.log").read()
                        os.remove(b_agent.stats_folder + 'smsoff_node_1')
                        self.send_sms_notifications(sms_message)
                    if os.path.exists(b_agent.stats_folder + 'smsoff_node_2'):
                        sms_message = "Facturador: " + b_agent.name_b_agent + ", recupero la conexion en el nodo 151."
                        message_log = b_agent.name_b_agent + ", recupero la conexion en el nodo 138 -> " + now.strftime("%Y-%m-%d %H:%M:%S")
                        print(message_log)
                        os.popen("echo '" + message_log +"' >> logs/history_nc.log").read()
                        os.remove(b_agent.stats_folder + 'smsoff_node_2')
                        self.send_sms_notifications(sms_message)

        now = datetime.datetime.now()
        print("end: " + now.strftime("%Y-%m-%d %H:%M:%S"))
        os.popen("echo 'end " + now.strftime("%Y-%m-%d %H:%M:%S")  + "' >> logs/history_nc.log").read()

    def process_request(self):
        list_threads = list()
        # Creating the threads
        for i in range(len(self.list_agents_to_request)):
            list_threads.append(MyThread('thread' + str(i+1),\
                self.list_agents_to_request[i].name_b_agent, self.list_agents_to_request[i].url_request))
        # Starting all the process
        for thd in list_threads:
            thd.start()
        # Joining al the process
        for thd in list_threads:
            thd.join()
        # Showing and saving the data
        for thd in list_threads:
            # Showing the biller agent data #
            print('=============================================================')
            print("Billing Agent: " + thd.name_b_agent + " starting requests")
            print("start: " + thd.time_begin.strftime("%Y-%m-%d %H:%M:%S"))
            print('have used the thread -> ' + thd.name_thread)
            os.popen("echo '=============================================================' >> logs/history_request.log").read()
            os.popen("echo 'Billing Agent: " + thd.name_b_agent + " starting requests' >> logs/history_request.log").read()
            os.popen("echo 'start: " + thd.time_begin.strftime("%Y-%m-%d %H:%M:%S")  + "' >> logs/history_request.log").read()
            os.popen("echo 'have used the thread -> " + thd.name_thread + "' >> logs/history_request.log").read()
            # Showing the results of the requests #
            print("Quantity of Success: " + str(thd.QUANT_REQUEST - thd.counter_time_outs))
            print("Quantity of Errors: " + str(thd.counter_time_outs))
            print("List of Status Codes: " + str(thd.list_status_codes))
            os.popen("echo 'Quantity of Success: " + str(thd.QUANT_REQUEST - thd.counter_time_outs) + "' >> logs/history_request.log").read()
            os.popen("echo 'Quantity of Errors: " + str(thd.counter_time_outs) + "' >> logs/history_request.log").read()
            os.popen("echo 'List of Status Codes: " + str(thd.list_status_codes) + "' >> logs/history_request.log").read()

### MAIN ###
if __name__ == "__main__":
    monitor = Monitor()
    monitor.process_billing_agents()
