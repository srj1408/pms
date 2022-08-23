from flask import Flask, request, session, redirect, url_for, render_template, flash
import psycopg2
import psycopg2.extras
from werkzeug.security import generate_password_hash, check_password_hash
import boto3

app = Flask(__name__)
app.secret_key = 'suraj-Agrawal'

DB_HOST = "localhost"
DB_NAME = "postgres"
DB_USER = "postgres"
DB_PASS = "Specs@123"

conn = psycopg2.connect(dbname = DB_NAME, user = DB_USER, password = DB_PASS, host = DB_HOST)

@app.route('/', methods=['GET'])
def home():
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    if 'loggedin' in session:

        app.config['S3_BUCKET'] = ""
        app.config['S3_KEY'] = ""
        app.config['S3_SECRET'] = ""
        app.config['S3_LOCATION'] = ''
        s3 = boto3.client("s3",aws_access_key_id=app.config['S3_KEY'], aws_secret_access_key=app.config['S3_SECRET']) 
        payslips1 = s3.list_objects_v2(Bucket=app.config['S3_BUCKET'])
        user_id = session['id']
        cursor.execute("TRUNCATE TABLE payslip")
        for payslip in (payslips1['Contents']):
            cursor.execute("INSERT INTO payslip(user_id,name,date) VALUES(%s,%s,%s)",(user_id,payslip['Key'],payslip['LastModified']))
            s3.download_file(Bucket=app.config['S3_BUCKET'],Key=payslip['Key'],Filename=payslip['Key'])
        cursor.execute("select * from payslip order by date")
        payslips = cursor.fetchall()
        conn.commit()
        return render_template('home.html',payslips=payslips)
    return redirect(url_for('login'))

@app.route('/login/', methods=['GET','POST'])
def login():
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']

        cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
        account = cursor.fetchone()
        if account: 
            password_rs = account['password']
            _hashed_password = generate_password_hash(password_rs)
            print(_hashed_password)
            print(password)
            if check_password_hash(_hashed_password, password):
                session['loggedin'] = True
                session['id'] = account['id']
                session['username'] = account['username']
                return redirect(url_for('home'))
            else:
                flash('Incorrect username or password')
        else:
            flash('Incorrect username or password')

    return render_template('login.html')

if __name__ == "__main__":
    app.run(debug=True)
