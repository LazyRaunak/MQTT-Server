#!flask/bin/python
from flask import Flask, request, Response
import paho.mqtt.client as paho
import mysql.connector
from mysql.connector import Error, errorcode
import json
import sys

app = Flask(__name__)

mqtt_host = "192.168.100.5"
mqtt_port = 1883

def on_connect(client, userdata, flags, rc):
    if(rc == 0):
        print("Connected to the broker")
    else:
        print("Connection failed")
        
def on_subscribe(client1, userdata, mid, qos):
    print("Subscribed: " +str(mid))
    
def mqtt_connect():
    client = paho.Client()
    client.on_connect = on_connect
    client.connect(mqtt_host, mqtt_port)
    client.loop_start()
    return(client)

class SQL_Ops:
    def __init__(self):
        try:        
            print("In SQL function")
            self.connection = mysql.connector.connect(
                host = "localhost",
                user = "admin",
                passwd = "raspberry",
                database = "nGShelter"
                )
            self.mycursor = self.connection.cursor()
            print("Successfully connected to database")
        except mysql.connector.Error as error:
            self.connection.rollback()
            print("Failed to connect to SQL server {}".format(error))

    def login_verify(self, content):
        self.mycursor.execute("SELECT ID, firstName, lastName from User_details WHERE `emailId` like '" + content["EmailId"] + "' AND `password` like '" + content["Password"] + "'")
        user_data = self.mycursor.fetchall()
        if(len(user_data) == 1):
            data_val = [{"Id":user_data[0][0], "FirstName":user_data[0][1], "LastName":user_data[0][2], "MobileNumber": "null", "UserApiToken": "", "MqttBrokerAddress":mqtt_host, "MqttBrokerPort":mqtt_port, "MqttUsername": "", "MqttPassword": ""}]
            login_reponse = { "Status": "true", "ErrorCode": 0, "Message": "null", "Data": data_val }
            return Response(json.dumps(login_reponse), mimetype='application/json')
        else:
            login_reponse = { "Status": "false", "ErrorCode": 2, "Message": "Please check Email Id and Password", "Data": "null" }
            return Response(json.dumps(login_reponse), mimetype='application/json')

            
def login_webservice():
    @app.route('/api/user/Login', methods=['POST'])
    def login():
        content = request.get_json()
        sql = SQL_Ops()
        return(sql.login_verify(content))
    

def getUserDeviceInfo():    
    @app.route('/api/mobile/GetUserDeviceInfo', methods=['POST'])
    def DeviceInfo():
        print("")
        return("")

    
def main():
    login_webservice()
    getUserDeviceInfo()

    app.run(debug=True, host='0.0.0.0', port=5000)


if __name__ == '__main__':
    sys.exit(main())




 
