import os
import pymysql
import urllib.request
from app import app
from db import mysql
from flask import jsonify, request, session
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def home():
    if 'username' in session:
        username = session['username']
        return jsonify({'message': 'You are already logged in', 'username': username})
    else:
        resp = jsonify({'message': 'Unauthorized'})
        resp.status_code = 401
        return resp


@app.route('/login', methods=['POST'])
def login():
    conn = None;
    cursor = None;

    try:
        _json = request.json
        _username = _json['username']
        _password = _json['password']

        # validate the received values
        if _username and _password:
            # check user exists
            conn = mysql.connect()
            cursor = conn.cursor()

            sql = "SELECT * FROM application_users WHERE AppUser_UniqueID=%s"
            sql_where = (_username,)

            cursor.execute(sql, sql_where)
            row = cursor.fetchone()

            if row:
                if check_password_hash(row[9], _password):
                    session['username'] = row[6]
                    # cursor.close()
                    # conn.close()
                    return jsonify({'message': 'You are logged in successfully'})
                else:
                    resp = jsonify({'message': 'Bad Request - invalid password'})
                    resp.status_code = 400
                    return resp
        else:
            resp = jsonify({'message': 'Bad Request - invalid credendtials'})
            resp.status_code = 400
            return resp

    except Exception as e:
        print(e)

    finally:
        if cursor and conn:
            cursor.close()
            conn.close()


@app.route('/logout')
def logout():
    if 'username' in session:
        session.pop('username', None)
    return jsonify({'message': 'You successfully logged out'})



@app.route('/signup', methods=['POST'])
def signup():
    conn = None;
    cursor = None;
    # datetime object containing current date and time
    now = datetime.now()
    # YY-mm-dd H:M:S
    dt_string = now.strftime("%Y-%m-%d %H:%M:%S")

    try:
        _json = request.json
        _uniqueid = _json['uniqueid']
        _email = _json['email']
        _phone = _json['phone']
        _lastname = _json['lastname']
        _firstname = _json['firstname']
        _password = _json['password']
        _hashed_password = generate_password_hash(_password)

        # validate the received values
        if _email and _phone:
            # check user exists
            conn = mysql.connect()
            cursor = conn.cursor()

            sql = "SELECT * FROM application_users WHERE AppUser_Email=%s OR AppUser_Phone=%s"
            sql_where = (_email,_phone)

            cursor.execute(sql, sql_where)
            row = cursor.fetchone()

            if row:
                return jsonify({'message': 'Error! User already exist'})

            else:
                sql = "INSERT INTO application_users(AppUser_Firstname, AppUser_Lastname, AppUser_UniqueID, AppUser_Email, AppUser_Phone, AppUser_Password, AppUser_Joined) VALUES(%s, %s, %s,%s, %s, %s, %s)"
                sql_where = (_firstname, _lastname, _uniqueid, _email, _phone, _hashed_password, dt_string)
                cursor.execute(sql, sql_where)
                conn.commit()

                resp = jsonify({'message': 'Success! User successfully signed up'})
                resp.status_code = 401
                return resp

    except Exception as e:
        print(e)

    finally:
        if cursor and conn:
            cursor.close()
            conn.close()


if __name__ == "__main__":
    app.run(debug=True)