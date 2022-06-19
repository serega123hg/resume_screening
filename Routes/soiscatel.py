from email import message
from flask.blueprints import Blueprint
from flask import render_template
from flask import request, flash, redirect, url_for
import os  
import pymongo
from flask import send_from_directory

#connect_string = ''
#client = pymongo.MongoClient(connect_string)
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["rec_data"]
my_collection = db["rec_data"]


soiscatel = Blueprint('soiscatel', __name__,
                template_folder='templates',
                static_folder='static')



@soiscatel.route('/soiscatel', methods=['POST', 'GET'])
def check_resume():

    vac = []
    for vacancy in my_collection.find({"rec_type": "vac"}):
        #post
        temp = []
        for elem in vacancy:
            temp.append({elem:vacancy[elem]})

        vac.append(temp)


    for vacancy in vac:
        for elem in vacancy:
            if "vacancy_text" in elem.keys():
                elem["vacancy_text_reduced"] = elem["vacancy_text"][:400] + "..."
    if vac == []:
        message = "На данный момент нет активных вакансий"
        return render_template('/soiscatel.html', message = message)

    return render_template('/soiscatel.html', vac = vac)

    