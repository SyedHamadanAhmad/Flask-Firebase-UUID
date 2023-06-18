import os
from flask import Flask, redirect, url_for, render_template, request, session, flash, jsonify
from datetime import timedelta, datetime
import pyrebase
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from sqlalchemy.orm import relationship
import pandas as pd
# import uuid
# from flask_migrate import Migrate

app = Flask(__name__)

config= {
    "apiKey": "AIzaSyCn8dMYxbT3_flp5M2mnNbywk-MaZiLH1Q",
    "authDomain": "test-project-b41ca.firebaseapp.com",
    "projectId": "test-project-b41ca",
    "storageBucket": "test-project-b41ca.appspot.com",
    "messagingSenderId": "337084528583",
    "appId": "1:337084528583:web:adbe0293fe720ccf3c8be2",
    "measurementId": "G-RM36F7YWSM",
    "databaseURL":""
       }
firebase=pyrebase.initialize_app(config)
auth=firebase.auth()


app.secret_key = "Avricus"
app.permanent_session_lifetime = timedelta(hours=5)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///iit3.db'  # Change the database URL as per your preference
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db = SQLAlchemy(app) 
# migrate = Migrate(app, db)




class IIT(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), default="NA")

class users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100))
    uuid = db.Column(db.String(28), nullable=False)
    password = db.Column(db.String(100))
    timestamp = db.Column(db.String(100))

    def __init__(self, name, email, uuid, password):
        self.name = name
        self.email = email
        self.uuid = uuid
        self.password = password
        self.timestamp = ""

    # def add_sign_up_timestamp(self):
    #     now=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    #     if self.timestamp:
    #             self.timestamp += f"CREATED ACCOUNT:, {now}"
            
    #     else:
    #         self.timestamp = now
    #     self.create_acc_logs_file()  # Update the logs file immediately after adding the timestamp
    
    
    def add_login_timestamp(self):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if self.timestamp:
            self.timestamp += f",{now}"
            
        else:
            self.timestamp = now
        self.update_logs_file()  # Update the logs file immediately after adding the timestamp

    def get_login_timestamps(self):
        return self.timestamp.split(",") if self.timestamp else []

    def update_logs_file(self):
        logs_file_path = os.path.join(os.path.dirname(__file__), "logs_final.txt")
        with open(logs_file_path, "a") as file:
            file.write(f"{self.name}: {self.get_login_timestamps()}\nEmail: {self.email}\n")

    # def create_acc_logs_file(self):
    #     logs_file_path = os.path.join(os.path.dirname(__file__), "logs_final.txt")
    #     with open(logs_file_path, "a") as file:
    #         file.write(f"{self.name}: {self.get_login_timestamps()}\nEmail: {self.email}\n")

class City(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

    def __init__(self, name):
        self.name = name


@app.route('/sign_up', methods=['POST', 'GET'])
def sign_up():
    if request.method == "POST":
        session.permanent =  True

        name=request.form['name']
        session['name']=name

        email = request.form['email']
        session['email']=email

        password=request.form['password']
        session['password']=password

        uuid=request.form["uuid"]
        session['uuid']=uuid

        found_user = users.query.filter_by(email = email).first()

        if found_user:
                session["uuid"] = found_user.uuid
        else: 
            # usr = users(user, "")
            # print("abcd")
            found_user = users(email=email, name=name, uuid=uuid, password=password)
            db.session.add(found_user)
            db.session.commit()
            found_user.add_sign_up_timestamp()
        return redirect(url_for("user"))
    else:
            if "user" in session:
                flash(f"You are already Logged In!!!")
                return render_template("sign_up.html")
        
       



@app.route("/home")
def home():
    return render_template("index.html", contents = "Testing")

@app.route("/view")
def view_logs():
    email = session.get("email", "")
    logs_file_path = os.path.join(app.root_path, "logs_final.txt")
    with open(logs_file_path, "r") as file:
        log_content = file.read()

    return render_template("view.html", log_content=log_content, email=email)

@app.route("/login", methods = ["POST", "GET"])
def login():
    if request.method == "POST":
      email=request.form['email']
      password=request.form['password']
      user=auth.sign_in_with_email_and_password(email, password)
      session['user']=email
      found_user=users.query.filter_by(email=email).first()
      found_user.add_login_timestamp()

      return redirect(url_for("home"))
    
    else:
        return render_template("login.html")
      
     
         
    

@app.route("/user", methods=["POST", "GET"])
def user():
    email = None
    if "user" in session:
        user = session["user"]

        if request.method == "POST":
            email = request.form["email"]
            session["email"] = email
            found_user = users.query.filter_by(name=user).first()
            found_user.email = email
            db.session.commit()
            flash("Email was saved!!!")
        else:
            if "email" in session:
                email = session["email"]

        return render_template("sign_up.html")
    else:
        # flash(f"You are not logged in!!!")
        return redirect(url_for("login"))

@app.route("/logout")
def logout():
    if "user" in session:
        user = session["user"]
        flash(f"You have been logged out, {user}", "info")
    else:
        flash(f"You are not logged in!!! LOGIN First :)", "info")
    session.pop("user", None)
    session.pop("email", None)
    return redirect(url_for("login"))

@app.route('/')
def iit_list():
    if "user" in session:
        iits = IIT.query.all()
        return render_template("iit_table.html", iits = iits)
    else:
        flash(f"You are not logged in!!!")
        return redirect(url_for("login"))


@app.route("/college/<int:num>")
def dynamicRoute(num):
    if "user" in session:
        iit = IIT.query.filter_by(id=num).first()
        if iit:
            return render_template("IndiCol.html", iits=iit)
        else:
            flash(f"We dont have this College in our database!!!")
            return render_template("error.html", error_message="Page not found", back_url=url_for("iit_list"))
    else:
        flash(f"You are not logged in!!!")
        return redirect(url_for("login")) 

@app.errorhandler(404)
def page_not_found(error):
    
    return render_template('error.html', error_message="Page not found", back_url=url_for('iit_list')), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template("error.html", error_message="Internal Server Error", back_url=url_for("iit_list")), 500

@app.route("/addCollege")
def addCollege():
    states = City.query.all()
    return render_template("addCdata.html", states=states)


@app.route("/add_college", methods=["POST"])
def add_college():
    if "user" in session:
        if request.method == "POST":
            college_name = request.form["college_name"]
            college_location = request.form["location"]
            

            if college_location:
                # Use the selected city from the dropdown
                location = college_location
            else:
                # No location specified
                location = None

            existing_college = IIT.query.filter(func.lower(func.replace(IIT.name, ' ', '')) == func.lower(func.replace(college_name, ' ', ''))).first()
            if existing_college:
                existing_college.location = location
                db.session.commit()
            else:
                iit = IIT(name=college_name, location=location)
                db.session.add(iit)
                db.session.commit()

            flash("College added/updated successfully!")
            return redirect(url_for("iit_list"))
    else:
        flash("You are not logged in!")
        return redirect(url_for("login"))




@app.route("/populate_cities")
def populate_cities():
    existing_states = City.query.all()

    df = pd.read_excel("C:/Users/ashmi/OneDrive/Desktop/Avricus PS1/Flask/cities/states.xlsx")
    states = df["State"].tolist()

    # Remove existing states from the database
    for state in existing_states:
        db.session.delete(state)

    # Add the new states
    for state in states:
        db.session.add(City(name=state))

    db.session.commit()
    flash("States updated successfully!")
    return redirect(url_for("addCollege"))



if __name__ == "__main__":
   
    with app.app_context():
        db.create_all()

    app.run(debug=True)