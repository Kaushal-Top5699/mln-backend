from flask import Flask, flash, render_template, request, redirect, url_for, session, g, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from flask_migrate import Migrate
from flask_login import UserMixin, login_user, LoginManager, login_required,logout_user, current_user
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from flask_wtf.csrf import CSRFProtect
from flask_bcrypt import Bcrypt
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool
from math import ceil
from pathlib import Path
import re
import json
import os
import subprocess
from routes import mln
import uuid
import shutil

from utils import response

app = Flask(__name__,'/static')
CORS(app, supports_credentials=True, origins="*")

app.config['SESSION_COOKIE_SAMESITE'] = "None"
app.config['SESSION_COOKIE_SECURE'] = True

BASE_URL='/mlndash-test'
USERS_DIRECTORY='./users'
DIRECTORY_CONFIG_FILE='./directory_config.cfg'
app.register_blueprint(mln)
bcrypt=Bcrypt(app)


import os

# ...

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), 'database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS']={'connect_args':{'check_same_thread':False,'timeout':30}}
app.config['SECRET_KEY']='ameysecretkey'
app.config['WTF_CSRF_ENABLED'] = False
db = SQLAlchemy(app)
migrate=Migrate(app,db)
csrf = CSRFProtect(app)


# with app.app_context():
#    db.init_app(app)

# @app.before_request
# def before_request():
#    g.db=db.session

# @app.teardown_request
# def teardown_request(exception):
#    db.session.remove()

app.app_context().push()
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer,primary_key=True)
    username = db.Column(db.String(20),nullable=False,unique=True)
    password = db.Column(db.String(80),nullable=False)
    name = db.Column(db.String(80),nullable=False)
    email = db.Column(db.String(80),nullable=False,unique=True)
    phNumber = db.Column(db.String(10),nullable=True)
    userpath=db.Column(db.String(300),nullable=True)
    def getUsername(self):
        return self.username


class RegisterForm(FlaskForm):
    username=StringField(validators=[InputRequired(),Length(min=4,max=20)],render_kw={"placeholder":"Username"})
    password=PasswordField(validators=[InputRequired(),Length(min=4,max=8)],render_kw={"placeholder":"Password"})
    email=StringField(validators=[InputRequired(),Length(min=4,max=80)],render_kw={"placeholder":"E-mail"})
    phNumber=StringField(validators=[Length(min=0,max=10)],render_kw={"placeholder":"Phone Number"})
    name=StringField(validators=[InputRequired(),Length(min=4,max=80)],render_kw={"placeholder":"Full Name"})
    submit=SubmitField("Register")

    def validate_username(self,username):
        existing_user_username=User.query.filter_by(
            username=username.data).first()
        if existing_user_username:
            raise ValidationError(
                "That username already exists. Please choose a different one."
            )
        

class LoginForm(FlaskForm):
    
    password=PasswordField(validators=[InputRequired(),Length(min=4,max=8)],render_kw={"placeholder":"Password"})
    username=StringField(validators=[InputRequired(),Length(min=4,max=20)],render_kw={"placeholder":"Username"})
    submit=SubmitField("Login")



#@app.route(BASE_URL+'/', methods=["POST","GET"])
#def landing():
    #form=LoginForm()
    #return render_template("landing.html",form=form,BASE_URL=BASE_URL)

# Field validation patterns

NAME_MATCHER = re.compile(r".{4,}")
USERNAME_MATCHER = re.compile(r"\w{4,}", re.IGNORECASE)
EMAIL_MATCHER = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b")
PASSWORD_MATCHER = re.compile(r"[^ ].{5,}")
PHONE_NUMBER_MATCHER = re.compile(r"^(\+\d{1,3})?\s?\(?\d{1,4}\)?[\s.-]?\d{3}[\s.-]?\d{4}$", re.IGNORECASE)

ENTITIES_MAPPING = {
    "stream": {
        "stored_path": "Streams",
        "file_name_field": "streamName",
        "extension": "str",
    },
    "enum": {
        "stored_path": "Enums",
        "file_name_field": "enumName",
        "extension": "enum",
    },
    "query": {
        "stored_path": "Queries",
        "file_name_field": "queryName",
        "extension": "qry",
    },
}

# Auth routes

@login_manager.unauthorized_handler
def unauth_handler():
    return response(
        "Unauthorized access is denied",
        code="unauthorized",
    ), 401

@app.route(BASE_URL+'/', methods=["POST","GET"])
@app.route(BASE_URL, methods=["POST","GET"])
@app.route(BASE_URL+'/login', methods=["POST","GET"])
def login():
    try:
        print("Code has been updated")
        # form = LoginForm()
        print("Came inside Login")

        data = request.get_json()
        username = data.get("username")
        password = data.get("password")

        if username is None:
            return response(
                "Username is required",
                code="username-required",
            ), 400
        if USERNAME_MATCHER.fullmatch(username) is None:
            return response(
                "Username is invalid",
                code="username-invalid",
            ), 400
        
        if password is None:
            return response(
                "Password is required",
                code="password-required",
            ), 400
        if PASSWORD_MATCHER.fullmatch(password) is None:
            return response(
                "Password is invalid",
                code="password-invalid",
            ), 400

        if request.method=='POST':
            user = User.query.filter_by(username=username).first()
            if user:
                if bcrypt.check_password_hash(user.password, password):
                    login_user(user)
                    # session['user_id']=user.id
                    # session['userpath']=user.userpath
                    # return redirect(url_for('mln.dashboard',user=user.username))
                    session_id=str(uuid.uuid4())
                    session[f'userpath_{session_id}'] = user.userpath
                    session[f'mainpath_{session_id}'] = user.userpath
                    session[f'username_{session_id}']=user.username
                    session[f'ph_{session_id}']=user.phNumber
                    session[f'email_{session_id}']=user.email
                    session[f'name_{session_id}']=user.name
                    session[f'showpath_{session_id}']=session[f'userpath_{session_id}'][session[f'userpath_{session_id}'].index(user.username):]
                    # return redirect(url_for('mln.dashboard',user=session[f'username_{session_id}'],sesid=session_id))

                    return response(
                        "Logged in successfully",
                        data={
                            "username": session[f"username_{session_id}"],
                            "session_id": session_id,
                        },
                    )
                else:
                    # flash(f"Wrong password.",'error')
                    return response(
                        "Wrong password",
                        code="wrong-password",
                    ), 403
                    # return render_template("login.html",form=form,BASE_URL=BASE_URL)
            else:
                # flash(f"User does not exist.",'error')
                return response(
                    "User does not exist.",
                    code="user-not-found",
                ), 404
                # return render_template("login.html",form=form,BASE_URL=BASE_URL)
        # elif request.method=='POST':
        #     for field, errors in form.errors.items():
        #         flash(f"Error in {field.name}: {', '.join(errors)}",'error')
        #     return render_template("login.html",form=form,BASE_URL=BASE_URL)

        return response("No action")
        # return render_template("login.html",form=form,BASE_URL=BASE_URL)
    except Exception as e:
        print(e)
        return response(
            "Unknown error occurred",
            code="internal-error",
        ), 500

@app.route(BASE_URL+'/register',methods=["POST","GET"]) 
def register():
    try:
        # form = RegisterForm()
        # print(form.name.data)
        # print(form.validate_on_submit())

        data = request.get_json()
        name = data.get("name")
        username = data.get("username")
        email = data.get("email")
        phone_number = data.get("phone_number")
        password = data.get("password")

        if name is None:
            return response(
                "Full name is required",
                code="full-name-required",
            ), 400
        if NAME_MATCHER.fullmatch(name) is None:
            return response(
                "Full Name is invalid",
                code="full-name-invalid",
            ), 400
        
        if username is None:
            return response(
                "Username is required",
                code="username-required",
            ), 400
        if USERNAME_MATCHER.fullmatch(username) is None:
            return response(
                "Username is invalid",
                code="username-invalid",
            ), 400
        
        if email is None:
            return response(
                "Email address is required",
                code="email-required",
            ), 400
        if EMAIL_MATCHER.fullmatch(email) is None:
            return response(
                "Email address is invalid",
                code="email-invalid",
            ), 400
        
        if phone_number is not None and PHONE_NUMBER_MATCHER.fullmatch(phone_number) is None:
            return response(
                "Phone number is invalid",
                code="phone-number-invalid",
            ), 400
        
        if password is None:
            return response(
                "Password is required",
                code="password-required",
            ), 400
        if PASSWORD_MATCHER.fullmatch(password) is None:
            return response(
                "Password must begin with a non-whitespace character and must be atleast 6 characters long",
                code="password-invalid",
            ), 400

        if User.query.filter((User.username == username) | (User.email == email)).first():
            return response(
                "Email/username is already taken",
                code="email-or-username-taken",
            ), 400

        # if form.validate_on_submit():
        #     print('inside')
        #     hashed_password = bcrypt.generate_password_hash(form.password.data)
        #     new_user = User(username=form.username.data,password=hashed_password,name=form.name.data,phNumber=form.phNumber.data,email=form.email.data,userpath=USERS_DIRECTORY+'/'+str(form.username.data))
        #     db.session.add(new_user)
        #     db.session.commit()
        #     os.mkdir(os.path.join(USERS_DIRECTORY,form.username.data),mode=0o777)
        #     os.chmod(os.path.join(USERS_DIRECTORY,form.username.data),mode=0o777)
        #     with open(DIRECTORY_CONFIG_FILE,'r') as file:
        #         directory_path=file.readline().strip()
        #     subprocess.check_output('cp -Rp '+directory_path+'* '+USERS_DIRECTORY+'/'+form.username.data+'/',shell=True)
        print('inside')
        hashed_password = bcrypt.generate_password_hash(password)
        new_user = User(username=username,password=hashed_password,name=name,phNumber=phone_number,email=email,userpath=USERS_DIRECTORY+'/'+str(username))
        db.session.add(new_user)
        db.session.commit()
        os.mkdir(os.path.join(USERS_DIRECTORY, username),mode=0o777)
        os.chmod(os.path.join(USERS_DIRECTORY, username),mode=0o777)
        with open(DIRECTORY_CONFIG_FILE,'r') as file:
            directory_path=file.readline().strip()
        subprocess.check_output('cp -Rp '+directory_path+'* '+USERS_DIRECTORY+'/'+username+'/',shell=True)
            
        return response("Registered successfully"), 201
        # return redirect(url_for('login'))
        # elif request.method=='POST':
        #     for field, errors in form.errors.items():
        #         flash(f"Error in {field}: {', '.join(errors)}",'error')
        #     return render_template("register.html",form=form,BASE_URL=BASE_URL)
        # return render_template("register.html",form=form,BASE_URL=BASE_URL)
    except Exception as e:
        print(e)
        return response(
            "Unknown error occurred",
            code="internal-exception",
        ), 500

@app.route(BASE_URL+"/authtest", methods=["GET"])
@login_required
def authtest():
    return response("You are logged in")

@app.route(BASE_URL+"/user-profile/<sid>", methods=["GET"])
@login_required
def get_profile(sid):
    try:
        NAME = session[f'name_{sid}']
        USERNAME = session[f'username_{sid}']
        EMAIL_ID = session[f'email_{sid}']
        PHONE_NO = session[f'ph_{sid}']

        return response(
            "Profile fetched successfully",
            data={
                "name": NAME,
                "username": USERNAME,
                "email_id": EMAIL_ID,
                "phone_no": PHONE_NO,
            }
        )
    except Exception as e:
        print(e)
        return response(
            "Unknown error occurred",
            code="internal-error"
        ), 500

@app.route(BASE_URL+'/delete',methods=["POST","GET"])
@login_required
def deletepage():
    try:
        sid=request.args.get('sid')
        if sid is None:
            return response(
                "Session Id is required",
                code="sid-required",
            ), 400

        shutil.rmtree(session[f'mainpath_{sid}'],ignore_errors=False)
        User.query.filter_by(username=session[f'username_{sid}']).delete()
        db.session.commit()
        
        return response("Account deleted successfully")
    except Exception as e:
        print(e)
        return response(
            "Unknown error occurred",
            code="internal-error",
        ), 500

# Directory routes

@app.route(BASE_URL+'/listdr/<sid>', methods=["GET"])
@login_required
def listdr(sid):
    try:
        cwd = session[f"userpath_{sid}"]
        file_list = [{ "dir": dir, "is_file": os.path.isfile(os.path.join(cwd, dir)) } for dir in os.listdir(cwd)]
        return response(
            "List retrieved successfully",
            data={
                "cwd": cwd,
                "list": file_list
            }
        )
    except Exception as e:
        print(e)
        return response(
            "Unknown error occurred",
            code="internal-error",
        ), 500

@app.route(BASE_URL+"/createdr/<folder_name>/<sid>", methods=["POST"])
@login_required
def createdr(folder_name, sid):
    try:
        path = os.path.join(session[f"userpath_{sid}"], folder_name)
        if os.path.exists(path):
            return response(
                "Path already exists",
                code="path-already-exists",
            ), 400
        
        os.mkdir(path)
        return response(f"Folder \"{folder_name}\" created successfully"), 201
    except Exception as e:
        print(e)
        return response(
            "Unknown error occurred",
            code="internal-error",
        ), 500

@login_required
@app.route(BASE_URL+'/changedr/<folder_name>/<sid>',methods=['GET','POST'])
def changedr(folder_name,sid):
    try:
        folder=folder_name
        print(folder_name)
        #current_working=os.path.join(session.get('userpath'),folder)
        current_working=os.path.join(session[f'userpath_{sid}'],folder)
        if not os.path.exists(current_working):
            return response(
                "Path does not exist",
                code="path-not-found",
            ), 404
        
        print("current_working :",current_working)
        session[f'userpath_{sid}']=current_working
        print("cdr ",session[f'userpath_{sid}'])

        return response(
            f"Navigated to \"{folder_name}\"",
            data={ "cwd": current_working }
        )
        # return redirect(url_for('mln.folder',folder_name=folder,sid=sid))
    except Exception as e:
        print(e)
        return response(
            "Unknown error occurred",
            code="internal-error",
        ), 500

@login_required
@app.route(BASE_URL+'/back/<sid>',methods=['GET','POST'])
def back(sid):
    try:
        if session[f"userpath_{sid}"].count("/") <= 2:
            return response(
                "Cannot level-up beyond user root",
                code="already-on-user-root",
            ), 403

        current_working=os.path.dirname(session[f'userpath_{sid}'])
        session[f'userpath_{sid}']=current_working
        print(session[f"userpath_{sid}"])
        folder=session[f'userpath_{sid}'].split("/")[-1]

        return response(
            "Navigated to parent directory",
            data={ "cwd": current_working }
        )
        # return redirect(url_for('mln.folder',folder_name=folder,sid=sid))
    except Exception as e:
        print(e)
        return response(
            "Unknown error occurred",
            code="internal-error",
        ), 500

# File routes

@app.route(BASE_URL+"/filecontent", methods=["GET"])
@login_required
def file_content():
    try:
        print("Inside View : ", os.getcwd())

        sid = request.args.get('sid')
        file_name = request.args.get("file")

        if sid is None:
            return response(
                "Session Id is required",
                code="sid-required",
            ), 400
        if file_name is None:
            return response(
                "File name is required",
                code="file-name-required",
            ), 400

        current_working = session[f'userpath_{sid}']
        FILENAME = os.path.join(current_working, file_name)

        if not os.path.exists(FILENAME) or not os.path.isfile(FILENAME):
            return response(
                "Specified path does not exist or is not a valid file",
                code="invalid-path",
            ), 400

        x = Path(FILENAME).read_text()
        # x = '<font size="+2"><strong>Selected File Content</strong></font><br>------------------------------------------------------------<br>'+x
        print("came till log output")
        log_window_output = "None"
        user = request.args.get('user')
        filename = request.args.get('file')
        # form = UploadFileForm()
        # if form.validate_on_submit():
        #     file = form.file.data
        #     print(type(file))
        #     file.save(os.path.join(session.get(
        #         f'userpath_{sid}'), secure_filename(file.filename)))
        # showpath = session.get(f'userpath_{sid}')[
        #     session.get(f'userpath_{sid}').index(user):]
        options = ['a', 'b']
        print("checking the extension")

        alert_message = None
        if('.gen' in FILENAME):
            alert_message = 'This is a generation config file. Click on <span style="color:#FFD900;">Generate Layers</span> to start generation.'
        elif('.ana' in FILENAME):
            alert_message = 'This is an analysis config file. Click on <span style="color:#FFD900;">Analyze Layers</span> to start analyzing.'
        elif('.net' in FILENAME):
            alert_message = 'Select an option from the <span style="color:#FFD900;">Visualize</span> dropdown to see a visualization for this file.'
        elif('.ecom' in FILENAME):
            alert_message = 'This is an edge community file. Select an option from the <span style="color:#FFD900;">Visualize</span> dropdown to see a visualization for this file.'
        elif('.vcom' in FILENAME):
            alert_message = 'This is a vertex community file. Select an option from the <span style="color:#FFD900;">Visualize</span> dropdown to see a visualization for this file.'
        
        return response(
            "Fetched file content successfully",
            data={
                "file_content": x,
                "filename": filename,
                "alert_message": alert_message,
                "user": user,
                "options": options,
                "cwd": current_working,
                "file_list": os.listdir(current_working),
                "log": log_window_output,
                "mainpage": session.get(f'mainpath_{sid}'),
            }
        )
        # return render_template('dashboard3.html', us=user, options=options, current_working_directory=current_working,
        #                        file_list=os.listdir(current_working), log=log_window_output, showpath=showpath, file_output=x, filen=filename, BASE_URL=BASE_URL, sid=sid, mp=session.get(f'mainpath_{sid}'), form=form, current_page=page, total_pages=total_pages)
    except Exception as e:
        print(e)
        user = request.args.get('user')
        sid = request.args.get('sid')

        return response(
            "Unknown error occurred",
            code="internal-error"
        ), 500
        # flash("Some error occurred", 'error')
        # return redirect(url_for('mln.dashboard', user=user, sesid=sid))

@app.route(BASE_URL+"/files/entities", methods=["POST", "PATCH"])
@login_required
def create_or_update_entities():
    try:
        if request.method == "POST":
            sid = request.args.get("sid")
            if sid is None:
                return response(
                    "Session Id is required",
                    code="sid-required",
                ), 400

            data = request.get_json()
            entities = data.get("entities")
            if entities is None:
                return response(
                    "Entities is required",
                    code="entities-required",
                ), 400

            '''
            entities_dict = {
                <filename>: {
                    file_name: <filename_with_extension>,
                    entity: <entity_body>
                }
            }
            '''
            entities_dict = {}
            for entity in entities:
                if entity["kind"] not in ENTITIES_MAPPING.keys():
                    return response(
                        f"Entity kind \"{entity['kind']}\" is invalid",
                        code="entity-kind-invalid",
                    ), 400
                entity_meta_info = ENTITIES_MAPPING[entity["kind"]]
                for child in entity["children"]:
                    entities_dict[child[entity_meta_info["file_name_field"]]] = {
                        "stored_path": ENTITIES_MAPPING[entity["kind"]]["stored_path"],
                        "file_name": f"{child[entity_meta_info['file_name_field']]}.{entity_meta_info['extension']}",
                        "entity": child,
                    }
            
            # Create entity dirs if not present
            for entity in entities_dict.values():
                entity_path = os.path.join(session[f"mainpath_{sid}"], entity["stored_path"])
                if not os.path.exists(entity_path):
                    os.mkdir(entity_path)
            
            # Check if the entity names are unique
            for entity_name, entity in entities_dict.items():
                path = os.path.join(session[f"mainpath_{sid}"], entity["stored_path"], entity["file_name"])
                if os.path.exists(path) and os.path.isfile(path):
                    return response(
                        f"Another entity with the name \"{entity_name}\" already exists",
                        code="entity-name-taken",
                    ), 400
            
            for entity_name, entity in entities_dict.items():
                with open(os.path.join(session[f"mainpath_{sid}"], entity["stored_path"], entity["file_name"]), "w") as f:
                    json.dump(entity["entity"], f, indent=4)
            
            return response("Entities created successfully"), 201
        elif request.method == "PATCH":
            sid = request.args.get("sid")
            if sid is None:
                return response(
                    "Session Id is required",
                    code="sid-required",
                ), 400

            data = request.get_json()
            entities = data.get("entities")
            if entities is None:
                return response(
                    "Entities is required",
                    code="entities-required",
                ), 400

            '''
            entities_dict = {
                <filename>: {
                    file_name: <filename_with_extension>,
                    entity: <entity_body>
                }
            }
            '''
            entities_dict = {}
            for entity in entities:
                if entity["kind"] not in ENTITIES_MAPPING.keys():
                    return response(
                        f"Entity kind \"{entity['kind']}\" is invalid",
                        code="entity-kind-invalid",
                    ), 400
                entity_meta_info = ENTITIES_MAPPING[entity["kind"]]
                for child in entity["children"]:
                    entities_dict[child[entity_meta_info["file_name_field"]]] = {
                        "stored_path": ENTITIES_MAPPING[entity["kind"]]["stored_path"],
                        "file_name": f"{child[entity_meta_info['file_name_field']]}.{entity_meta_info['extension']}",
                        "entity": child,
                    }
            
            # Create entity dirs if not present
            for entity in entities_dict.values():
                entity_path = os.path.join(session[f"mainpath_{sid}"], entity["stored_path"])
                if not os.path.exists(entity_path):
                    os.mkdir(entity_path)
            
            # Check if the entity names are unique
            # for entity_name, entity in entities_dict.items():
            #     path = os.path.join(session[f"mainpath_{sid}"], entity["stored_path"], entity["file_name"])
            #     if os.path.exists(path) and os.path.isfile(path):
            #         return response(
            #             f"Another entity with the name \"{entity_name}\" already exists",
            #             code="entity-name-taken",
            #         ), 400
            
            for entity_name, entity in entities_dict.items():
                with open(os.path.join(session[f"mainpath_{sid}"], entity["stored_path"], entity["file_name"]), "w") as f:
                    json.dump(entity["entity"], f, indent=4)
            
            return response("Entities created successfully"), 201
    except Exception as e:
        print(e)
        return response(
            "Unknown error occurred",
            code="internal-error",
        ), 500

@app.route(BASE_URL+"/files/streams", methods=["GET"])
@login_required
def get_streams():
    try:
        sid = request.args.get("sid")
        if sid is None:
            return response(
                "Session Id is required",
                code="sid-required",
            ), 400

        streams_path = os.path.join(session[f"mainpath_{sid}"], ENTITIES_MAPPING["stream"]["stored_path"])
        if not os.path.exists(streams_path):
            os.mkdir(streams_path)
            return response(
                "No streams present at the moment",
                data={ "streams": [] }
            )
        
        streams = []
        stream_files = [ file for file in os.listdir(streams_path) if file.endswith(".str") ]
        for stream_file in stream_files:
            content = json.loads(Path(os.path.join(streams_path, stream_file)).read_text())
            streams.append(content)
        
        return response(
            "Streams fetched successfully",
            data={ "streams": streams },
        )
    except Exception as e:
        print(e)
        return response(
            "Unknown error occurred",
            code="internal-error",
        ), 500

@app.route(BASE_URL+"/files/enums", methods=["GET"])
@login_required
def get_enums():
    try:
        sid = request.args.get("sid")
        if sid is None:
            return response(
                "Session Id is required",
                code="sid-required",
            ), 400

        enums_path = os.path.join(session[f"mainpath_{sid}"], ENTITIES_MAPPING["enum"]["stored_path"])
        if not os.path.exists(enums_path):
            os.mkdir(enums_path)
            return response(
                "No enums present at the moment",
                data={ "enums": [] }
            )
        
        enums = []
        enum_files = [ file for file in os.listdir(enums_path) if file.endswith(f".{ENTITIES_MAPPING['enum']['extension']}") ]
        for enum_file in enum_files:
            content = json.loads(Path(os.path.join(enums_path, enum_file)).read_text())
            enums.append(content)
        
        return response(
            "Enums fetched successfully",
            data={ "enums": enums },
        )
    except Exception as e:
        print(e)
        return response(
            "Unknown error occurred",
            code="internal-error",
        ), 500
    
@app.route(BASE_URL+"/files/queries", methods=["GET"])
@login_required
def get_queries():
    try:
        sid = request.args.get("sid")
        if sid is None:
            return response(
                "Session Id is required",
                code="sid-required",
            ), 400

        queries_path = os.path.join(session[f"mainpath_{sid}"], ENTITIES_MAPPING["query"]["stored_path"])
        if not os.path.exists(queries_path):
            os.mkdir(queries_path)
            return response(
                "No queries present at the moment",
                data={ "queries": [] }
            )
        
        queries = []
        query_files = [ file for file in os.listdir(queries_path) if file.endswith(".json") ]
        for query_file in query_files:
            content = json.loads(Path(os.path.join(queries_path, query_file)).read_text())
            queries.append(content)
        
        return response(
            "Queries fetched successfully",
            data={ "queries": queries },
        )
    except Exception as e:
        print(e)
        return response(
            "Unknown error occurred",
            code="internal-error",
        ), 500

@app.route(BASE_URL+"/files/<file_name>", methods=["DELETE"])
@login_required
def delete_file(file_name):
    try:
        sid = request.args.get("sid")
        if sid is None:
            return response(
                "Session Id is required",
                code="sid-required",
            ), 400
        
        # Check if the stream exists
        path = os.path.join(session[f"userpath_{sid}"], f"{file_name}")
        if not os.path.exists(path) or not os.path.isfile(path):
            return response(
                "Specified path is invalid or not a file",
                code="path-invalid",
            ), 404
        
        # Delete stream file
        os.unlink(path)

        return response(f"File \"{file_name}\" deleted successfully")
    except Exception as e:
        print(e)
        return response(
            "Unknown error occurred",
            code="internal-error",
        ), 500

# app.register_blueprint( mln )
with app.app_context():
    db.create_all()

if __name__ == "__main__":
   app.run(port=3001)

