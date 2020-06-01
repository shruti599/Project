from flask import flash
from flask_sqlalchemy import SQLAlchemy
import pymongo
import smtplib 
import socket

myserver = pymongo.MongoClient("mongodb://localhost:27017")
socket.getaddrinfo('localhost',8080)
mydb = myserver["Summarizer_Database"]

Users_Detail=mydb["User_Datail"] #personal details of user 
Users_Content=mydb["User_Content"] #content detail of users


# def d():
#     em = {}
#     a = Users_Detail.find().sort("email")
#     for i in a:
#         em["mail"] = i["email"]
#         if i["email"] == em["mail"]:
#             Users_Detail.delete_one(i)

def display():
    q = Users_Detail.find()
    for i in q:
        print(i)


# print(mydb.list_collection_names())
# print(myserver.list_database_names())
#function for entering record of user
def insert_precord(username,email):
    c = duplicate_mail(email)
    print(f'duplicate email {c}')
    if c != 0: 
        flash("email already exist.")
        print("email exist.")
        return 0
    else:
        value = {'username':username , 'email': email}
        x = Users_Detail.insert_one(value)
        print("Record inserted successfully")
        flash("Inserted recorded")
        display()
        return 1

def insert_srecord():
    value = {"matter":matter}
    y = Users_Content.insert_one(value)
    print("content saved")

# function to check whether email already exists
def duplicate_mail(mail):
    query = {"email": mail}
    flag=0
    a = Users_Detail.find(query)
    for i in a:
        if i['email'] == mail:
            flag = flag + 1
            print(i)
            break
    if flag != 0:
        return 1
    else:
        return 0


#funtion to insert password for the given email
def insert_password(mail, sequence, img):
    # mail=input("enter mail: ")
    a = duplicate_mail(mail)
    q = {'email':mail}
    if a != 0:
        value={'password': sequence , 'image_name': img}
        b = Users_Detail.update_many(q,{"$set":value, "$currentDate":{"lastModified":True}})
        print("password set")
        return 'True'
    else:
        print("Email not found")
        return 'False'
    return 0


def mail_for_password(mail, main):
    conn = smtplib.SMTP("smtp.gmail.com",587)
    conn.starttls()
    conn.login("summarywebapplication@gmail.com","summary@123")
    #1 jo send krta
    #2 jisko krna hota
    conn.sendmail("summarywebapplication@gmail.com", mail, "Subject: practise\n\n Dear nalayak dost, stay safe\n\n")
    return True



# def delete():
#     query = {"email":'abc.209@gmail.com'}
#     a = Users_Detail.find_one_and_delete(query)
#     print(a.deleted_count)