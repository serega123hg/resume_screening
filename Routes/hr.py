from flask.blueprints import Blueprint
from flask import render_template
from flask import request, flash, redirect
import os
import operator
import docx2txt
import pymongo
from pprint import pprint

client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["rec_data"]
my_collection = db["rec_data"]

hr = Blueprint('hr', __name__,
                template_folder='templates',
                static_folder='static')


@hr.route('/hr', methods=['POST', 'GET'])
def index5():

    vac = []
    for vacancy in my_collection.find({"rec_type":"vac"}):
        temp = []
        for elem in vacancy:
            temp.append({elem:vacancy[elem]})

        vac.append(temp)

    for vacancy in vac:
        for elem in vacancy:
            if "vacancy_text" in elem.keys():
                elem["vacancy_text_reduced"] = elem["vacancy_text"][:400] + "..."
    
    if request.method == 'POST':
        rec_vacancy_text = ""
        
        if (request.form.get('vacancy_name')):
            rec_vacancy_name = request.form.get('vacancy_name')
        if (request.form.get('vacancy_text')):
            rec_vacancy_text = request.form.get('vacancy_text')

        if 'vac_desc' in request.files:
            vac_desc = request.files['vac_desc']
            if vac_desc.filename == '':
                flash('Нет выбранного файла')
                return redirect(request.url)
            
            rec_vacancy_text = docx2txt.process(vac_desc)


        vac_record = {
        "vacancy_name" : rec_vacancy_name,
        "vacancy_text" : rec_vacancy_text,
        "rec_type":"vac"
        }
        id_ = my_collection.insert_one(vac_record).inserted_id

        return render_template('hr.html',vac = vac)
    
    if vac == []:
        message = "На данный момент нет активных вакансий"
        return render_template('/hr.html', message = message)


    return render_template('hr.html',vac = vac)
