from flask.blueprints import Blueprint
from flask import render_template
from flask import request, flash, redirect
import os
import operator
import docx2txt
import pymongo
from pprint import pprint

connect_string = 'mongodb+srv://sergey:MXL8whWLH264W5y@cluster0.icpry.mongodb.net/?retryWrites=true&w=majority'
client = pymongo.MongoClient(connect_string)
#client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["rec_data"]
my_collection = db["rec_data"]

hr = Blueprint('hr', __name__,
                template_folder='templates',
                static_folder='static')


@hr.route('/hr', methods=['POST', 'GET'])
def index5():

    vac = []
    for vacancy in my_collection.find({"rec_type":"vac"}):
        #post
        temp = []
        #if post["NAME"]:
            #temp.append(post)
            #temp.append({"NAME" : post["NAME"]})
        for elem in vacancy:
            temp.append({elem:vacancy[elem]})

        vac.append(temp)
   # print(vac)

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






















    # soiscatels = []
    # for post in my_collection.find():
    #     #post
    #     temp = []
    #     #if post["NAME"]:
    #         #temp.append(post)
    #         #temp.append({"NAME" : post["NAME"]})
    #     for elem in post:
    #         temp.append({elem:post[elem]})

    #     soiscatels.append(temp)

    # stroka = ""
    # stroka1 = ""
    # for s in soiscatels:
    #     for item in s:

    #         if "SKILLS" in item.keys():
    #             temp = item["SKILLS"]
    #             for elem in temp:
    #                 stroka1 += elem + ", "
    #             stroka1 = stroka1[:-1]
    #             stroka1 = stroka1[:-1]
    #             item["SKILLS"] = stroka1
    #             stroka1 = ""

    #         if "EDUCATION" in item.keys():
    #             temp = item["EDUCATION"]
    #             for elem in temp:
    #                 if len(elem) == 2:
    #                     stroka += elem[0].title() + " " + elem[1] + "г, "
    #                 else: 
    #                     stroka += elem[0].title() + ", "
    #             stroka = stroka[:-1]
    #             stroka = stroka[:-1]
    #             item["EDUCATION"] = stroka
    #             stroka = ""

    #     try:
    #         soiscatels = soiscatels.sort(key=operator.itemgetter('match_score'))
    #     except:
    #         pass
    #     # for s in soiscatels:
    #     #     s["contacts"] = s["name"] + "\n" + s["email"] + "\n" + s["phone"] 
    #     #     s["geo"] = s["city"] + "\n" + s["cond"] 
    #     #     #soiscatels["contacts"] = soiscatels["name"] + "\n" + soiscatels["email"] + "\n" + soiscatels["phone"] 
    #     #     temp = s["skills"]
    #     #     s["skills"] = ""
    #     #     for item in temp:
    #     #         s["skills"] += item[1] + "\n"
    #     # for s in soiscatels:
    #     #     s["contacts"] = s["NAME"] + "\n" + s["EMAIL"] + "\n" + s["PHONE"] 
    #     #     #s["geo"] = s["city"] + "\n" + s["cond"] 
    #     #     #soiscatels["contacts"] = soiscatels["name"] + "\n" + soiscatels["email"] + "\n" + soiscatels["phone"] 
    #     #     temp = s["SKILLS"]
    #     #     s["SKILLS"] = ""
    #     #     for item in temp:
    #     #         s["SKILLS"] += item[1] + "\n"
    
    # #print(soiscatels)    
    
        
    # return render_template('/hr.html', soiscatels = soiscatels)

            #return render_template('client.html', cards=crds, flag = 1, Name = Name1, Last_Name = Last_Name1, Rating = result12, plans=plans, mes = 'Такси заказано')
    #return render_template('hr.html')
    