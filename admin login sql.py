from flask import Flask, render_template, request, session, redirect, url_for, flash
import mysql.connector
from mysql.connector import Error, errorcode

app = Flask(__name__)

class SQL_Ops:
    def __init__(self):
        try:
            self.connection = mysql.connector.connect(
                host = "localhost",
                user = "admin",
                passwd = "raspberry",
                database = "nGShelter"
                )
            self.mycursor = self.connection.cursor()
            print("Connected to SQL database")

        except mysql.connector.Error as error:
            self.connection.rollback()
            print("Failed to connect to MySql server {}".format(error))
        

@app.route('/', methods=['post', 'get'])    
def login():
    message = ''
    if request.method == 'POST':
        admin_user = request.form.get('username')  # access the data inside 
        admin_pass = request.form.get('password')
        
        sql = SQL_Ops()
        sql.mycursor.execute("Create Table IF NOT EXISTS admin_user( ID INT AUTO_INCREMENT PRIMARY KEY, Username VARCHAR(255), Password VARCHAR(255))")
        sql.mycursor.execute("INSERT INTO `admin_user`(`Username`, `Password`) VALUES (%s,%s)", ("admin", "admin"))
        sql.mycursor.execute("SELECT username, password from admin_user WHERE `Username` like '" + admin_user + "' AND `Password` like '" + admin_pass + "'")
        user_data = sql.mycursor.fetchall()
        if(len(user_data) == 1):
            if(user_data[0][0] == admin_user and user_data[0][1] == admin_pass):
                message = "Correct username and password"
                print(len(user_data[0][0]))
                return render_template('admin.html')
        else:
            message = "Wrong username or password"

    return render_template('login.html', message=message)

        

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)






    
