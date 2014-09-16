# -*- coding: utf-8 -*-
"""
    Flaskr
    ~~~~~~

    A microblog example application written as Flask tutorial with
    Flask and sqlite3.

    :copyright: (c) 2010 by Armin Ronacher.
    :license: BSD, see LICENSE for more details.
"""

from sqlite3 import dbapi2 as sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash, _app_ctx_stack

# configuration
DEBUG = True

# create our little application :)
app = Flask(__name__)
app.config.from_object(__name__)

@app.route('/', methods=['GET','POST'])
def calculate():
    error = None
    if request.method == 'POST':
        print( request.values["a1_x1"])
        print( request.values["atompos_2_x"])
        return render_template('z2pack_online.html')
    else:
        #~ print( request.values["a1_x1"])
        return render_template('z2pack_online.html')



if __name__ == '__main__':
    app.run()
