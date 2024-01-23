# Version data here

# Imports
import sqlite3 as sql
import os
from getpass import getpass


# Functions
def hashString(string:str) -> str:
    from hashlib import sha1
    return str(sha1(string.encode("utf-8")).hexdigest())

def openSystem() -> tuple:
    db = sql.connect("systemSettings.db")
    c = db.cursor()
    return db, c

def closeSystem(db) -> None:
    db.commit()
    db.close()

def getInput(prompt:str=""):
    return input(prompt+">")


# Classes
class System:
    def __init__(self) -> None:
        self.logout()

    def logout(self) -> None:
        self.userID = None
        self.username = None
        self.userAccessRecords = None
    
    def login(self, username:str, passwordStr:str) -> str:
        db, c = openSystem()
        users = c.execute("SELECT * FROM Users").fetchall()
        found = False
        for user in users:
            userid, userName, passwordHash = user
            if userName == username:
                found = True
                break
        if not found:
            return "invalid_username"
        if passwordHash != hashString(passwordStr):
            return "invalid_password"
        self.userID = userid
        self.username = username
        accessRecords = c.execute("SELECT * FROM accessREcords").fetchall()
        userRecords = []
        for record in accessRecords:
            recordid, userid, dbname, table = record
            if userid == self.userID:
                userRecords.append(record)
        self.userAccessRecords = userRecords
        return "success"

    def newUser(self, username:str, passwordStr:str) -> str:
        db, c = openSystem()
        users = c.execute("SELECT * FROM Users").fetchall()
        IDs, usernames = [x[0] for x in users], [x[1] for x in users]
        newID = len(IDs) + 1
        if username in usernames:
            closeSystem(db)
            return "invalid_username"
        c.execute("INSERT INTO Users VALUES (?, ?, ?)", (newID, username, hashString(passwordStr)))
        closeSystem(db)
        return "success"
    
    def newAccessRecord(self, userID:int, dbName:str, table:str=None) -> str:
        db, c = openSystem()
        IDs = c.execute("SELECT arID FROM accessRecords").fetchall()
        userIDs = [x[0] for x in c.execute("SELECT userID FROM Users").fetchall()]
        if userID not in userIDs:
            closeSystem(db)
            return "invalid_userid"
        newID = len(IDs) + 1
        c.execute("INSERT INTO accessRecords VALUES (?, ?, ?, ?)", (newID, userID, dbName, table if table else ""))
        closeSystem(db)
        return "success"


class Display:
    def __init__(self) -> None:
        self.currentScreen = "login"
        self.headerChar = "="
        self.headerMinLength = 20
        self.separateChar = "-"
        self.columnSpace = 4


    def cls(self) -> None:
        os.system("cls" if os.name == "nt" else "clear")

    def header(self, text:str, upper:bool=True) -> str:
        if len(text) > self.headerMinLength:
            headerLength = len(text)+2
        else:
            headerLength = self.headerMinLength
        if len(text) % 2 != 0 and headerLength % 2 == 0:
            headerLength += 1
        textSpace = (headerLength - len(text)) // 2
        headerStr = f"\n{' ' * textSpace}{text.upper() if upper else text}\n{self.headerChar * headerLength}\n"
        return headerStr

    def update(self) -> None:
        # self.cls()
        print(self.header(self.currentScreen))


# Main
def main() -> None:
    DISPLAY.update()

    username = getInput("Username")
    if username == "create":
        pass  # do work
    else:
        password = getpass("Password>")
        print("Checking details")
        result = SYSTEM.login(username, password)
        if result == "success":
            DISPLAY.currentScreen = "menu"
            DISPLAY.update()
            # do main menu work
        else:
            print("User not found or password incorrect")
            main()


if __name__ == "__main__":
    os.remove("systemSettings.db")
    db = sql.connect("systemSettings.db")
    c = db.cursor()
    c.execute("CREATE TABLE Users (userID integer, username text, passwordHash text)")
    c.execute("CREATE TABLE AccessRecords (arID integer, userID integer, dbName text, tableName text)")
    db.commit()
    db.close()
    SYSTEM = System()
    SYSTEM.newUser("fred", "test")
    DISPLAY = Display()
    main()