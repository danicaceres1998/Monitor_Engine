#!/usr/bin/python3
import json
import os

command = os.popen("java -jar sql2json.jar \"SELECT * FROM GXGEDTA.GFT006 WHERE GF06WSID LIKE 'ZIMPLE%'\"")
result = command.read()
json_dic = json.loads(result)
print(json_dic)
print (json_dic['count'])
print (json_dic['records'][0]['GF06BASURL'])