from flask import Flask, render_template, flash, request, redirect, url_for, send_from_directory, session
from werkzeug.utils import secure_filename
from summarize import summarize
import os
import json
from function import extract_text_from_pdf, get_image_name, get_image_path, extract_text
import re
from db import insert_precord, insert_srecord, duplicate_mail, insert_password, mail_for_password, password_checker, passowrd_set_or_not


UPLOAD_FOLDER = 'static/uploaded_files'
ALLOWED_EXTENSIONS = set(['txt','pdf','doc','docx'])

app=Flask(__name__)
app.secret_key="hello"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],filename)

content_detail=""
contents=""
@app.route('/main', methods=['GET','POST'])
def main():
    global content_detail
    if request.method == 'POST':
        print("under post")
        data = request.form.get('text')
        lines = request.form.get('lines')
        print("post")
        print(data)
        if data != None:
            if lines == None: 
                lines = str(13)  #temporary assigning here
            print(lines)
            session['lines'] = str(lines)
            content_detail = data
            print(content_detail)
            return redirect(url_for('text_result'))      
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
            print(filename)
            ext = filename.rsplit('.',1)[1]
            # print("ext"+ext)
            if ext == 'pdf':
                contents = extract_text_from_pdf('static\\uploaded_files\\' + filename)
                return render_template('main.html', content = contents)
            else:
                contents = extract_text('static\\uploaded_files\\' + filename)
                return render_template('main.html', content = contents)
        # print(request.form.get("text"))
    else:
        contents=""
        print("get")
        return render_template('main.html', content=contents)

@app.route('/text_result' ,methods = ['GET', 'POST'])
def text_result():
    result = ""
    global content_detail
    if request.method == 'GET':
        data = content_detail
        lines = session.get('lines',None)
        print(lines)
        print("data",data)
        if data != "":
            if lines != None:
                lines = str(13)
            result = json.loads(summarize(data,lines))
            print(result)
            if result !=  "":
                session['summary']=result
                return render_template('sum_result.html', results=result)
        else:
            print(result)
            result = None
            return redirect(url_for('site'))
    else:
        print(result)
        return redirect(url_for('userdash'))

# @app.route('/display_error')
# def some_error():
#     if session.get('summary') == "":
#         return render_template('some_error.html')

@app.route('/userpass', methods=['GET','POST'])
def userpassword():
    reg_pass = []
    img = session.get('image','None')
    if img != 'None':
        path_of_image = get_image_path(img)
    if request.method == 'GET':
        print(path_of_image)
        return render_template('userpass.html', img_path = path_of_image)
    else:
        m = session.get('registered_mail', 'None')
        se = request.form.get('seq')
        r = password_checker(m, se)
        print(r)
        if r == 1:
            return redirect(url_for('main'))
        else:
            err = "Wrong Password"
            return render_template('userpass.html', img_path = path_of_image, error = err)
    

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
                return redirect(url_for('reg_confirmation'))
        else :
            print("no data")
    return render_template('pass1.html')


@app.route('/confirm')
def reg_confirmation():
    mail = session.get("email_value", 'None')
    if mail != 'None':
        mail_for_password(mail)
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
def login():
    re = {}
    if request.method == 'POST':
        m = request.form['mail'].strip()
        re['user_record'] = duplicate_mail(m)
        print("re value")
        print(re['user_record'])
        if re['user_record'] != None:
            val = re['user_record']
            v = passowrd_set_or_not(val)
            print("value of v")
            print(v)
            if v != 0:
            # if re['user_record']['image_name'] 
                n = re['user_record']['image_name']
            # # print(n)
                session['image'] = n
                session['registered_mail'] = m
                return redirect(url_for('userpassword'))
            else:
                return render_template('login.html', error ="Your password is not set. Please click on forget password to set your password.")
        else:
            print("when record is none.")
            return render_template('login.html', error = "E-mail is not registered.Please register yourself.") 
        # check that mail exist in db
    return render_template('login.html')

# @app.route('/')
# def home():
#     return render_template('home.html') 

@app.route('/')
def site():
    return render_template('index.html')

@app.route('/some_error')
def some_error():
    return render_template('some_error.html')

@app.route('/demo')
def demo():
    return render_template('checking.html')

@app.route('/adminlog', methods=['POST', 'GET'])
def admin():
    return render_template('adminlog.html')

@app.route('/dash')
def admin_dash():
    return render_template('admindash.html')

@app.route('/main_replica', methods=['GET','POST'])
def main_replica():
    if request.method == 'POST':
        name = request.form['name']
        num = request.form['number']
        print(name)
        print(num)
        if name and num:
            return render_template('checking.html')
        else:
            return redirect(url_for('main_replica'))
    else:
        return render_template('main_replica.html')
    
if __name__ == "__main__":
    app.run(debug=True)