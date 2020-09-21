from flask import Flask, render_template, flash, request, redirect, url_for, send_from_directory, session, jsonify
from werkzeug.utils import secure_filename
from summarize import summarize
import os
import json
from function import extract_text_from_pdf, get_image_name, get_image_path, extract_text
import re
from db import insert_precord, insert_srecord, duplicate_mail, insert_password, mail_for_main, password_checker, passowrd_set_or_not, mail_for_password, insert_modified_content, insert_summary


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

#global variables    
logged_in = False
logged_email = ""
content_detail=""

def clear_all():
    logged_in = False
    logged_email = ""
    content_detail=""
    return "cleared"

@app.route('/register',methods = ['GET', 'POST'])
def register():
    global logged_email
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
            logged_email = email
            return redirect(url_for('password'))
        else:
            errors = "Email exist"
            return render_template('registration.html', errors = errors)
    # else:
    return render_template('registration.html')

# @app.route('/process', methods=['POST'])
# def rprocess():
#     # user = request.form('user')
#     # mail = request.form('mail')
#     user = request.agrs.get('user')
#     mail = request.args.get('mail')
#     user = user.strip()
#     mail = mail.strip()
#     return_value = insert_precord(user,mail)
#     if return_value == 1 :
#         response = "Successfully regiertered. Please set password."
#         # return json.dumps({'status':response})
#     else:
#         response = "This email already exist!"
#         # return json.dumps({'status':error})
#     return jsonify({'success':response})

#if email exits then send password to that mail & store it in db  

@app.route('/pass', methods=['GET' , 'POST'])
def password():
    global logged_email
    mail = logged_email
    print(mail)
    if request.method == 'POST':
        seq = request.form.get('seq')
        image = request.form.get('image')
        if image and seq and mail:
            image = get_image_name(image)
            print(mail, seq, image)
            val = insert_password(mail, seq, image)
            if val == "True":
                logged_in = True
                mail_for_main(mail)
                return redirect(url_for('reg_confirmation'))
        else :
            print("no data")
    return render_template('pass1.html')

@app.route('/confirm')
def reg_confirmation():
    return render_template('confirm.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    clear_all()
    global logged_email
    re = {}
    if request.method == 'POST':
        m = request.form.get('mail')
        forget_mail = request.form.get('forget-mail')
        print("mail", m)
        print("forget_mail", forget_mail)
        if m != None:
            # when user login
            re['user_record'] = duplicate_mail(m)
            print("re value",re['user_record'])
            if re['user_record'] != None:
                val = re['user_record']
                v = passowrd_set_or_not(val)
                print("value of v ",v)
                if v != 0: 
                    n = re['user_record']['image_name']
                    session['image'] = n
                    logged_email = m
                    logged_in = True
                    return redirect(url_for('userpassword'))
                else:
                    return render_template('login.html', error ="Your password is not set. Please click on forget password to set your password.")
            else:
                print("when record is none.")
                return render_template('login.html', error = "E-mail is not registered.Please register yourself.") 
        elif forget_mail != None:
            # when user enter email for forget password
            re['user_record'] = duplicate_mail(forget_mail)
            print("re value", re['user_record'])
            if re['user_record'] != None:
                mail_for_password(forget_mail)
                logged_email = forget_mail
                logged_in = True
                #check if mail is correct or not
                return redirect(url_for('confirmation_for_forget_password'))
            else:
                return render_template('login.html', err = "Not registered")
    return render_template('login.html')

@app.route('/confirmation')
def confirmation_for_forget_password():
    return render_template('confirmation_for_forget_password.html')

@app.route('/reset_password', methods=['GET','POST'])
def reset_password():
    global logged_email
    mail = logged_email
    print(mail)
    if request.method == 'POST':
        seq = request.form.get('seq')
        image = request.form.get('image')
        if image and seq and mail:
            image = get_image_name(image)
            print(mail, seq, image)
            val = insert_password(mail, seq, image)
            if val == "True":
                logged_in = True
                return redirect(url_for('login'))
        else :
            print("no data")
    return render_template('forget_pass.html')

@app.route('/userpass', methods=['GET','POST'])
def userpassword():
    global logged_email
    global logged_in
    img = session.get('image','None')
    path_of_image = get_image_path(img)
    if request.method == 'POST':
        m = logged_email
        se = request.form.get('seq')
        print("se",se)
        if se and m:
            print('mail', m)
            r = password_checker(m, se)
            print(r)
            if r == 1:
                logged_in = True
                print(logged_in)
                return redirect(url_for('main'))
            else:
                err = "Wrong Password"
                print(err)
                return redirect(url_for('userdash'))
        else:
            logged_in = False
            return redirect(url_for('about'))
        # return redirect(url_for('main'))
    else:
        print(path_of_image)
        return render_template('userpass.html', img_path = path_of_image)

# 


contents=""
@app.route('/main', methods=['GET','POST'])
def main():
    global content_detail
    global logged_in
    global logged_email
    mail = logged_email
    # mail = session('email_value',None)
    if request.method == 'POST':
        # print("under post")
        data = request.form.get('text')
        lines = request.form.get('lines')
        # print("post")
        # print(data)
        if data != None:
            if lines == None: 
                lines = str(13)  #temporary assigning here
            print(lines)
            session['lines'] = str(lines)
            content_detail = data
            rslt = insert_modified_content(mail, content_detail)
            # print(content_detail)
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
                if contents != None:
                    
                    result = insert_srecord(mail, contents)
                return render_template('main.html', content = contents)
            else:
                contents = extract_text('static\\uploaded_files\\' + filename)
                result = insert_srecord(mail, contents)
                return render_template('main.html', content = contents)
    else:
        print("value of logged_in",logged_in)
        if logged_in == True:
            contents=""
            return render_template('main.html', content=contents)
        else:
            print(logged_in)
            return render_template('login.html')

@app.route('/text_result' ,methods = ['GET', 'POST'])
def text_result():
    result = ""
    global content_detail
    global logged_email
    mail = logged_email
    if request.method == 'GET':
        data = content_detail
        lines = session.get('lines', None)
        print(lines)
        print("data", data)
        if data != "":
            if lines != None:
                lines = str(13)
            result = json.loads(summarize(data, lines))
            print(result)
            if result !=  "":
                # session['summary'] = result
                temp = insert_summary(mail, result['summary'])
                if temp == True:
                    return render_template('sum_result.html', results = result)
                else:
                    return render_template('main')
        else:
            print("result: data is empty")
            result = None
            return redirect(url_for('main'))
    else:
        print("result: Post")
        return redirect(url_for('main'))


@app.route('/userdash')
def userdash():
    return render_template('userdash.html')

@app.route('/useraccount')
def useraccount():
    return render_template('useraccount.html')

@app.route('/confpass')
def reg_confirm():
    return render_template('confpass.html')

@app.route('/')
def site():
    return render_template('index.html')

@app.route('/demo')
def demo():
    return render_template('checking.html')

@app.route('/adminlog', methods=['POST', 'GET'])
def admin():
    return render_template('adminlog.html')

@app.route('/dash')
def admin_dash():
    return render_template('admindash.html')

@app.route('/about', methods=['GET','POST'])
def about():
    return render_template('about.html')

if __name__ == "__main__":
    app.run(debug=True)