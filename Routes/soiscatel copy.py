# from flask.blueprints import Blueprint
# from flask import render_template
# from flask import request, flash, redirect, url_for
# import os  
# import spacy
# import docx2txt
# nlp_model = spacy.load("C:\\Users\\Serge\\ner_model_rus")
# import pymongo
# from pprint import pprint
# import re
# import operator
# #from nltk.tokenize import word_tokenize 
# #from nltk.corpus import stopwords
# #set(stopwords.words('english'))
# #from wordcloud import WordCloud
# from nltk.probability import FreqDist
# #import matplotlib.pyplot as plt

# from sklearn.feature_extraction.text import CountVectorizer
# from sklearn.metrics.pairwise import cosine_similarity
# import datetime 
# from werkzeug.utils import secure_filename
# from flask import send_from_directory
# #from manage import ALLOWED_EXTENSIONS, UPLOAD_FOLDER
# ALLOWED_EXTENSIONS = {'pdf','docx'}


# client = pymongo.MongoClient("mongodb://localhost:27017/")
# db = client["rec_data"]
# my_collection = db["rec_data"]


# def allowed_file(filename):
#     """ Функция проверки расширения файла """
#     return '.' in filename and \
#            filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# soiscatel = Blueprint('soiscatel', __name__,
#                 template_folder='templates',
#                 static_folder='static')

# # @soiscatel_result.route('/soiscatel/uploads/<name>')
# # def download_file(name):
# #     return send_from_directory(app.config["UPLOAD_FOLDER"], name)



# @soiscatel.route('/soiscatel', methods=['POST', 'GET'])
# def check_resume():
#     if request.method == 'POST':
#         # проверим, передается ли в запросе файл 
#         if 'resume_file' not in request.files and 'desc_file' not in request.files:
#             # После перенаправления на страницу загрузки
#             # покажем сообщение пользователю 
#             flash('Необходимо загрузить оба файла в формате docx')
#             return redirect(request.url)
#         resume_file = request.files['resume_file']
#         desc_file = request.files['desc_file']

#         # Если файл не выбран, то браузер может
#         # отправить пустой файл без имени.
#         if resume_file.filename == '' or desc_file.filename == '':
#             flash('Нет выбранного файла')
#             return redirect(request.url)
#         # if resume_file and allowed_file(resume_file.filename):
#         #     # безопасно извлекаем оригинальное имя файла
#         #     filename = secure_filename(file.filename)
#         #     # сохраняем файл
#         #     file.save(os.path.join(UPLOAD_FOLDER, filename))
#             # если все прошло успешно, то перенаправляем  
#             # на функцию-представление `download_file` 
#             # для скачивания файла
#         #if resume_file and desc_file is not None:
#         # file_details = {"Filename":resume_file.name,"FileType":resume_file.type,"FileSize":resume_file.size}
#         # st.write(file_details)
#         resume = docx2txt.process(resume_file)

#         job_desc = docx2txt.process(desc_file)
#         text = [resume, job_desc]
#         cv = CountVectorizer()
#         count_matrix = cv.fit_transform(text)
#         match_percentage = cosine_similarity(count_matrix)[0][1] * 100
#         match_percentage = round(match_percentage, 2)
#         print("Your resume matches about " + str(match_percentage) + " of the job description")
#         mes = "Your resume matches about " + str(match_percentage) + " of the job description"
#             #return redirect(url_for('download_file', name=filename))

#         mes += resume

#         doc = nlp_model(resume)
#         educ = []
#         ed_count = 0
#         educ_comm = []
#         educ_spec = []
#         educ_inter = []
#         educ_year = []
#         skills = []
#         ach = []
#         cond = []
#         lang = []
#         ed = []
#         workexp = []
#         rec_name = []
#         rec_age = []
#         rec_phone = []
#         rec_city = []
#         rec_email = []
#         rec_woexp = []
#         rec_vac = []
#         rec_sal = []
#         rec_name = []


#         for ent in doc.ents:
#             #print(f'{ent.label_.upper():{30}}- {ent.text}')
#             #st.write(f'{ent.label_.upper():{30}}- {ent.text}')
#             #st.write("\n")

#             if ent.label_.upper() == "NAME":
#                 rec_name.append({ent.label_.upper() : ent.text})

#             if ent.label_.upper() == "AGE":
#                 rec_age.append({ent.label_.upper() : ent.text})

#             if ent.label_.upper() == "PHONE":
#                 rec_phone.append({ent.label_.upper() : ent.text})

#             if ent.label_.upper() == "CITY":
#                 rec_city.append({ent.label_.upper() : ent.text})

#             if ent.label_.upper() == "EMAIL":
#                 rec_email.append({ent.label_.upper() : ent.text})

#             if ent.label_.upper() == "WOEXP":
#                 rec_woexp.append({ent.label_.upper() : ent.text})

#             if ent.label_.upper() == "EDUCATION":
#                 #ed[f'{ed_count}'] = []
#                 #rec_education = '"' + ent.label_.upper() + '"' + ":" + '"' + ent.text + '"'
#                 educ_comm.append({'\'' + ent.label_.upper() + '\'' : '\'' + ent.text + '\''})
#                 #ed['f{ed_count}'] = educ_comm
#                 #educ.append({'"' + ent.label_.upper() + '"' : '"' + ent.text + '"'})

#             if ent.label_.upper() == "YEAROFGRAD":
#                 #rec_name = '"' + ent.label_.upper() + '"' + ":" + '"' + ent.text + '"'
#                 educ_year.append({'\'' + ent.label_.upper() + '\'' : '\'' + ent.text + '\''})


#             if ent.label_.upper() == "INTER":
#                 educ_inter.append({'\'' + ent.label_.upper() + '\'' : '\'' + ent.text + '\''})

#             if ent.label_.upper() == "SPEC":
#                 educ_spec.append({'\'' + ent.label_.upper() + '\'' : '\'' + ent.text + '\''})

#             if ent.label_.upper() == "VACANCY":
#                 rec_vac.append({ent.label_.upper() : ent.text})

#             if ent.label_.upper() == "SALARY":
#                 rec_sal.append({ent.label_.upper() : ent.text})

#             if ent.label_.upper() == "WORKCONDITIONS":
#                 cond.append({'\'' + ent.label_.upper() + '\'' : '\'' + ent.text + '\''})

#             if ent.label_.upper() == "ORG":
#                 workexp.append({'\'' + ent.label_.upper() + '\'' : '\'' + ent.text + '\''})
                
#             if ent.label_.upper() == "POSITION":
#                 workexp.append({'\'' + ent.label_.upper() + '\'' : '\'' + ent.text + '\''})
                
#             if ent.label_.upper() == "WORKFROM":
#                 workexp.append({'\'' + ent.label_.upper() + '\'' : '\'' + ent.text + '\''})
                
#             if ent.label_.upper() == "WORKTO":
#                 workexp.append({'\'' + ent.label_.upper() + '\'' : '\'' + ent.text + '\''})
                
#             if ent.label_.upper() == "SUMMARY":
#                 workexp.append({'\'' + ent.label_.upper() + '\'' : '\'' + ent.text + '\''})

#             if ent.label_.upper() == "SKILLS":
#                 skills.append({'\'' + ent.label_.upper() + '\'' : '\'' + ent.text + '\''})

#             if ent.label_.upper() == "ACHIEVEMENTS":
#                 ach.append({'\'' + ent.label_.upper() + '\'' : '\'' + ent.text + '\''})

#             if ent.label_.upper() == "LANG":
#                 lang.append({ent.label_.upper() : ent.text })
                    
                
#         #     if str(ed_count) in ed:
#         #         ed[f'{ed_count}'] = educ_comm
#         #         ed_count = ed_count + 1
#         #         educ_comm = []
                
#         #print(lang)

#         lang_str = "["
#         for item in lang:
#             lang_str = lang_str + str(item) + ','
#         lang_str = lang_str + "]"
#         print(lang_str.replace(",]", "]"))
#         print(rec_sal)

#         if len(educ_comm) >= len(educ_inter):
#             educ_comm = educ_comm[1:]

#         temp = []
#         for i in range(len(educ_comm)):
#             try:
#                 temp.append(educ_comm[i])
#             except:
#                 pass
#             try:
#                 temp.append(educ_year[i])
#             except:
#                 pass
#             try:
#                 temp.append(educ_inter[i])
#             except:
#                 pass
#             try:
#                 temp.append(educ_spec[i])
#             except:
#                 pass
            
#             ed.append({str(i) : temp})
#             temp = []

#         print(ed)
#         print(workexp)

#         rec_record = {
#         "name" : rec_name,
#         "age": rec_age,
#         "email": rec_email,
#         "city": rec_city,
#         "phone": rec_phone,
#         "age": rec_age,
#         "cond": cond,
#         "woexp": rec_woexp,
#         "vacancy": rec_vac,
#         "salary": rec_sal,
#         "education" : ed,
#         "skills": skills,
#         "ach": ach,
#         "lang": lang
#         }
#         my_collection.insert_one(rec_record)


#         return render_template('/soiscatel.html', mes = mes)
#     return render_template('/soiscatel.html')