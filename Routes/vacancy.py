from email import message
from django.shortcuts import redirect
from flask.blueprints import Blueprint
from flask import render_template
from flask import request, url_for, redirect, flash
import os  
import pymongo
import operator
from bson.objectid import ObjectId


vacancy = Blueprint('vacancy', __name__,
                template_folder='templates',
                static_folder='static')

connect_string = 'mongodb+srv://sergey:MXL8whWLH264W5y@cluster0.icpry.mongodb.net/?retryWrites=true&w=majority'
client = pymongo.MongoClient(connect_string)
#client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["rec_data"]
my_collection = db["rec_data"]


@vacancy.route('/vacancy/<vacancy_id>', methods=['POST', 'GET'])
def index5(vacancy_id):

    if request.method == 'POST':
        if (request.form.get('del_vac')):
            result = my_collection.delete_one({'_id': ObjectId(vacancy_id)})
            flash('Вакансия успешно удалена', category='success')
            return redirect(url_for('hr.index5'))
    #vacancy_id = request.args.get('vacancy_id')
    #vacancy_id = request.query_string.decode("utf-8").replace("vacancy_id=", "")
    #print(vacancy_id)
    if vacancy_id and vacancy_id != "":
        vac = []
        for vacancy in my_collection.find({'_id': ObjectId(vacancy_id), "rec_type":"vac"}):
            #post
            #print(vacancy)
            temp = []
            #if post["NAME"]:
                #temp.append(post)
                #temp.append({"NAME" : post["NAME"]})
            for elem in vacancy:
                temp.append({elem:vacancy[elem]})

            vac.append(temp)


        try:
            soiscatels = []
            for post in my_collection.find({'owner': vacancy_id}):
                #post
                temp = []
                #if post["NAME"]:
                    #temp.append(post)
                    #temp.append({"NAME" : post["NAME"]})
                for elem in post:
                    temp.append({elem:post[elem]})

                soiscatels.append(temp)

            stroka = ""
            stroka1 = ""
            for s in soiscatels:
                for item in s:

                    if "SKILLS" in item.keys():
                        temp = item["SKILLS"]
                        for elem in temp:
                            stroka1 += elem + ", "
                        stroka1 = stroka1[:-1]
                        stroka1 = stroka1[:-1]
                        item["SKILLS"] = stroka1
                        stroka1 = ""

                    if "EDUCATION" in item.keys():
                        temp = item["EDUCATION"]
                        for elem in temp:
                            if len(elem) == 2:
                                stroka += elem[0].title() + " " + elem[1] + "г, "
                            else: 
                                stroka += elem[0].title() + ", "
                        stroka = stroka[:-1]
                        stroka = stroka[:-1]
                        item["EDUCATION"] = stroka
                        stroka = ""

                try:
                    soiscatels = soiscatels.sort(key=operator.itemgetter('match_score'))
                except:
                    pass
        except:
            return render_template('hr.html',vac = vac, soiscatels = [])

        if soiscatels == []:
            return render_template('vacancy.html',vac = vac[0], message = "На данную вакансию нет откликов")
        return render_template('vacancy.html',vac = vac[0], soiscatels = soiscatels)
    return redirect(url_for('hr.index5'))
    