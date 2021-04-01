from flask import Flask, render_template, request, redirect
import mysql.connector
from mysql.connector import Error, errorcode
import sys

app = Flask(__name__)

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
    
    def add_device(self, room_id, switch_type, sku_id, module_name, no_of_switches):
        self.mycursor.execute("Select RoomName from ROOM where ID like '"+room_id+"'")
        room_name = self.mycursor.fetchall()
        self.mycursor.execute("Insert into `Device`(`Room_ID`, `Room_Name`, `SKU_ID`, `Switch_type`, `Module_Name`, `No_of_switch`) Values ('"+room_id+"', '"+room_name[0][0]+"', '"+sku_id+"', '"+switch_type+"', '"+module_name+"', '"+no_of_switches+"')")
        self.connection.commit()

    def Create_switches(self, arr):
        self.mycursor.execute("Create TABLE IF NOT EXISTS Switch(ID INT AUTO_INCREMENT, Dev_ID VARCHAR(255), SEQ VARCHAR(255), Switch_Name VARCHAR(255), Is_Dimmable INT, PRIMARY KEY(ID))")
        for i in range(int(arr[0][0][0])):
            self.mycursor.execute("INSERT INTO `Switch`(`Dev_ID`, `SEQ`, `Switch_Name`, `Is_Dimmable`) VALUES (%s,%s,%s,%s)", (arr[4], arr[1][i], arr[2][i], arr[3][i]))
            self.connection.commit()
            
    def update_device(self, arr): 
        try:
            dev_id = arr[4]
            self.mycursor.execute("UPDATE `Device` SET `Module_Name`  = '" + arr[5] + "' WHERE `ID` = '" + dev_id + "'")
            self.connection.commit()
            for i in range(int(arr[0][0][0])):
                    self.mycursor.execute ("UPDATE Switch SET SEQ = '%s', Switch_Name = '%s', Is_Dimmable = '%d' where ID = '%d' "% (arr[1][i], arr[2][i], arr[3][i], arr[6][i]))
                    self.connection.commit()
        except mysql.connector.Error as error:
            self.connection.rollback()
            print("Failed to connect to SQL server {}".format(error))
    
    def create_room(self, userName, roomName):
        try:
            insert_room_details = """ INSERT INTO `ROOM`(`userID`, `RoomName`) VALUES (%s, %s)"""
            self.mycursor.execute("CREATE TABLE IF NOT EXISTS ROOM (ID INT AUTO_INCREMENT, userID VARCHAR(255), RoomName VARCHAR(255), PRIMARY KEY(ID))")

            self.mycursor.execute("SELECT userID, RoomName from ROOM WHERE `userID` like '" + userName + "' AND `RoomName` like '" + roomName + "'")
            user_data = self.mycursor.fetchall()
            user_data_len = len(user_data)
            if(user_data_len == 1):
                message = "Same Username and Room exists!"
                return render_template("create_room.html", message=message)
            else:
                self.mycursor.execute(insert_room_details, (userName, roomName))
                self.connection.commit()
                message = "Room succesfully created"
                return render_template("create_room.html", message=message)
        except mysql.connector.Error as error:
            self.connection.rollback()
            print("Failed to connect to SQL server {}".format(error))
            
    def update_room(self, userName, roomName, newName):
        try:
            self.mycursor.execute("SELECT ID from ROOM where `userID` like '" + userName + "' AND `RoomName` like '" + roomName + "'")
            room_id = self.mycursor.fetchall()
            roomID_data = []
            for i in range(len(room_id)):
                 roomID_data = roomID_data + list(room_id[i])
            self.mycursor.execute("UPDATE `Device` SET `Room_Name`  = '" + newName + "' WHERE `Room_ID` = '" + str(roomID_data[0]) + "' AND `Room_Name` = '" + roomName + "'")
            self.mycursor.execute("UPDATE `ROOM` SET `RoomName`  = '" + newName + "' WHERE `userID` = '" + userName + "' AND `RoomName` = '" + roomName + "'")
            self.connection.commit()
        except mysql.connector.Error as error:
            self.connection.rollback()
            print("Failed to connect to SQL server {}".format(error))

            
def Submit_edit_device():
    @app.route('/Submit/Device/Edit/<dev_id>', methods=['GET','POST'])
    def submit_edit_device(dev_id):
        sql = SQL_Ops()
        sql.mycursor.execute("Select No_of_switch from Device where `ID` like '"+dev_id+"'")
        no_of_switches = sql.mycursor.fetchall()
        sql.mycursor.execute("Select ID from Switch where `Dev_ID` like '"+dev_id+"'")
        switch_id = sql.mycursor.fetchall()
        
        if request.method == 'POST':
            seq_arr, switch_name_arr, isEnabled_arr, switch_id_arr = [], [], [], []

            new_module_name = request.form["new_module_name"]
            for i in range(int(no_of_switches[0][0])):
                new_seq_name=request.form["seq_name["+str(i)+"]"]
                seq_arr.append(new_seq_name)
                
                new_switch_name=request.form["switch_name["+str(i)+"]"]
                switch_name_arr.append(new_switch_name)
                
                switch_id_arr.append(switch_id[i][0])
                
                try:
                    isEnabled=int(request.form["isEnabled["+str(i)+"]"])
                except KeyError:
                    isEnabled = 0
                isEnabled_arr.append(isEnabled)
                
            arr = [no_of_switches] + [seq_arr] + [switch_name_arr] + [isEnabled_arr] + [dev_id] + [new_module_name] + [switch_id_arr]
            sql.update_device(arr)
            return(redirect('/Device'))
        
def Edit_device():
    @app.route('/Device/Edit/<dev_id>', methods=['GET','POST'])
    def edit_device(dev_id):
        sql = SQL_Ops()
        sql.mycursor.execute("Select Room_ID, Room_Name, Switch_type, Module_name, No_of_switch from Device where ID like '"+dev_id+"'")
        dev_details = sql.mycursor.fetchall()
        sql.mycursor.execute("Select userID from ROOM where `ID` like '"+dev_details[0][0]+"'")
        user_name = sql.mycursor.fetchall()
        data = [user_name] + [dev_details]
        return(render_template("edit_device.html", data = data, url_data = dev_id))
    
def Submit_switch():
    @app.route('/Submit/Switch/<dev_id>', methods=['GET','POST'])
    def switch_val(dev_id):
        sql = SQL_Ops()
        sql.mycursor.execute("Select No_of_switch from Device where `ID` like '"+dev_id+"'")
        no_of_switches = sql.mycursor.fetchall()

        if request.method=='POST':
            seq_arr, switch_name_arr, isEnabled_arr = [], [], []                        
            for i in range(int(no_of_switches[0][0])):
                new_seq_name=request.form["seq_name["+str(i)+"]"]
                seq_arr.append(new_seq_name)
            for i in range(int(no_of_switches[0][0])):
                new_switch_name=request.form["switch_name["+str(i)+"]"]
                switch_name_arr.append(new_switch_name)
            for i in range(int(no_of_switches[0][0])):
                try:
                    isEnabled=int(request.form["isEnabled["+str(i)+"]"])
                except KeyError:
                    isEnabled = 0
                isEnabled_arr.append(isEnabled)

            arr = [no_of_switches] + [seq_arr] + [switch_name_arr] + [isEnabled_arr] + [dev_id]
            sql.Create_switches(arr)
            return(redirect('/Device'))
           
def Add_switches():
    @app.route('/Switches/<no_of_dev>', methods=['GET','POST'])
    def add_switches(no_of_dev):
        dev_id = str(no_of_dev)
        sql = SQL_Ops()
        sql.mycursor.execute("SELECT Room_ID, Room_Name, Switch_type, Module_Name, No_of_switch, ID FROM Device where `ID` like '"+dev_id+"'")
        dev_details = sql.mycursor.fetchall()
        room_id = dev_details[0][0]
        sql.mycursor.execute("SELECT userID FROM ROOM where `ID` like '"+room_id+"'")
        user_details = sql.mycursor.fetchall()
        user_details = user_details[0][0]
        return(render_template("add_switches.html", data=dev_details, user_data=user_details, message=dev_details[0][0]))

def Submit_Device():
    @app.route('/Submit/Device/<room_id>', methods=['Get', 'POST'])
    def submit(room_id):
        if(request.method == 'POST'):
            sku_id = request.form['sku_id']
            switch_type = request.form['switch_type']
            module_name = request.form['module_name']
            no_of_switches = request.form['no_of_switches']
            sql = SQL_Ops()
            sql.add_device(room_id, switch_type, sku_id, module_name, no_of_switches)
            return(redirect('/Device'))

        return(render_template('add_device.html', data=room_id))
   
def Add_Devices():
    @app.route('/Device/Create/<room_id>', methods=['Get', 'POST'])
    def add_device(room_id):
        switch_type_select = ['Triac', 'Relay 10A', 'Relay 20A']
        switch_no = ['1', '2', '4', '6', '10']
        data = [switch_type_select] + [switch_no] + [room_id]

        return(render_template('add_device.html', data=data))
    

def Select_Room():
    @app.route('/Device/Create', methods=['Get', 'POST'])
    def select_room():
        sql = SQL_Ops()
        sql.mycursor.execute("Select ID, userID, RoomName from ROOM")
        room_table = sql.mycursor.fetchall()
        return(render_template('Create_device.html', data=room_table))

    
def Device_page():
    @app.route('/Device', methods=['GET','POST'])
    def show_modules():
        sql = SQL_Ops()
        sql.mycursor.execute("CREATE TABLE IF NOT EXISTS Device (ID INT AUTO_INCREMENT, Room_ID VARCHAR(255), Room_Name VARCHAR(255), SKU_ID VARCHAR(255), Switch_type VARCHAR(255), Module_Name VARCHAR(255), No_of_switch VARCHAR(255), PRIMARY KEY(ID))")
        sql.mycursor.execute("SELECT ID, SKU_ID, Module_Name, Room_Name, Switch_type, No_of_switch, Room_ID from Device")
        result = sql.mycursor.fetchall()
        return render_template("device.html", data=result)

def Submit_Room():
    @app.route('/Submit/Edit/Room', methods=['GET','POST'])
    def submit_data():
        sql = SQL_Ops()
        if(request.method=='POST'):
            userName=request.form["emailID[0]"]
            roomName=request.form["room_name[0]"]
            newName=request.form["new_name"]
            sql.update_room(userName, roomName, newName)
            sql.mycursor.execute("SELECT ID, userID, RoomName from ROOM")
            result = sql.mycursor.fetchall()
            return(redirect('/Room'))

def Room_edit():
    @app.route('/Room/edit/<no_of_room>', methods=['GET','POST'])
    def edit_room(no_of_room):
        room_no = str(no_of_room)
        sql = SQL_Ops()
        sql.mycursor.execute("Select userID, RoomName from ROOM where `ID` like '"+room_no+"'")
        data = sql.mycursor.fetchall()          
        return render_template("edit_room.html", data=data)
        
def Room_Creation():
    @app.route('/Room/Create', methods=['GET','POST'])
    def show_user():
        sql = SQL_Ops()
        sql.mycursor.execute("SELECT emailId from User_details")  
        user_data = sql.mycursor.fetchall()
        data = []
        for i in range(len(user_data)):
            data = data + list(user_data[i])
            
        if request.method=='POST':
            userName=request.form['emailID']
            roomName=request.form["roomName"]
            sql.create_room(userName, roomName)
            return(redirect('/Room'))
        return render_template('create_room.html', emailID=data)

def Room_page():
    @app.route('/Room', methods=['GET','POST'])
    def show_rooms():
        sql = SQL_Ops()
        sql.mycursor.execute("SELECT ID, userID, RoomName from ROOM")
        result = sql.mycursor.fetchall()
        return render_template("Room.html", data=result)

def main():
    Room_Creation()
    Room_page()
    Room_edit()
    Submit_Room()
    
    Device_page()
    Select_Room()
    Add_Devices()
    Submit_Device()
    Add_switches()
    Submit_switch()
    Edit_device()
    Submit_edit_device()
    
    app.run(debug=True, host='0.0.0.0', port=5000)

if __name__ == "__main__":
    sys.exit(main())