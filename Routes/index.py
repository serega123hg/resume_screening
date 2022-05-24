from flask.blueprints import Blueprint
from flask import render_template
import os  
#from models.lecturer import Lecturer
import datetime
from flask import request
import sys
# from datetime import datetime
# from models.subject import Subject
# from models.interval import Interval
# from models.group import Group
# from models.schedule import Schedule


index1 = Blueprint('index1', __name__,
                template_folder='templates',
                static_folder='static')


@index1.route('/')
def index():
    
    return render_template('index.html')