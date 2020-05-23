#!/usr/bin/python3
import os
import yaml
import urllib2
import datetime
import subprocess
import pickle
import time
import smtplib
from string import Template
from email.mime.text import MIMEText

# Constant #
DATA_FILE = 'data/data.pickle'

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
    def __init__(self, name_b_agent, server, port, enable_services, disable_services, local_telnet, remote_telnet, stats_folder):
        self.name_b_agent = name_b_agent
        self.server = server
        self.port = port
        self.enable_services = enable_services
        self.disable_services = disable_services
        self.local_telnet = local_telnet
        self.remote_telnet = remote_telnet
        self.stats_folder = stats_folder

    def telnet_local(self):
        ''' Function that telnet the server from local'''
        archive = 'python ' + self.local_telnet
        try:
            stream = os.popen(archive)
        except Exception as e:
            error = 'FATAL ERROR: ' + str(e)
            print(error)
            os.popen("echo '" + error + "' >> history.log").read()
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
            os.popen("echo '" + error + "' >> history.log").read()
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

class SmsSender:
    ''' Abstraction of an SMS Sender '''
    # Static Constant #
    CELL_PHONES = {'Aki': '0983524814', 'Jose': '0985775785', 'Dani': '0971160145',\
                    'Nahuel': '0991636345', 'Nati': '0972164527'}

    def send_sms_notifications(self, sms_message):
        # send sms alerting that services are down
        cellphone_keys = self.CELL_PHONES.keys()
        for key in cellphone_keys:
            self.send_sms(self.CELL_PHONES[key], sms_message, key)

    def send_sms(self, cellphone_number, sms_message, name):
        print('SMS Alert: Alerting to ' + name + ' -> ' + cellphone_number + ' ...')
        os.popen("echo 'SMS Alert: Alerting to " + name + " -> " + cellphone_number + " ...' >> history.log")
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

class EmailSender:
    ''' Abstraction of an Email Sender '''
    ### Static Constants ###
    # From Addres #
    MY_ADDRESS = 'jose.cantero@bancard.com.py'
    # Contacts File #
    CONTACTS_FILE = 'data/my_contacts.txt'
    # Alerts Messages #
    ALERT_MSG_BOTH_NODES = 'data/alert_msg.txt'
    ALERT_MSG_NODE_ONE = 'data/alert_msg_node_1.txt'
    ALERT_MSG_NODE_TWO = 'data/alert_msg_node_2.txt'
    # Notice Messages #
    NOTICE_MSG_BOTH_NODES = 'data/notice_msg.txt'
    NOTICE_MSG_NODE_ONE = 'data/notice_msg_node_1.txt'
    NOTICE_MSG_NODE_TWO = 'data/notice_msg_node_2.txt'
    # Nodes #
    BOTH_NODES = 0
    NODE_ONE = 1
    NODE_TWO = 2

    def get_contacts(self):
        """
        Return two lists names, emails containing names and email addresses
        read from a file specified by filename.
        """
        # Variables
        names = []
        emails = []
        # Getting emails and names
        with open(self.CONTACTS_FILE, mode='r') as contacts_file:
            for a_contact in contacts_file:
                names.append(a_contact.split()[0])
                emails.append(a_contact.split()[1])
        return names, emails

    def read_template(self, filename):
        """
        Returns a Template object comprising the contents of the
        file specified by filename.
        """
        # Getting the message
        with open(filename, 'r') as template_file:
            template_file_content = template_file.read()
        return Template(template_file_content)

    def send_email(self, type_message, type_node, name_b_agent):
        # Reading the contacts
        names, emails = self.get_contacts()
        # Reading the message
        if type_message is True: # type_message -> True: Alert | False: Notice
            if type_node == self.BOTH_NODES:
                message_template = self.read_template(self.ALERT_MSG_BOTH_NODES)
            elif type_node == self.NODE_ONE:
                message_template = self.read_template(self.ALERT_MSG_NODE_ONE)
            elif type_node == self.NODE_TWO:
                message_template = self.read_template(self.ALERT_MSG_NODE_TWO)
        else:
            if type_node == self.BOTH_NODES:
                message_template = self.read_template(self.NOTICE_MSG_BOTH_NODES)
            elif type_node == self.NODE_ONE:
                message_template = self.read_template(self.NOTICE_MSG_NODE_ONE)
            elif type_node == self.NODE_TWO:
                message_template = self.read_template(self.NOTICE_MSG_NODE_TWO)
        # set up the SMTP server
        server = smtplib.SMTP(host='192.100.1.12', port=25)
        # For each contact, send the email:
        for name, email in zip(names, emails):
            # Add in the actual person name to the message template
            message = message_template.substitute(PERSON_NAME=name.title(), TIME=time.strftime('%X').title(), B_AGENT=name_b_agent.title())
            # Prints out the message body for our sake
            print('EMAIL Alert: Alerting to ' + name + ' -> ' + email + ' ...')
            os.popen("echo 'EMAIL Alert: Alerting to " + name + " -> " + email + " ...' >> history.log")
            # Create the message
            msg = MIMEText(message)
            # setup the parameters of the message
            msg['From'] = self.MY_ADDRESS
            msg['To'] = email
            if type_message is True:
                msg['Subject'] = 'Alerta Monitoreo - Telnet Facturadores'
            else:
                msg['Subject'] = 'Aviso Monitoreo - Telnet Facturadores'
            # send the message via the server
            server.sendmail(msg['From'], [msg['To']], msg.as_string())
            del msg
        # Terminate the SMTP session and close the connection
        server.quit()

class Monitor:
    ''' Abstraction of the object Monitor '''
    # Constants #
    CANT_BITS = 3145728
    MAX_TIME_OUTS = 3
    GREAT_TIME_OUTS = 6
    INIT_HOUR = 8
    FINISH_HOUR = 20
    BOTH_NODES = 0
    NODE_ONE = 1
    NODE_TWO = 2

    def __init__(self):
        ''' For the instance of the Object '''
        ### Objects to send emails and sms messages ###
        self.email_sender = EmailSender()
        self.sms_sender = SmsSender()
        ### Here we put all the agents ###
        self.list_billing_agents = list()
        ######################################################################################
        ## Put the name, server, port, the directory/name of the .yaml archives and telnets ##
        ######################################################################################
        # ANDE #
        self.list_billing_agents.append(BillingAgent('ANDE', 'prod1.ande.gov.py', '8580',\
            'conf/ande/enable_services.yaml', 'conf/ande/disable_services.yaml',\
            'bin/ande/telnet_local_server.py', 'bin/ande/telnet_remote_server.py', 'stats/ande/'))

        # TIGO #
        self.list_billing_agents.append(BillingAgent('Tigo', 'apipagos.telecel.net.py', '443',\
            'conf/tigo/enable_services.yaml', 'conf/tigo/disable_services.yaml',\
            'bin/tigo/telnet_local_server.py', 'bin/tigo/telnet_remote_server.py', 'stats/tigo/'))

        # COPACO #
        self.list_billing_agents.append(BillingAgent('Copaco', '10.1.11.101', '8080',\
            'conf/copaco/enable_services.yaml', 'conf/copaco/disable_services.yaml',\
            'bin/copaco/telnet_local_server.py', 'bin/copaco/telnet_remote_server.py', 'stats/copaco/'))

        # VOX PAGO FACTURA #
        self.list_billing_agents.append(BillingAgent('VOX', '10.0.241.1', '8081',\
            'conf/vox_pago_factura/enable_services.yaml', 'conf/vox_pago_factura/disable_services.yaml',\
            'bin/vox_pago_factura/telnet_local_server.py', 'bin/vox_pago_factura/telnet_remote_server.py',\
            'stats/vox_pago_factura/'))

        # BRISTOL #
        self.list_billing_agents.append(BillingAgent('Bristol', '138.186.60.106', '9090',\
            'conf/bristol/enable_services.yaml', 'conf/bristol/disable_services.yaml',\
            'bin/bristol/telnet_local_server.py', 'bin/bristol/telnet_remote_server.py',\
            'stats/bristol/'))

    def process_billing_agents(self):
        ''' Function that control the netcat for each agent '''
        for b_a in self.list_billing_agents:
            self.main_function(b_a)

    def main_function(self, b_agent):
        # change directory to script directory - cron ready
        absolute_path = os.path.abspath(__file__)
        directory_name = os.path.dirname(absolute_path)
        os.chdir(directory_name)
        # Starging the process
        now = datetime.datetime.now()
        print('=============================================================')
        print('Billing Agent: ' + b_agent.name_b_agent)
        print("start: " + now.strftime("%Y-%m-%d %H:%M:%S"))
        os.popen("echo '=============================================================' >> history.log").read()
        os.popen("echo ''Billing Agent: '" + b_agent.name_b_agent + "' >> history.log").read()
        os.popen("echo 'start " + now.strftime("%Y-%m-%d %H:%M:%S")  + "' >> history.log").read()
        current_directory = os.getcwd()
        print("current directory: " + current_directory)
        os.popen("echo 'current directory: " + current_directory + "' >> history.log").read()
        # Getting the size of the .log
        if os.path.getsize("history.log") > self.CANT_BITS: # 3MB.
            os.remove("history.log")
            os.popen("echo 'history file removed...' >> history.log").read()
        # Starting the Netcat to the Billing Agent
        local_telnet_output = b_agent.telnet_local()
        remote_telnet_output = b_agent.telnet_remote()
        print("telnet from local dispatcher to " + b_agent.name_b_agent + ": " + local_telnet_output)
        os.popen("echo 'telnet from local dispatcher to " + b_agent.name_b_agent + ": " + local_telnet_output + "' >> history.log").read()
        print("telnet from remote dispatcher to " + b_agent.name_b_agent + ": " + remote_telnet_output)
        os.popen("echo 'telnet from remote dispatcher to " + b_agent.name_b_agent + ": " + remote_telnet_output + "' >> history.log").read()
        # Starting the analysis #
        if local_telnet_output != 'succeeded!' and remote_telnet_output != 'succeeded!':
            # Setting the counter
            b_agent.set_time_out_both_nodes()
            # disabling services
            print("ERROR, having problems to connect with " + b_agent.name_b_agent)
            os.popen("echo 'Problem -> both nodes are having problem connecting with " + b_agent.name_b_agent + "' >> history.log").read()
            # Getting the counter of time outs of both nodes
            if b_agent.get_times_out_both_nodes() <= self.MAX_TIME_OUTS:
                print(b_agent.name_b_agent + ' only have ' + str(b_agent.get_times_out_both_nodes()) + ' times out on both nodes, the service will not be disabled')
                os.popen("echo '" + b_agent.name_b_agent + " only have " + str(b_agent.get_times_out_both_nodes()) + " times out on both nodes, the service will not be disabled' >> history.log").read()
                now = datetime.datetime.now()
                print("end: " + now.strftime("%Y-%m-%d %H:%M:%S"))
                os.popen("echo 'end " + now.strftime("%Y-%m-%d %H:%M:%S")  + "' >> history.log").read()
                return None
            if not os.path.exists(b_agent.stats_folder + 'service_disabled'):
                # disabling services
                stream = os.popen('touch ' + b_agent.stats_folder + 'service_disabled')
                stream.read()
                print("disabling services and turning emails alerts off...")
                os.popen("echo 'disabling services and turning emails alerts off...' >> history.log").read()
                b_agent.disable_services_function()
            # Asking for the hour
            current_hour = int(time.strftime('%H'))
            if current_hour >= self.INIT_HOUR and current_hour <= self.FINISH_HOUR:
                # Getting the counter of time outs of both nodes
                if b_agent.get_times_out_both_nodes() > self.GREAT_TIME_OUTS:
                    if not os.path.exists(b_agent.stats_folder + 'smsoff'):
                        # Writing the Message
                        sms_message = "ALERTA " + time.strftime('%X') + " -> Problema con " + b_agent.name_b_agent + " ambos nodos (138 y 151) no conectan al facturador hace mas de 30 min."
                        stream = os.popen('touch ' + b_agent.stats_folder + 'smsoff')
                        stream.read()
                        # send sms alerting that services are down
                        self.sms_sender.send_sms_notifications(sms_message)
                else:
                    if not os.path.exists(b_agent.stats_folder + 'emailoff'):
                        stream = os.popen('touch ' + b_agent.stats_folder + 'emailoff')
                        stream.read()
                        # send email alerting that services are down
                        type_message = True # type_message -> True: Alert | False: Notice
                        self.email_sender.send_email(type_message, self.BOTH_NODES, b_agent.name_b_agent)
        elif local_telnet_output != 'succeeded!':
            # Setting the counter
            b_agent.set_time_out_local_node()
            print("problem with local connection to " + b_agent.name_b_agent)
            os.popen("echo 'problem with local connection to " + b_agent.name_b_agent + "' >> history.log").read()
            # Getting te counter of time outs of the local node
            if b_agent.get_times_out_local_node() <= self.MAX_TIME_OUTS:
                print(b_agent.name_b_agent + ' only have ' + str(b_agent.get_times_out_local_node()) + ' times out on the local node, the monitor will not send an alert')
                os.popen("echo '" + b_agent.name_b_agent + " only have " + str(b_agent.get_times_out_local_node()) + " times out on the local node, the monitor will not send an alert' >> history.log").read()
                now = datetime.datetime.now()
                print("end: " + now.strftime("%Y-%m-%d %H:%M:%S"))
                os.popen("echo 'end " + now.strftime("%Y-%m-%d %H:%M:%S")  + "' >> history.log").read()
                return None
            # Asking for the hour
            current_hour = int(time.strftime('%H'))
            if current_hour >= self.INIT_HOUR and current_hour <= self.FINISH_HOUR:
                # Verifying the alert
                if not os.path.exists(b_agent.stats_folder + 'emailoff_node_1'):
                    if not os.path.exists(b_agent.stats_folder + 'service_disabled'):
                        stream = os.popen('touch ' + b_agent.stats_folder + 'emailoff_node_1')
                        stream.read()
                        # send email alerting that services are down
                        type_message = True # type_message -> True: Alert | False: Notice
                        self.email_sender.send_email(type_message, self.NODE_ONE, b_agent.name_b_agent)
        elif remote_telnet_output != 'succeeded!':
            # Setting the counter
            b_agent.set_time_out_remote_node()
            print('problem with remote server connection to ' + b_agent.name_b_agent)
            os.popen("echo 'problem with remote server connection to " + b_agent.name_b_agent + "' >> history.log").read()
            # Getting te counter of time outs of the remote node
            if b_agent.get_times_out_remote_node() <= self.MAX_TIME_OUTS:
                print(b_agent.name_b_agent + ' only have ' + str(b_agent.get_times_out_remote_node()) + ' times out on the remote node, the monitor will not send an alert')
                os.popen("echo '" + b_agent.name_b_agent + " only have " + str(b_agent.get_times_out_remote_node()) + " times out on the remote node, the monitor will not send an alert' >> history.log").read()
                now = datetime.datetime.now()
                print("end: " + now.strftime("%Y-%m-%d %H:%M:%S"))
                os.popen("echo 'end " + now.strftime("%Y-%m-%d %H:%M:%S")  + "' >> history.log").read()
                return None
            # Asking for the hour
            current_hour = int(time.strftime('%H'))
            if current_hour >= self.INIT_HOUR and current_hour <= self.FINISH_HOUR:
                # Verifying the alert
                if not os.path.exists(b_agent.stats_folder + "emailoff_node_2"):
                    if not os.path.exists(b_agent.stats_folder + 'service_disabled'):
                        stream = os.popen('touch ' + b_agent.stats_folder + 'emailoff_node_2')
                        stream.read()
                        # send email alerting that services are down
                        type_message = True # type_message -> True: Alert | False: Notice
                        self.email_sender.send_email(type_message, self.NODE_TWO, b_agent.name_b_agent)
        else:
            # Asking for the counter
            if b_agent.get_times_out_both_nodes() != 0:
                print('Restarting counter of the Billing Agent to -> 0')
                os.popen("echo 'Restarting counter of the Billing Agent to -> 0' >> history.log").read()
            # Restarting the counter of time outs
            b_agent.restart_time_outs_all_nodes()
            # enabling services
            print(b_agent.name_b_agent + " is online!")
            os.popen("echo '" + b_agent.name_b_agent + " is online!' >> history.log").read()
            if os.path.exists(b_agent.stats_folder + 'service_disabled'):
                sms_message = "AVISO " + time.strftime('%X') + " -> Facturador " + b_agent.name_b_agent + " en linea en ambos nodos (138 y 151), se habilitan los servicios, se eliminan los  mensajes personalizados."
                print("enabling services...")
                os.popen("echo 'enabling services...' >> history.log").read()
                b_agent.enable_services_function()
                os.remove(b_agent.stats_folder + 'service_disabled')
                # Removing the smsoff
                if os.path.exists(b_agent.stats_folder + 'smsoff'):
                    os.remove(b_agent.stats_folder + 'smsoff')
                    # Asking for the hour
                    current_hour = int(time.strftime('%H'))
                    if current_hour >= self.INIT_HOUR and current_hour <= self.FINISH_HOUR:
                        # Sending sms alerting that services are online
                        self.sms_sender.send_sms_notifications(sms_message)
                # Removing the emailoff
                os.remove(b_agent.stats_folder + 'emailoff')
                if os.path.exists(b_agent.stats_folder + 'emailoff_node_1'):
                    os.remove(b_agent.stats_folder + 'emailoff_node_1')
                if os.path.exists(b_agent.stats_folder + 'emailoff_node_2'):
                    os.remove(b_agent.stats_folder + 'emailoff_node_2')
                # Asking for the hour
                current_hour = int(time.strftime('%H'))
                if current_hour >= self.INIT_HOUR and current_hour <= self.FINISH_HOUR:
                    # send email alerting that services are online
                    type_message = False # type_message -> True: Alert | False: Notice
                    self.email_sender.send_email(type_message, self.BOTH_NODES, b_agent.name_b_agent)
            else:
                # Deleting the emailoff nodes
                # Asking for the hour
                current_hour = int(time.strftime('%H'))
                if os.path.exists(b_agent.stats_folder + 'emailoff_node_1'):
                    sms_message = "AVISO " + time.strftime('%X') + " -> Facturador " + b_agent.name_b_agent + ", recupero la conexion en el nodo 138."
                    message_log = b_agent.name_b_agent + ", recupero la conexion en el nodo 138 -> " + now.strftime("%Y-%m-%d %H:%M:%S")
                    print(message_log)
                    os.popen("echo '" + message_log + "' >> history.log").read()
                    os.remove(b_agent.stats_folder + 'emailoff_node_1')
                    if current_hour >= self.INIT_HOUR and current_hour <= self.FINISH_HOUR:
                        # send email alerting that services are online
                        type_message = False # type_message -> True: Alert | False: Notice
                        self.email_sender.send_email(type_message, self.NODE_ONE, b_agent.name_b_agent)
                if os.path.exists(b_agent.stats_folder + 'emailoff_node_2'):
                    sms_message = "AVISO " + time.strftime('%X') + " -> Facturador " + b_agent.name_b_agent + ", recupero la conexion en el nodo 151."
                    message_log = b_agent.name_b_agent + ", recupero la conexion en el nodo 138 -> " + now.strftime("%Y-%m-%d %H:%M:%S")
                    print(message_log)
                    os.popen("echo '" + message_log +"' >> history.log").read()
                    os.remove(b_agent.stats_folder + 'emailoff_node_2')
                    if current_hour >= self.INIT_HOUR and current_hour <= self.FINISH_HOUR:
                        # send email alerting that services are online
                        type_message = False # type_message -> True: Alert | False: Notice
                        self.email_sender.send_email(type_message, self.NODE_TWO, b_agent.name_b_agent)
        # Finishing the analysis
        now = datetime.datetime.now()
        print("end: " + now.strftime("%Y-%m-%d %H:%M:%S"))
        os.popen("echo 'end " + now.strftime("%Y-%m-%d %H:%M:%S")  + "' >> history.log").read()

### MAIN ###
if __name__ == "__main__":
    monitor = Monitor()
    monitor.process_billing_agents()
