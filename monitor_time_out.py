#!/usr/bin/python
import yaml
import subprocess
import urllib2
import os
import time


class Monitor:
    ''' Abstraction of an Monitor'''
    # Static Class Constants
    MAX_BITES = 5242880
    PATH_YML = 'facturadores_list.yaml'
    PATH_DATA = "data/"

    def __init__(self):
        pass

    def send_sms(self, cellphone_number, error_message):
        print("Alerting to " + cellphone_number + "...")
        url = 'http://10.30.12.38:9081/courier/api/secure/messages'
        data = '{"channelDestination": "SMS","recipient": "' + cellphone_number + '","message": "' + error_message + '"}'
        req = urllib2.Request(url, data)
        req.add_header('Cache-Control', 'no-cache')
        req.add_header('Content-Type', 'application/json')
        req.add_header('X-JOKO-AUTH', 'eyJhbGciOiJIUzUxMiJ9.eyJzdWIiOiJNb25pdG9yZW8iLCJleHAiOjE2MDc1MjQ3NjUsImlhdCI6MTU3NTk4ODc2NSwianRpIjoiNUZERjRYN0xGRk9aWllDV1EyTEEiLCJqb2tvIjp7InR5cGUiOiJBQ0NFU1MiLCJyb2xlcyI6WyJCQUNLT0ZGSUNFIl0sInByb2ZpbGUiOiJERUZBVUxUIn19.ycGxxnia6M_quGbyemEGjppp3NeGuwD-Yhg9InXzE-EDcn2xdpx8uGPxtVy5Sl-PZ_0BAA3umwyf0_J0Ol02zw')
        req.get_method = lambda: "POST"

        proxy_handler = urllib2.ProxyHandler({})
        opener = urllib2.build_opener(proxy_handler)
        urllib2.install_opener(opener)

        http_request = urllib2.urlopen(req)
        # result printing
        # for line in http_request:
        #    print(line)
        http_request.close()
        return

    def get_count(self, filename):
        source_file = open(filename, 'r')
        content = source_file.readline()
        return int(content)

    def add_count(self, filename, increment):
        count = getCount(filename) + increment
        writeCount(filename, count)

    def writeCount(self, filename, count):
        target_file = open(filename, 'w')
        target_file.write(str(count))
        target_file.close()

    def main(self):
        # Change directory to this script directory
        abspath = os.path.abspath(__file__)
        dname = os.path.dirname(abspath)
        os.chdir(dname)

        # Alert on N errors
        numberOfErrorsToAlert = 5

        # Delete log file if bigger than 5MB
        logFile = 'monitor.log'
        statinfo = os.stat(logFile)
        size = statinfo.st_size
        if (size >= self.MAX_BITES):
            os.remove(logFile)

        with open(self.PATH_YML) as f:
            docs = yaml.load_all(f, Loader=yaml.FullLoader)
            for doc in docs:
                for key, value in doc.items():
                    facturador = key
                    timeout = str(value["timeout"])
                    #curl = value["curl"] + " -m " + timeout
                    curl = value["curl"]
                    description = value["description"]

                    print("====================================")
                    print("facturador: " + facturador + "...")
                    print("curl: " + curl)
                    print("description: " + description)
                    print("timeout: " + timeout)

                    print("executing curl...")
                    p = subprocess.Popen(curl, stdout=subprocess.PIPE, shell=True)
                    (output, err) = p.communicate()
                    print("output: " + output)
                    # Check if max timeout was exceeded
                    if (float(output) >= float(timeout)):
                        addCount(statsDir + facturador, 1)
                        currentCount = getCount(statsDir + facturador)
                        if (currentCount >= numberOfErrorsToAlert):
                            writeCount(statsDir + facturador, 0)
                        if (not os.path.exists("smsoff")):
                            print("problem!!!, number of timeouts reached, numberOfErrorsToAlert: " + str(numberOfErrorsToAlert))
                            error_message = "Problema con facturador en nodo (10.10.17.138): " + description + ", cantidad de timeouts seguidos: " + str(currentCount) + ", verificar!!!"
                            #Aki
                            sendSMS("0983523814", error_message)
                            #Gustavo
                            sendSMS("0983524013", error_message)
                            #Victor
                            sendSMS("0981551796", error_message)
                            #Paola
                            sendSMS("0971251737", error_message)
                            #Bruno
                            sendSMS("0982225476", error_message)
                            #Jose
                            sendSMS("0985775785", error_message)
                            #Dani
                            sendSMS('0971160145', error_message)
                        else:
                            print("alerts turned off!!!")
                        datetime = time.strftime('%Y/%m/%d %H:%M:%S')
                        print(datetime)
                    else:
                        writeCount(statsDir + facturador, 0)
                        currentCount = getCount(statsDir + facturador)
                        datetime = time.strftime('%Y/%m/%d %H:%M:%S')
                        print(datetime + " - response time: " + output + " less than: " + timeout + ", nothing wrong!")
                    print("errors: " + str(currentCount))
                    print("====================================")


### MAIN ###
if __name__ == '__main__':
    monitor = Monitor()
    monitor.main()