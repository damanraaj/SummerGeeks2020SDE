import requests
import json

URL = 'https://www.way2sms.com/api/v1/createSenderId'

# post request
def sendPostRequest(reqUrl, apiKey, secretKey, useType, senderId):
  req_params = {
  'apikey':apiKey,
  'secret':secretKey,
  'usetype':useType,
  'senderid':senderId
  }
  return requests.post(reqUrl, req_params)

# get response
print("Enter API Key : ",end="")
APIKEY=input()
print("Enter Secret Key : ",end="")
SECRET=input()
print('Enter Sender ID : ',end="")
SENDERID=input()
response = sendPostRequest(URL, APIKEY, SECRET, 'prod', SENDERID)
"""
  Note:-
    you must provide apikey, secretkey, usetype and senderid values
    and then requst to api
"""
# print response if you want
print (response.text)
