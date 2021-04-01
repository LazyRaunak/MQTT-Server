#!flask/bin/python
from flask import Flask, request, Response
import paho.mqtt.client as paho
import mysql.connector
from mysql.connector import Error
from mysql.connector import errorcode
import json
import sys

app = Flask(__name__)

from flask import Flask
from flask import request

false_json = {"Status": "false",
    "ErrorCode": 3,
    "Message": "Email Id Already Exists",
    "Data": "null"
}

true_json = {"Status": "true",
    "ErrorCode": 0,
    "Message": "null",
    "Data": "null"
}

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

    def insertUser(self, content):
        print("In insertUser function")
        try:
            insert_user_details = """ INSERT INTO `User_details`(`firstName`, `lastName`, `emailId`, `password`) VALUES (%s, %s, %s, %s)"""
            
            self.mycursor.execute("CREATE TABLE IF NOT EXISTS User_details (ID INT AUTO_INCREMENT, firstName VARCHAR(255), lastName VARCHAR(255), emailId VARCHAR(255), password VARCHAR(255), PRIMARY KEY(ID))")

            self.mycursor.execute("SELECT emailId from User_details WHERE `emailId` like '" + content["EmailId"] + "'")
            user_data = self.mycursor.fetchall()
            user_data_len = len(user_data)

            if(user_data_len == 1):
                return Response(json.dumps(false_json), mimetype='application/json')

            else:
                self.mycursor.execute(insert_user_details, (content["FirstName"], content["LastName"], content["EmailId"], content["Password"]))
                self.connection.commit()
                return Response(json.dumps(true_json), mimetype='application/json')
            
        except mysql.connector.Error as err:
            print("Unable to create table: {}".format(err))

def registration():
    @app.route('/api/user/Registration', methods=['POST'])
    def register():
        content = request.get_json()
        sql = SQL_Ops()
        return(sql.insertUser(content))
        

def main():
    registration()

    app.run(debug=True, host='0.0.0.0', port=5000)

if __name__ == '__main__':
    sys.exit(main())



    
