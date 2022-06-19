from flask.blueprints import Blueprint
from flask import render_template
from flask import request,  flash, redirect, url_for
import os  
import spacy
from spacy.matcher import Matcher
import pandas as pd
import docx2txt
import pymongo
import re
import pymorphy2
morph = pymorphy2.MorphAnalyzer()
from pdfminer.converter import TextConverter
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
import io
from nltk.probability import FreqDist
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

nlp = spacy.load("D:\\Python\\Diplom\\project\\tuned_spacy_ner_rus")
skills = "jz_skill_patterns.jsonl"


# initialize matcher with a vocab
matcher = Matcher(nlp.vocab)
STOP_WORDS = spacy.lang.ru.stop_words.STOP_WORDS

def extract_text_from_pdf(pdf_path):
    with open(pdf_path, 'rb') as fh:
        # iterate over all pages of PDF document
        for page in PDFPage.get_pages(fh, caching=True, check_extractable=True):
            # creating a resoure manager
            resource_manager = PDFResourceManager()
            # create a file handle
            fake_file_handle = io.StringIO()
            # creating a text converter object
            converter = TextConverter(
                                resource_manager, 
                                fake_file_handle, 
                                codec='utf-8', 
                                laparams=LAParams()
                        )
            # creating a page interpreter
            page_interpreter = PDFPageInterpreter(
                                resource_manager, 
                                converter
                            )
            # process current page
            page_interpreter.process_page(page)
            # extract text
            text = fake_file_handle.getvalue()
            yield text
            # close open handles
            converter.close()
            fake_file_handle.close()


def process_text(text):
    doc = nlp(text.lower())
    result = []
    for token in doc:
        if token.text in nlp.Defaults.stop_words:
            continue
        if token.is_punct:
            continue
        if token.lemma_ == '-PRON-':
            continue
        result.append(token.lemma_)
    return " ".join(result)


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
            'ВЫСШЕЕ','СРЕДНЕЕ ОБЩЕЕ', 'ВЫСШЕЕ НЕОКОНЧЕННОЕ', 'БАКАЛАВР', 'МАГИСТР',
            'ОСВНОВНОЕ ОБЩЕЕ', 'СРЕДНЕЕ ПРОФЕССИОНАЛЬНОЕ', 'СПЕЦИАЛИТЕТ', 'ПОДГОТОВКА КАДРОВ ВЫСШЕЙ КВАЛИФИКАЦИИ'
        ]

def extract_education(resume_text):
    nlp_text = nlp(resume_text)

    # Sentence Tokenizer
    nlp_text = [sent.text.strip() for sent in nlp_text.sents]
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

client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["rec_data"]
my_collection = db["rec_data"]

@vacancy_apply.route('/vacancy_apply/<vacancy_id>', methods=['GET', 'POST'])
def index4(vacancy_id):
    if vacancy_id and vacancy_id != "":
        vac = []
        for vacancy in my_collection.find({'_id': ObjectId(vacancy_id), "rec_type":"vac"}):
            temp = []
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

            # Если файл не выбран, то браузер может
            # отправить пустой файл без имени.
            if resume_file.filename == '':
                flash('Нет выбранного файла')
                return redirect(request.url)

            extension = resume_file.filename.split('.')[-1]
            if extension == "docx" or "doc":
                resume = docx2txt.process(resume_file)
            else:
                resume = ""
                # calling above function and extracting text
                for page in extract_text_from_pdf(resume_file):
                    resume += ' ' + page 

            for elem in vac[0]:
                if "vacancy_text" in elem.keys():
                    job_desc = elem["vacancy_text"]

            match_percentage =nlp(process_text(resume)).similarity(nlp(process_text(job_desc))) * 100
            mes = "Ваше резюме соответствует описанию вакансии примерно на " + str(match_percentage) + "%"
      
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

            rec_record = {
            "NAME":dic["NAME"],
            "EMAIL":dic["EMAIL"],
            "PHONE":dic["MOBILE"],
            "SKILLS":dic["SKILLS"],
            "EDUCATION":dic["EDUCATION"],
            "match_score": match_percentage,
            "rec_type": "soiscatel",
            "owner": str(vacancy_id),
            "full_text": resume
            }
            my_collection.insert_one(rec_record)


            return render_template('/vacancy_apply.html', mes = mes, vac = vac[0])

        return render_template('vacancy_apply.html', vac = vac[0])
    return render_template('vacancy_apply.html')


