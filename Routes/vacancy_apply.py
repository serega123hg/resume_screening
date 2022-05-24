from flask.blueprints import Blueprint
from flask import render_template
from flask import request,  flash, redirect, url_for
import os  
import spacy
from spacy.matcher import Matcher
import pandas as pd
import docx2txt
#nlp_model = spacy.load("C:\\Users\\Serge\\ner_model_rus")
import pymongo
#from pprint import pprint
import re
import pymorphy2
morph = pymorphy2.MorphAnalyzer()
#import pymorphy2
#import operator
#from nltk.tokenize import word_tokenize 
#from nltk.corpus import stopwords
#set(stopwords.words('english'))
#from wordcloud import WordCloud
from nltk.probability import FreqDist
#import matplotlib.pyplot as plt
from bson.objectid import ObjectId

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
#import datetime 
from werkzeug.utils import secure_filename
from flask import send_from_directory
#from manage import ALLOWED_EXTENSIONS, UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'pdf','docx'}


vacancy_apply = Blueprint('vacancy_apply', __name__,
                template_folder='templates',
                static_folder='static')

nlp = spacy.load("D:\\Python\\Diplom\\models\\tuned_spacy_ner_rus")
skills = "D:\Python\Diplom\jz_skill_patterns.jsonl"
#ruler = nlp.add_pipe("entity_ruler", before="ner")


# initialize matcher with a vocab
matcher = Matcher(nlp.vocab)

def extract_name(resume_text):
    nlp_text = nlp(resume_text)
    
    # First name and Last name are always Proper Nouns
    pattern = [{'POS': 'PROPN'}, {'POS': 'PROPN'}]
    
    matcher.add('NAME',[pattern])
    
    matches = matcher(nlp_text)
    
    for match_id, start, end in matches:
        span = nlp_text[start:end]
        return span.text


# Education Degrees
EDUCATION = [
            'ВЫСШЕЕ','СРЕДНЕЕ ОБЩЕЕ', 'ВЫСШЕЕ НЕОКОНЧЕННОЕ', 'БАКАЛАВР', 'МАГИСТР'
        ]

def extract_education(resume_text):
    nlp_text = nlp(resume_text)

    # Sentence Tokenizer
    #nlp_text = [sent.string.strip() for sent in nlp_text.sents]
    nlp_text = [sent.text.strip() for sent in nlp_text.sents]
    #print(nlp_text)
    edu = {}
    # Extract education degree
    for index, text in enumerate(nlp_text):
        for tex in text.split():
            # Replace all special symbols
            tex = re.sub(r'[?|$|.|!|,]', r'', tex)
            if tex.upper() in EDUCATION:
                edu[tex] = text + nlp_text[index + 1]

    # Extract year
    education = []
    for key in edu.keys():
        year = re.search(re.compile(r'(((20|19)(\d{2})))'), edu[key])
        if year:
            education.append((key, ''.join(year[0])))
        else:
            education.append(key)
    return list(set(education))


def allowed_file(filename):
    """ Функция проверки расширения файла """
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


soiscatel = Blueprint('soiscatel', __name__,
                template_folder='templates',
                static_folder='static')

# @soiscatel_result.route('/soiscatel/uploads/<name>')
# def download_file(name):
#     return send_from_directory(app.config["UPLOAD_FOLDER"], name)



connect_string = 'mongodb+srv://sergey:MXL8whWLH264W5y@cluster0.icpry.mongodb.net/?retryWrites=true&w=majority'
client = pymongo.MongoClient(connect_string)
#client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["rec_data"]
my_collection = db["rec_data"]

@vacancy_apply.route('/vacancy_apply/<vacancy_id>', methods=['GET', 'POST'])
def index4(vacancy_id):
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

        for vacancy in vac:
            for elem in vacancy:
                if "vacancy_text" in elem.keys():
                    elem["vacancy_text_reduced"] = elem["vacancy_text"][:400] + "..."

        if request.method == 'POST':
            # проверим, передается ли в запросе файл 
            if 'resume_file' not in request.files:
                # После перенаправления на страницу загрузки
                # покажем сообщение пользователю 
                flash('Необходимо загрузить файл в формате docx или pdf')
                return redirect(request.url)
            resume_file = request.files['resume_file']
            #desc_file = request.files['desc_file']

            # Если файл не выбран, то браузер может
            # отправить пустой файл без имени.
            if resume_file.filename == '':
                flash('Нет выбранного файла')
                return redirect(request.url)
            # if resume_file and allowed_file(resume_file.filename):
            #     # безопасно извлекаем оригинальное имя файла
            #     filename = secure_filename(file.filename)
            #     # сохраняем файл
            #     file.save(os.path.join(UPLOAD_FOLDER, filename))
                # если все прошло успешно, то перенаправляем  
                # на функцию-представление `download_file` 
                # для скачивания файла
            #if resume_file and desc_file is not None:
            # file_details = {"Filename":resume_file.name,"FileType":resume_file.type,"FileSize":resume_file.size}
            # st.write(file_details)
            resume = docx2txt.process(resume_file)

            for elem in vac[0]:
                if "vacancy_text" in elem.keys():
                    job_desc = elem["vacancy_text"]
            text = [resume, job_desc]
            cv = CountVectorizer()
            count_matrix = cv.fit_transform(text)
            match_percentage = cosine_similarity(count_matrix)[0][1] * 100
            match_percentage = round(match_percentage, 2)
            #print("Your resume matches about " + str(match_percentage) + " of the job description")
            mes = "Ваше резюме соответствует описанию вакансии примерно на " + str(match_percentage) + "%"
                #return redirect(url_for('download_file', name=filename))

            doc = nlp(resume)

            dic = {}
            skillls = []
            i = 0
            for ent in doc.ents:
                if ent.label_ == "PERSON" and i == 0: 
                    dic["PERSON"] = ent.text
                    i = i + 1
                if ent.label_ == "EMAIL":
                    dic["EMAIL"] = ent.text
                if ent.label_ == "MOBILE":
                    dic["MOBILE"] = ent.text 
                if ent.label_ == "SKILL":
                    skillls.append(ent.text)

            skillls = [i.capitalize() for i in set([i.lower() for i in skillls])]
            dic["SKILLS"] = skillls

            
            dic["EDUCATION"] = extract_education(resume)
            dic["NAME"] = extract_name(resume)
            #print(dic)
            

        
            rec_record = {
            "NAME":dic["NAME"],
            "EMAIL":dic["EMAIL"],
            "PHONE":dic["MOBILE"],
            "SKILLS":dic["SKILLS"],
            "EDUCATION":dic["EDUCATION"],
            "match_score": match_percentage,
            "rec_type": "soiscatel",
            "owner": str(vacancy_id)
            }
            my_collection.insert_one(rec_record)


            return render_template('/vacancy_apply.html', mes = mes, vac = vac[0])

        return render_template('vacancy_apply.html', vac = vac[0])
    return render_template('vacancy_apply.html')





# @support.route('/support/inwork', methods=['POST', 'GET'])
# def idx2():
#     conn = cx_Oracle.connect(user='KURS', password='KOLOBOK', dsn=dsn)
#     mycursor = conn.cursor()
#     mycursor.execute('select * from APPLINWORK ORDER BY Ride_Time')
#     result = mycursor.fetchall()

#     conn.close

#     if request.method == 'POST':
#         if (request.form.get('applid')):
#             applid = request.form.get('applid')
#         conn = cx_Oracle.connect(user='KURS', password='KOLOBOK', dsn=dsn)
#         mycursor = conn.cursor()
#         mycursor.execute('UPDATE APPLICATIONS SET Closed = 1 WHERE ApplID = ' + str(applid))
#         mycursor.execute('COMMIT')
#         mycursor.execute('select * from APPLINWORK ORDER BY Ride_Time')
#         result = mycursor.fetchall()
#         conn.close
#         return render_template('support.html', rezinwork=result)

#     return render_template('support.html', rezinwork=result)


# @support.route('/support/create', methods=['POST', 'GET'])
# def idx3():
#     conn = cx_Oracle.connect(user='KURS', password='KOLOBOK', dsn=dsn)
#     mycursor = conn.cursor()
#     mycursor.execute('select WORKERS.FIO, WORKERS.WorkerID from WORKERS JOIN POSITIONS ON WORKERS.fk_pos = POSITIONS.PosID WHERE POSITIONS.Pos_Name = \'Support\'')
#     workers = mycursor.fetchall()
#     wrkrs = []
#     for elem in workers:
#         wd1[elem[0]] = elem[1]
#         wrkrs.append(elem[0])

#     conn.close

#     if request.method == 'POST':
#         if request.form.get('fk_worker'):
#             fields = []
#             fields1 = []
#             if request.form.get('fk_worker'):
#                 fk_worker = request.form.get('fk_worker')
#                 fk_worker = str(wd1[fk_worker])
#                 fields.append(fk_worker)
#                 fields1.append('fk_worker')

#             if request.form.get('Client_Name'):
#                 Name = request.form.get('Client_Name')
#                 Name = '\''+str(Name)+'\''
            
#             if request.form.get('Client_Last_Name'):
#                 Last_Name = request.form.get('Client_Last_Name')
#                 Last_Name = '\''+str(Last_Name)+'\''

#             if request.form.get('Client_Phone'):
#                 Phone = request.form.get('Client_Phone')
#                 Phone = '\''+str(Phone)+'\''


#             if request.form.get('Ride_time'):
#                 Ride_Date = request.form.get('Ride_time')
#                 #Ride_Date = '\''+str(Ride_Date)+'\''
            
#             if request.form.get('Ride_time1'):
#                 Ride_time = request.form.get('Ride_time1')
#                 #Ride_time = '\''+str(Ride_time)+'\''

#             td =  'TO_DATE(\''+str(Ride_Date) + ' ' + str(Ride_time) + ':00\', \'YYYY-MM-DD HH24:MI:SS\')'


#             conn = cx_Oracle.connect(user='KURS', password='KOLOBOK', dsn=dsn)
#             mycursor = conn.cursor()
#             mycursor.execute('select CLIENTS.ClientID from CLIENTS where Name = '+ str(Name) + ' AND Last_Name = ' +str(Last_Name)  + ' AND Phone = ' + str(Phone))
#             rz = mycursor.fetchall()
#             cl = str(rz[0][0])
#             fields.append(str(rz[0][0]))
#             fields1.append('fk_client')

#             mycursor.execute('select RideID, (('+ td +' - Ride_time) * 24 * 60) from RIDE where fk_client = '+ cl)
#             #mycursor.execute('select RideID, min(ABS('+ td +' - Ride_time) * 24 * 60) from RIDE where fk_client = '+ cl + ' GROUP BY RideID')
#             rz = mycursor.fetchall()
#             tmpid = []
#             tmprazn = []
#             for elem in rz:
#                 tmpid.append(elem[0])
#                 tmprazn.append(elem[1])

#             fk_ride = str(tmpid[tmprazn.index(min(tmprazn))])

#             fields.append(fk_ride)
#             fields1.append('fk_ride')
#             #fk_ride = str(rz[0][0])

#             if request.form.get('Description'):
#                 Description = request.form.get('Description')
#                 fields.append('\''+str(Description)+'\'')
#                 fields1.append('Description')
            
#             mystr = ''
#             mystr1 = ''
#             for elem in fields:
#                 mystr += elem + ', '
#             mystr = mystr[:-1]
#             mystr = mystr[:-1]

#             for element in fields1:
#                 mystr1 += element + ', '
#             mystr1 = mystr1[:-1]
#             mystr1 = mystr1[:-1]

#             #conn = cx_Oracle.connect(user='KURS', password='KOLOBOK', dsn=dsn)
#             #mycursor = conn.cursor()

#             mycursor.execute('INSERT INTO APPLICATIONS (ApplID, ' + mystr1 + ', Closed) VALUES (ApplID.NextVal, ' + mystr + ', 0)')
#             mycursor.execute('COMMIT')
#             mycursor.execute('select WORKERS.FIO, POSITIONS.PosID from WORKERS JOIN POSITIONS ON WORKERS.fk_pos = POSITIONS.PosID WHERE POSITIONS.Pos_Name = \'Support\'')
#             workers = mycursor.fetchall()
#             wrkrs = []
#             for elem in workers:
#                 wd1[elem[0]] = elem[1]
#                 wrkrs.append(elem[0])
#             conn.close
#             return render_template('support.html', message1 = 'Запись добавлена', workers = wrkrs, rezcreate=1)

#     return render_template('support.html', workers = wrkrs, rezcreate=1)

