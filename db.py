from flask import flash
from flask_sqlalchemy import SQLAlchemy
import pymongo
import smtplib 
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import socket
import ast
# from email.message import EmailMessage

myserver = pymongo.MongoClient("mongodb://localhost:27017")
socket.getaddrinfo('localhost',8080)
mydb = myserver["Summarizer_Database"]

Users_Detail = mydb["User_Datail"] #personal details of user 
Users_Content = mydb["User_Content"] #content detail of users

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

# display()
# def display_content():
#     q =  Users_Content.find()
#     for i in q:
#         print(i)

# print(mydb.list_collection_names())
# print(myserver.list_database_names())
# function for entering record of user
def insert_precord(username,email):
    c = duplicate_mail(email)
    print(f'duplicate email {c}')
    if c != None:
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

def insert_srecord(mail, o_content, m_content):
    value = {'email': mail, 'Orignal_content': o_content, 'Modified_content': m_content}
    y = Users_Content.insert_one(value)
    print("content saved")
    return 1

# function to check whether email already exists
def duplicate_mail(mail):
    query = {"email": mail}
    a = Users_Detail.find_one(query)
    return a

#funtion to insert password for the given email
def insert_password(mail, sequence, img):
    if img and mail and sequence:
        a = duplicate_mail(mail)
        q = {'email':mail}
        if a != None:
            value={'password': sequence , 'image_name': img}
            b = Users_Detail.update_many(q,{"$set":value, "$currentDate":{"lastModified":True}})
            print("password set")
            return 'True'
        else:
            print("Email not found")
            return 'False'
    return 0

#function for checking password
def password_checker(mail, enter_pass):
    a = duplicate_mail(mail)
    print("enter_pass", enter_pass, type(enter_pass))
    print("a",a)
    if enter_pass != None:
        p = a['password']
        print(type(p))
        reg_pass = ast.literal_eval(a['password'])
        print("reg_pass",type(reg_pass))
        print("enter pass", enter_pass )
        ep = ast.literal_eval(enter_pass)
        print("ep",type(ep), ep)
        # print(type(reg_pass))
        reg_pass.sort()
        ep.sort()
        # print(reg_pass)
        # print(ep)
        if reg_pass == ep:
            return 1
        else:
            return 0
    else:
        return 3

def passowrd_set_or_not(user_dict):
    search_key = 'image_name'
    count = 0
    for key, value in user_dict.items():
        if key == search_key:
            # print(key)
            count = 1
            break
        else:
            count = 0
    return count

def mail_for_main(mail):
    email = 'summarywebapplication@gmail.com'
    password = 'summary@123'
    send_to_email = mail
    sub = 'Verficication Mail'
    link = "http://127.0.0.1:5000/main"
    msg = '<p> Please click on the link to summarize your data. </p>' + link

    m = MIMEMultipart('alertnative')
    m['From'] = email
    m['To'] = send_to_email
    m['Subject'] = sub

    m.attach(MIMEText(msg, 'html'))

    conn = smtplib.SMTP("smtp.gmail.com", 587)
    conn.starttls()
    conn.login(email, password)
    text = m.as_string()

    #1 jo send krta
    #2 jisko krna hota
    conn.sendmail(email, send_to_email, text)
    conn.quit()
    return True

def mail_for_password(mail):
    email = 'summarywebapplication@gmail.com'
    password = 'summary@123'
    send_to_email = mail
    sub = 'Verficication Mail'
    link = "http://127.0.0.1:5000/pass"
    msg = '<p> Please click on the link to reset your password. </p>' + link

    m = MIMEMultipart('alertnative')
    m['From'] = email
    m['To'] = send_to_email
    m['Subject'] = sub

    m.attach(MIMEText(msg, 'html'))

    conn = smtplib.SMTP("smtp.gmail.com", 587)
    conn.starttls()
    conn.login(email, password)
    text = m.as_string()

    #1 jo send krta
    #2 jisko krna hota
    conn.sendmail(email, send_to_email, text)
    conn.quit()
    return True

def delete():
    q = {'email' : ""}
    a = Users_Detail.find_one_and_delete(q)



# password_checker('shrmsh.1999@gmail.com',[238 ,255])
# display()