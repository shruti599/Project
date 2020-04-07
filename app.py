from flask import Flask, render_template, flash, request, redirect, url_for, send_from_directory, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from summarize import summarize
import pymongo
import os
import json
from function import extract_text_from_pdf
import re
import smtplib 

myserver=pymongo.MongoClient("mongodb://localhost:27017")

mydb=myserver["Summarizer_Database"]

Users_Detail=mydb["User_Datail"] #personal details of user
Users_Content=mydb["User_Content"] #content detail of users

#function for entering record of user
def insert_precord(username,email):
    value = {"username":username , "email": email, "password":password}
    x = Users_Detail.insert_one(value)
    print("Record inserted successfully")
    flash("Inserted recorded")

def insert_srecord():
    value = {"content":content}
    y = Users_Content.insert_one(value)
    print("content saved")

UPLOAD_FOLDER = 'static/uploaded_files'
ALLOWED_EXTENSIONS = set(['txt','pdf'])

app=Flask(__name__)
app.secret_key="hello"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],filename)

#function for validing email
def is_email_address_valid(email):
    """Validate the email address using a regex."""
    if not re.match("^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)*$", email):
        return False
    return True

#function for sending mail
def mail_for_password():
    conn = smtplib.SMTP("smtp.gmail.com",587)
    conn.starttls()
    conn.login("mailid","password")
    #1 jo send krta
    #2 jisko krna hota
    conn.sendmail("shrmsh.1999@gmail.com","upendrasingh11lko@gmail.com","Subject: practise\n\n Dear nalayak dost, stay safe\n\n")
    return True

contents=""
@app.route('/main',methods=['GET','POST'])
def main():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            #print("No file selected")
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            print(os.path.exists(app.config['UPLOAD_FOLDER']))
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            contents=extract_text_from_pdf('static\\uploaded_files\\'+filename)
    else:
        contents=""
    return render_template('main.html', content=contents)


@app.route('/text_result' ,methods = ['GET', 'POST'])
def text_result():
    if request.method == 'POST':
        lines=(request.form.get("lines"))
        data=request.form.get("text")
        if not data == "":
            results = json.loads(summarize(data,lines))
            session['summary']=results
        else:
            results = None
        return render_template('sum_result.html',results=results)
    # else:
    #     return render_template('sum_result.html')

@app.route('/userpass')
def userpassword():
    return render_template('userpass.html')

@app.route('/userdash')
def userdash():
    return render_template('userdash.html')

@app.route('/useraccount')
def useraccount():
    return render_template('useraccount.html')


@app.route('/pass')
def password():
    return render_template('pass1.html')

@app.route('/adminlog')
def admin():
    return render_template('adminlog.html')

@app.route('/confirm')
def reg_confirmation():
    return render_template('confirm.html')


@app.route('/register',methods = ['GET', 'POST'])
def register():
    # Initialize the errors variable to empty string. We will have the error messages
    # in that variable, if any.
    errors = ''
    if request.method == "GET": # If the request is GET, render the form template.
        return render_template("registration.html", errors=errors)
     else: 
        # The request is POST with some data, get POST data and validate it.
        # The form data is available in request.form dictionary. Stripping it to remove
        # leading and trailing whitespaces
        email = request.form['email'].strip()
        username = request.form['username'].strip()
        # Check if all the fields are non-empty and raise an error otherwise
        if not email or not username:
            errors = "Please enter all the fields."
        if not errors:
            # Validate the email address and raise an error if it is invalid
            if not is_email_address_valid(email):
                errors = errors + "Please enter a valid email address"
        if not errors:
            #if email exits then send password to that mail & store it in db
            
        return render_template('registration.html')

@app.route('/login')
def about():
    return render_template('login.html')

@app.route('/')
def home():
    return render_template('layout.html') 
    
if __name__ == "__main__":
    app.run(debug=True)