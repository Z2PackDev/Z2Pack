# -*- coding: utf-8 -*-
"""
    Z2Pack online
    ~~~~~~
    
    A calculator for the Z2 topological invariant in the tight-binding
    model. 
"""

from sqlite3 import dbapi2 as sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, _app_ctx_stack, jsonify, send_from_directory

# configuration
DEBUG = True

# create our little application :)
app = Flask(__name__)
app.config.from_object(__name__)

@app.route('/')
def welcome():
    return render_template('welcome.html')

@app.route('/input', methods=['GET','POST'])
def input():
    error = None
    if request.method == 'POST':
        check_input = False
        #----------------check all input variables----------------------#
        check_input = True #DEBUG
        if(check_input):
            return redirect(url_for('results'))
        else:
            return render_template('input.html')
    else:
        return render_template('input.html')
        
@app.route('/not_implemented')
def not_implemented():
    return render_template('not_implemented.html')

@app.route('/results')
def results():
    return render_template('result.html')
    
# to be removed (serves as example only)
@app.route('/echo/', methods=['GET'])
def echo():
    ret_data = {"value": request.args.get('echoValue')}
    return jsonify(ret_data)
    
@app.route('/user_guide')
def user_guide():
    return render_template('user_guide.html')
    
@app.route('/downloads/<path:filename>')
def download(filename):
    return send_from_directory(directory = 'downloads/', filename = filename)

@app.route('/downloads')
def downloads():
    return render_template('downloads.html')
    
if __name__ == '__main__':
    app.run()
