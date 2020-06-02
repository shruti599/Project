from flask import Flask, render_template, flash, request, redirect, url_for, send_from_directory, session
from werkzeug.utils import secure_filename
from summarize import summarize
import os
import json
from function import extract_text_from_pdf, get_image_name, get_image_path
import re
from db import insert_precord, insert_srecord, duplicate_mail, insert_password, mail_for_password


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
# def is_email_address_valid(email):
#     """Validate the email address using a regex."""
#     if not re.match("^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)*$", email):
#         return False
#     return True

#function for sending mail


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

@app.route('/userpass', methods=['GET','POST'])
def userpassword():
    img = session.get('image','None')
    m = session.get('registered_mail', 'None')
    path_of_image = get_image_path(img)
    print(path_of_image)
    # if request.method == 'POST':
    
    return render_template('userpass.html', img_path = path_of_image)

@app.route('/userdash')
def userdash():
    return render_template('userdash.html')

@app.route('/useraccount')
def useraccount():
    return render_template('useraccount.html')

@app.route('/pass', methods=['GET' , 'POST'])
def password():
    mail = session.get('email_value','None')
    print(mail)
    if request.method == 'POST':
        seq = request.form.get('seq')
        image = request.form.get('image')
        if image and seq and mail:
            image = get_image_name(image)
            print(mail, seq, image)
            val = insert_password(mail, seq, image)
            if val == "True":
                return redirect('/confirm')
        else :
            print("no data")
    return render_template('pass1.html')

@app.route('/adminlog')
def admin():
    return render_template('adminlog.html')

@app.route('/confirm')
def reg_confirmation():
    # mail_for_password(mail, main)
    return render_template('confirm.html')

@app.route('/confpass')
def reg_confirm():
    return render_template('confpass.html')

@app.route('/register',methods = ['GET', 'POST'])
def register():
    # Initialize the errors variable to empty string. We will have the error message in that variable, if any.
    if request.method == "POST": 
        # Stripping it to remove leading and trailing whitespaces
        email = request.form['mail'].strip()
        username = request.form['username'].strip()
        # Check if all the fields are non-empty and raise an error otherwise
        # if not errors:
        # #if errors != "":
        #     # Validate the email address and raise an error if it is invalid
        #     if not is_email_address_valid(email):
        #         errors = errors + "Please enter a valid email address"
        errors =  insert_precord(username,email)
        if errors != 0:
            #encrypt the mail
            session['email_value'] = email
            return redirect(url_for('password'))
        else:
            errors = "Email exist"
            return render_template('registration.html',errors = errors)
    else:
        return render_template('registration.html')

#if email exits then send password to that mail & store it in db  

@app.route('/login', methods=['GET', 'POST'])
def about():
    re = {}
    if request.method == 'POST':
        m = request.form['mail'].strip()
        re['user_record'] = duplicate_mail(m)
        print(re)
        if re != {}:
            n = re['user_record']['image_name']
            print(n)
            session['image'] = n
            session['registered_mail'] = m
            return redirect(url_for('userpassword'))
        # check that mail exist in db
    return render_template('login.html')

@app.route('/')
def home():
    return render_template('home.html') 
    
if __name__ == "__main__":
    app.run(debug=True)