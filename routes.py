from flask import Flask, render_template, request, render_template_string, redirect, url_for, Blueprint, session, send_file, flash
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from wtforms import StringField, PasswordField, SubmitField, FileField
from wtforms.validators import InputRequired, Length, ValidationError
from flask_bcrypt import Bcrypt
from werkzeug.utils import secure_filename
from math import ceil
import os
import multiprocessing
import subprocess
import sys
import bleach
import re

from utils import response

BASE_URL = '/mlndash-test'

mln = Blueprint('mln', __name__, url_prefix=BASE_URL)


class UploadFileForm(FlaskForm):
    file = FileField("File")
    submit = SubmitField("Upload File")


original = os.path.dirname(os.path.abspath(__file__))
current_working = original


@mln.route('/dashboard/<user>/<sesid>', methods=["POST", "GET"])
@login_required
def dashboard(user, sesid):
    form = UploadFileForm()
    if form.validate_on_submit():
        file = form.file.data
        if(file == None):
            pass
        else:
            file.save(os.path.join(session.get(
                f'userpath_{sesid}'), secure_filename(file.filename)))
    showpath = session.get(f'showpath_{sesid}')
    options = ['Option 1', 'Option 2', 'Option 3']
    return render_template('dashboard3.html', us=user, options=options, current_working_directory=session.get(f'userpath_{sesid}'), showpath=showpath, file_list=os.listdir(session.get(f'userpath_{sesid}')), BASE_URL=BASE_URL, filen=" ", sid=sesid, mp=session.get(f'mainpath_{sesid}'), form=form)


@mln.route('/home/<user>/<sesid>', methods=["POST", "GET"])
@login_required
def home(user, sesid):
    form = UploadFileForm()
    if form.validate_on_submit():
        file = form.file.data
        if(file == None):
            pass
        else:
            file.save(os.path.join(session.get(
                f'userpath_{sesid}'), secure_filename(file.filename)))
    showpath = session.get(f'mainpath_{sesid}')[
        session.get(f'mainpath_{sesid}').index(user):]
    session[f'showpath_{sesid}'] = showpath
    session[f'userpath_{sesid}'] = session.get(f'mainpath_{sesid}')
    options = ['Option 1', 'Option 2', 'Option 3']
    return render_template('dashboard3.html', us=user, options=options, current_working_directory=session.get(f'mainpath_{sesid}'), showpath=showpath, file_list=os.listdir(session.get(f'mainpath_{sesid}')), BASE_URL=BASE_URL, filen=" ", sid=sesid, mp=session.get(f'mainpath_{sesid}'), form=form)


@mln.route('/logout', methods=["POST", "GET"])
@login_required
def logout():
    sid = request.args.get('sid')
    if sid is None:
        return response(
            "Session Id is required",
            code="sid-required",
        ), 400

    session.pop(session[f'username_{sid}'], None)
    logout_user()

    return response("Successfully logged out")
    # return redirect(url_for('login'))


@login_required
@mln.route('/cd')
def cd():
    folder_name = request.args.get('folder')
    sid = request.args.get('sid')
    print("before change: ", current_working)
    return redirect(url_for('changedr', folder_name=folder_name, sid=sid))


@login_required
@mln.route('/folder/<folder_name>/<sid>', methods=['POST', 'GET'])
def folder(folder_name, sid):
    foldern = folder_name
    user = session[f'username_{sid}']
    cwd = session[f'userpath_{sid}']
    form = UploadFileForm()
    if form.validate_on_submit():
        file = form.file.data
        if(file == None):
            pass
        else:
            file.save(os.path.join(session.get(
                f'userpath_{sid}'), secure_filename(file.filename)))
    fl = os.listdir(cwd)
    showpath = session.get(f'userpath_{sid}')[
        session.get(f'userpath_{sid}').index(user):]
    session[f'showpath_{sid}'] = showpath
    return render_template('dashboard3.html', us=user, current_working_directory=cwd,
                           file_list=fl, showpath=session[f'showpath_{sid}'], BASE_URL=BASE_URL, filen=' ', sid=sid, mp=session.get(f'mainpath_{sid}'), form=form)


@login_required
@mln.route('/back')
def goback():
    sid = request.args.get('sid')
    folder_name = session[f'userpath_{sid}'].split("/")[-1]
    return redirect(url_for('back', folder_name=folder_name, sid=sid))


@login_required
@mln.route('/view', methods=['POST', 'GET'])
def view():
    try:
        print("Inside View : ", os.getcwd())
        sid = request.args.get('sid')
        current_working = session[f'userpath_{sid}']
        FILENAME = os.path.join(current_working, request.args.get('file'))
        page = int(request.args.get('page', 1))
        start_line = (page - 1) * 20
        end_line = start_line + 20

        with open(FILENAME, 'r') as file:
            all_lines = file.readlines()
            total_pages = ceil(len(all_lines) / 20)
            lines_to_display = all_lines[start_line:end_line]
        x = '<br>'.join(lines_to_display)
        x = '<font size="+2"><strong>Selected File Content</strong></font><br>------------------------------------------------------------<br>'+x
        print("came till log output")
        log_window_output = "None"
        user = request.args.get('user')
        filename = request.args.get('file')
        form = UploadFileForm()
        if form.validate_on_submit():
            file = form.file.data
            print(type(file))
            file.save(os.path.join(session.get(
                f'userpath_{sid}'), secure_filename(file.filename)))
        showpath = session.get(f'userpath_{sid}')[
            session.get(f'userpath_{sid}').index(user):]
        options = ['a', 'b']
        print("checking the extension")
        if('.gen' in FILENAME):
            flash(f'This is a generation config file. Click on <span style="color:#FFD900;">Generate Layers</span> to start generation.', 'file_info')
        elif('.ana' in FILENAME):
            flash(f'This is an analysis config file. Click on <span style="color:#FFD900;">Analyze Layers</span> to start analyzing.', 'file_info')
        elif('.net' in FILENAME):
            flash(f'Select an option from the <span style="color:#FFD900;">Visualize</span> dropdown to see a visualization for this file.', 'file_info')
        elif('.ecom' in FILENAME):
            flash(f'This is an edge community file. Select an option from the <span style="color:#FFD900;">Visualize</span> dropdown to see a visualization for this file.', 'file_info')
        elif('.vcom' in FILENAME):
            flash(f'This is a vertex community file. Select an option from the <span style="color:#FFD900;">Visualize</span> dropdown to see a visualization for this file.', 'file_info')
        return render_template('dashboard3.html', us=user, options=options, current_working_directory=current_working,
                               file_list=os.listdir(current_working), log=log_window_output, showpath=showpath, file_output=x, filen=filename, BASE_URL=BASE_URL, sid=sid, mp=session.get(f'mainpath_{sid}'), form=form, current_page=page, total_pages=total_pages)
    except Exception as e:
        print(e)
        user = request.args.get('user')
        sid = request.args.get('sid')
        flash("Some error occurred", 'error')
        return redirect(url_for('mln.dashboard', user=user, sesid=sid))


@login_required
@mln.route('/profilepage')
def accountpage():
    try:
        sid = request.args.get('sid')
        return render_template('profile.html', BASE_URL=BASE_URL, usname=session[f'username_{sid}'], name=session[f'name_{sid}'], ph=session[f'ph_{sid}'], em=session[f'email_{sid}'], sid=sid)
    except:
        user = request.args.get('user')
        sid = request.args.get('sid')
        flash(f"Oops! Something seems to have gone wrong. Please provide feedback on this using the feedback button.", 'error')
        return redirect(url_for('mln.dashboard', user=user, sesid=sid))


@login_required
@mln.route('/deletepage')
def deletepage():
    sid = request.args.get('sid')
    return render_template('delete.html', BASE_URL=BASE_URL, usname=session[f'username_{sid}'], sid=sid)


@login_required
@mln.route('/newfolder', methods=['POST', 'GET'])
def newfolder():

    sid = request.args.get('sid')
    user = session[f'username_{sid}']
    direcName = request.form["fdname"]
    sanitized_direcName = re.sub(r'[^a-zA-Z0-0]', '', direcName)
    os.mkdir(os.path.join(
        session[f'userpath_{sid}'], sanitized_direcName), mode=0o777)
    os.chmod(os.path.join(
        session[f'userpath_{sid}'], sanitized_direcName), mode=0o777)
    cwd = session[f'userpath_{sid}']
    form = UploadFileForm()
    session[f'showpath_{sid}'] = session.get(f'userpath_{sid}')[
        session.get(f'userpath_{sid}').index(user):]
    if form.validate_on_submit():

        file = form.file.data
        if(file == None):
            pass
        else:
            file.save(os.path.join(session.get(
                f'userpath_{sid}'), secure_filename(file.filename)))

    return redirect(url_for('mln.dashboard', user=user, sesid=sid))


@login_required
@mln.route('/generate_layer', methods=['POST', 'GET'])
def generate_page():
    try:

        user = request.args.get('user')
        sid = request.args.get('sid')
        file = request.args.get('file')
        mln_usr = session.get(f'mainpath_{sid}')
        configfilename = os.path.join(session.get(f'userpath_{sid}'), file)
        MLN_USR = mln_usr
        # os.chdir("/home/demos/mlndash-test/mln-gui/HOMLN8")
        # sys.path.append("/home/demos/mlndash-test/mln-gui/HOMLN8")
        # import layer_generator
        # multiprocessing.freeze_support()
        # layer_generator.main(MLN_USR, configfilename)
        print('function completed')
        # os.chdir("/home/demos/mlndash-test")
        # sys.path.append("/home/demos/mlndash-test")
        x=""
        # x = subprocess.check_output(
        #     'cat '+session.get(f'mainpath_{sid}')+'/log-files/'+configfilename.split('/')[-1]+'.log', shell=True).decode('utf-8').replace('\n', '<br>')
        x = '<font size="+2"><strong>Log information after processing config file: '+file + \
             '</strong></font><br>------------------------------------------------------------<br>'+x
        # return redirect(url_for('mln.dashboard',user=user,sesid=sid))
        # log_window_output = "File last modified : "+subprocess.check_output(
        #     'date -r '+configfilename+' +"%a %B %d %H:%M:%S %Y"', shell=True).decode('utf-8').replace('\n', '<br>')
        log_window_output="None"
        cwd = session[f'userpath_{sid}']
        form = UploadFileForm()
        if form.validate_on_submit():
            file = form.file.data
            if(file == None):
                pass
            else:
                file.save(os.path.join(session.get(
                    f'userpath_{sid}'), secure_filename(file.filename)))
        fl = os.listdir(cwd)
        showpath = session.get(f'userpath_{sid}')[
            session.get(f'userpath_{sid}').index(user):]
        session[f'showpath_{sid}'] = showpath
        # flash(f"Layer Generation Successful. You can visualize the .net files in ../layers_generated.", 'success')
        flash(f"Layer Generation Failed.", 'error')
        # return send_file(final_path,mimetype='text/html')
        return render_template('dashboard3.html', us=user, current_working_directory=cwd,
                               file_list=fl, showpath=session[f'showpath_{sid}'], BASE_URL=BASE_URL, filen=file, sid=sid, mp=session.get(f'mainpath_{sid}'), form=form, file_output=x, log=log_window_output)
    except Exception as e:
        print(e)
        print("Fariba Generation code error : ")
        # os.chdir("/home/demos/mlndash-test")
        # sys.path.append("/home/demos/mlndash-test")
        user = request.args.get('user')
        sid = request.args.get('sid')
        flash(f"Oops! Something seems to have gone wrong. Please provide feedback on this using the feedback button.", 'error')
        return redirect(url_for('mln.dashboard', user=user, sesid=sid))


@login_required
@mln.route('/analyze_layer', methods=['POST', 'GET'])
def analyze_page():

    try:
        print("Inside Analysis")
        user = request.args.get('user')
        sid = request.args.get('sid')
        file = request.args.get('file')
        mln_usr = session.get(f'mainpath_{sid}')
        configfilename = os.path.join(session.get(f'userpath_{sid}'), file)
        MLN_USR = mln_usr
        print("Config File name: ", configfilename)
        print("MLN_USR : ", MLN_USR)
        x=""
        # os.chdir("/home/demos/mlndash-test/mln-gui/ANALYSIS8")
        # sys.path.append("/home/demos/mlndash-test/mln-gui/ANALYSIS8")
        # import ana_MainDriver
        # error_value = ana_MainDriver.main(MLN_USR, configfilename)
        # os.chdir("/home/demos/mlndash-test")
        # sys.path.append("/home/demos/mlndash-test")
        # x = subprocess.check_output(
        #     'cat '+session.get(f'mainpath_{sid}')+'/log-files/'+configfilename.split('/')[-1]+'.log', shell=True).decode('utf-8').replace('\n', '<br>')
        x = '<font size="+2"><strong>Log information after processing config file: '+file + \
            '</strong></font><br>------------------------------------------------------------<br>'+x
        # return redirect(url_for('mln.dashboard',user=user,sesid=sid))
        log_window_output = "None"
        cwd = session[f'userpath_{sid}']
        form = UploadFileForm()
        if form.validate_on_submit():
            file = form.file.data
            if(file == None):
                pass
            else:
                file.save(os.path.join(session.get(
                    f'userpath_{sid}'), secure_filename(file.filename)))
        fl = os.listdir(cwd)
        showpath = session.get(f'userpath_{sid}')[
            session.get(f'userpath_{sid}').index(user):]
        session[f'showpath_{sid}'] = showpath
        flash(f"Analysis Failed. You can visualize the .ecom file in the ../analysis_results folder", 'error')
        # print("Viraj code error value : ", error_value)
        # if(error_value == 0):
        #     flash(f"Analysis Successful. You can visualize the .ecom file in the ../analysis_results folder", 'success')
        # elif(error_value == 1):
        #     gen_file = file.split('.')[0]
        #     flash(
        #         f"Analysis Failed. No Dictionary found. Please execute the {gen_file}.gen to generate the layers before performing analysis.", 'error')
        # elif(error_value == 2):
        #     gen_file = file.split('.')[0]
        #     flash(
        #         f"Analysis Failed. Imported Generated layers do NOT exist. Please execute the {gen_file}.gen to generate the layers before performing analysis.", 'error')
        # return send_file(final_path,mimetype='text/html')
        return render_template('dashboard3.html', us=user, current_working_directory=cwd,
                               file_list=fl, showpath=session[f'showpath_{sid}'], BASE_URL=BASE_URL, filen=file, sid=sid, mp=session.get(f'mainpath_{sid}'), form=form, file_output=x, log=log_window_output)
    except Exception as e:
        print("Error viraj_analysis : ", str(e))
        print("Error in analysis for ActorGenre : ")
        os.chdir("/home/demos/mlndash-test")
        sys.path.append("/home/demos/mlndash-test")
        user = request.args.get('user')
        sid = request.args.get('sid')

        flash(f"Oops! Something seems to have gone wrong. Please provide feedback on this using the feedback button.", 'error')
        return redirect(url_for('mln.dashboard', user=user, sesid=sid))


@login_required
@mln.route('/visualize_layer', methods=['POST', 'GET'])
def visualize_page():
    try:
        user = request.args.get('user')
        sid = request.args.get('sid')
        os.chdir('/home/demos/mlndash-test/mln-gui/VISUALIZATION')
        sys.path.append('/home/demos/mlndash-test/mln-gui/VISUALIZATION')
        filename = request.args.get('file')

        def read_html_content(file):
            with open(file, 'r') as file:
                content = file.read()
            return content
        if(request.args.get('vtype') == 'nv'):
            import plotlyVisualization8 as pv
            fname = filename.split('.')[0]
            mappingfile = os.path.join(session.get(
                f'mainpath_{sid}'), 'primary_key_converter_for_inputfiles', fname+'.map')
            final_path = pv.visualization(os.path.join(session.get(
                f'userpath_{sid}'), filename), mappingfile, session.get(f'mainpath_{sid}'))

            def read_content(file):
                with open(file, 'r') as file:
                    content = file.read()
                return content
            html_content = read_content(final_path)
            return render_template_string(html_content)
        # srdoc=open(final_path).read()
        elif(request.args.get('vtype') == 'wc'):
            import wordCloudViz5 as wc
            fpn = wc.visualization(os.path.join(session.get(
                f'userpath_{sid}'), filename), session.get(f'mainpath_{sid}'))
            html_content = read_html_content(fpn)
            return render_template_string(html_content)
            # srdoc=open(fpn).read()
        elif(request.args.get('vtype') == 'cn'):
            import communityNetworkViz5 as cn
            fname = filename.split('.')[0]
            mappingfile = os.path.join(session.get(
                f'mainpath_{sid}'), 'primary_key_converter_for_inputfiles', fname+'.map')
            fpc = cn.visualization(os.path.join(session.get(
                f'userpath_{sid}'), filename), mappingfile, session.get(f'mainpath_{sid}'))
            html_content = read_html_content(fpc)
            return render_template_string(html_content)
            # srdoc=open(fpc).read()
        elif(request.args.get('vtype') == 'bv'):
            import bokehVisualization9 as bv
            fname = filename.split('.')[0]
            mappingfile = os.path.join(session.get(
                f'mainpath_{sid}'), 'primary_key_converter_for_inputfiles', fname+'.map')
            fpa = bv.visualization(os.path.join(session.get(
                f'userpath_{sid}'), filename), mappingfile, session.get(f'mainpath_{sid}'))
            html_content = read_html_content(fpa)
            return render_template_string(html_content)
            # srdoc=open(fpa).read()
        elif(request.args.get('vtype') == 'bvd'):
            import bokehVisualization_dc1 as bvd
            fname = filename.split('.')[0]
            mappingfile = os.path.join(session.get(
                f'mainpath_{sid}'), 'primary_key_converter_for_inputfiles', fname+'.map')
            fpb = bvd.visualization(os.path.join(session.get(
                f'userpath_{sid}'), filename), mappingfile, session.get(f'mainpath_{sid}'))
            html_content = read_html_content(fpb)
            return render_template_string(html_content)
            # srdoc=open(fpa).read()
        elif(request.args.get('vtype') == 'mv'):
            import mapbox as mv
            mappingfile = os.path.join(session.get(
                f'mainpath_{sid}'), 'primary_key_converter_for_inputfiles', 'basefile.map')
            fpf = mv.visualize(os.path.join(session.get(
                f'userpath_{sid}'), filename), mappingfile, session.get(f'mainpath_{sid}'))
            html_content = read_html_content(fpf)
            return render_template_string(html_content)
            # srdoc=open(fpf).read()
        elif(request.args.get('vtype') == 'bcv'):
            import bubbleChartViz2 as bcv
            fpp = bcv.visualization(os.path.join(session.get(
                f'userpath_{sid}'), filename), session.get(f'mainpath_{sid}'))
            html_content = read_html_content(fpp)
            return render_template_string(html_content)
            # srdoc=open(fpp).read()
        else:
            import pyvisVisualization3 as pvz
            fpx = pvz.visualization(os.path.join(session.get(
                f'userpath_{sid}'), filename), session.get(f'mainpath_{sid}'))
            html_content = read_html_content(fpx)
            return render_template_string(html_content)
            # srdoc=open(fpa).read()
        FILENAME = os.path.join(session.get(f'userpath_{sid}'), filename)
        log_window_output = "File last modified : "+subprocess.check_output(
            'date -r '+FILENAME+' +"%a %B %d %H:%M:%S %Y"', shell=True).decode('utf-8').replace('\n', '<br>')
        cwd = session[f'userpath_{sid}']
        form = UploadFileForm()
        if form.validate_on_submit():
            file = form.file.data
            if(file == None):
                pass
            else:
                file.save(os.path.join(session.get(
                    f'userpath_{sid}'), secure_filename(file.filename)))
        fl = os.listdir(cwd)
        showpath = session.get(f'userpath_{sid}')[
            session.get(f'userpath_{sid}').index(user):]
        session[f'showpath_{sid}'] = showpath
        # gp=os.path.relpath(final_path,'/home/demos/mlndash-test/mln-gui/templates/dashboard3_iframe.html')
        # print(gp)
        # return send_file(final_path,mimetype='text/html')
        return render_template('dashboard3_iframe.html', us=user, log=log_window_output, current_working_directory=cwd,
                            file_list=fl, showpath=session[f'showpath_{sid}'], BASE_URL=BASE_URL, filen=filename, sid=sid, mp=session.get(f'mainpath_{sid}'), form=form, gp=srdoc)
    except:

        # os.chdir("/home/demos/mlndash-test")
        # sys.path.append("/home/demos/mlndash-test")
        user=request.args.get('user')
        sid=request.args.get('sid')

        flash(f"Oops! Something seems to have gone wrong. Please provide feedback on this using the feedback button.",'error')
        return redirect(url_for('mln.dashboard',user=user,sesid=sid))
