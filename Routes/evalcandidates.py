from email import message
from flask.blueprints import Blueprint
from flask import render_template
from flask import request, flash, redirect
import os
import operator
import docx2txt
import pymongo
from pprint import pprint
from werkzeug.utils import secure_filename
from flask import send_from_directory
import PyPDF2
import os
from os import listdir
from os.path import isfile, join
from io import StringIO
import pandas as pd
from collections import Counter
#import ru_core_news_sm
#nlp = ru_core_news_sm.load()
import spacy
nlp = spacy.load("D:\\Python\\Diplom\\project\\tuned_spacy_ner_rus")
from spacy.matcher import PhraseMatcher
import requests
import codecs
from bs4 import BeautifulSoup as BS
from random import randint
import base64
from io import BytesIO


headers = [
    {'User-Agent': 'Mozilla/5.0 (Windows NT 5.1; rv:47.0) Gecko/20100101 Firefox/47.0',
        'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'},
    {'User-Agent': 'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.112 Safari/537.36',
        'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'},
    {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; rv:53.0) Gecko/20100101 Firefox/53.0',
        'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'}
    ]


client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["rec_data"]
my_collection = db["rec_data"]

eval = Blueprint('eval', __name__,
                template_folder='templates',
                static_folder='static')


def pdfextract(file):
    fileReader = PyPDF2.PdfFileReader(open(file,'rb'))
    countpage = fileReader.getNumPages()
    count = 0
    text = []
    while count < countpage:    
        pageObj = fileReader.getPage(count)
        count +=1
        t = pageObj.extractText()
        print (t)
        text.append(t)
    return text

def hhru(url):
    resumes = []
    links = []
    errors = []
    domain = 'https://hh.ru'
    if url:
        resp = requests.get(url, headers=headers[randint(0, 2)])
        if resp.status_code == 200:
            soup = BS(resp.content, 'html.parser')
            main_div = soup.find('div', attrs={'class': 'resume-serp'})
            if main_div:
                div_lst = main_div.find_all('div', attrs={'class': 'resume-search-item__content-wrapper'})
                for div in div_lst:
                    my_link = div.find('div', attrs={'class': 'resume-search-item__header'}).find('span').find('a')['href']
                    resp2 = requests.get(domain + my_link, headers=headers[randint(0, 2)])
                    if resp2.status_code == 200:
                        soup2 = BS(resp2.content, 'html.parser')
                        resume_text = soup2.find('div', attrs={'class': 'resume-wrapper'}).text
                        resumes.append(resume_text)
                        links.append(domain + my_link)
                        
            else:
                errors.append({'url': url, 'title': "Div does not exists"})
        else:
            errors.append({'url': url, 'title': "Page do not response"})

    return resumes, links

#function that does phrase matching and builds a candidate profile
def create_profile(file, skillsfile):
    text = pdfextract(file) 
    text = str(text)
    text = text.replace("\\n", "")
    text = text.lower()
    #below is the csv where we have all the keywords, you can customize your own
    keyword_dict = pd.read_csv(skillsfile)
    skills_words = {}
    for item in keyword_dict:
        skills_words[item] = [nlp(text) for text in keyword_dict[item].dropna(axis = 0)]
        
    matcher = PhraseMatcher(nlp.vocab)
    for item in skills_words:
        matcher.add(item, None, *skills_words[item])

    doc = nlp(text)
    
    d = []  
    matches = matcher(doc)
    for match_id, start, end in matches:
        rule_id = nlp.vocab.strings[match_id]  # get the unicode ID, i.e. 'COLOR'
        span = doc[start : end]  # get the matched slice of the doc
        d.append((rule_id, span.text))      
    keywords = "\n".join(f'{i[0]} {i[1]} ({j})' for i,j in Counter(d).items())
    
    ## convertimg string of keywords to dataframe
    df = pd.read_csv(StringIO(keywords),names = ['Keywords_List'])
    df1 = pd.DataFrame(df.Keywords_List.str.split(' ',1).tolist(),columns = ['Subject','Keyword'])
    df2 = pd.DataFrame(df1.Keyword.str.split('(',1).tolist(),columns = ['Keyword', 'Count'])
    df3 = pd.concat([df1['Subject'],df2['Keyword'], df2['Count']], axis =1) 
    df3['Count'] = df3['Count'].apply(lambda x: x.rstrip(")"))
    
    base = os.path.basename(file)
    filename = os.path.splitext(base)[0]
       
    name = filename.split('_')
    name2 = name[0]
    name2 = name2.lower()
    ## converting str to dataframe
    name3 = pd.read_csv(StringIO(name2),names = ['Candidate Name'])
    
    dataf = pd.concat([name3['Candidate Name'], df3['Subject'], df3['Keyword'], df3['Count']], axis = 1)
    dataf['Candidate Name'].fillna(dataf['Candidate Name'].iloc[0], inplace = True)

    return(dataf)


#function that does phrase matching and builds a candidate profile from hh.ru
def create_profile_hh(text, link, skillsfile): 
    text = text.replace("\\n", "")
    text = text.lower()
    #below is the csv where we have all the keywords, you can customize your own
    keyword_dict = pd.read_csv(skillsfile)
    skills_words = {}
    for item in keyword_dict:
        skills_words[item] = [nlp(text) for text in keyword_dict[item].dropna(axis = 0)]
        
    matcher = PhraseMatcher(nlp.vocab)
    for item in skills_words:
        matcher.add(item, None, *skills_words[item])

    doc = nlp(text)
    
    d = []  
    matches = matcher(doc)
    for match_id, start, end in matches:
        rule_id = nlp.vocab.strings[match_id]  # get the unicode ID, i.e. 'COLOR'
        span = doc[start : end]  # get the matched slice of the doc
        d.append((rule_id, span.text))      
    keywords = "\n".join(f'{i[0]} {i[1]} ({j})' for i,j in Counter(d).items())
    
    ## convertimg string of keywords to dataframe
    df = pd.read_csv(StringIO(keywords),names = ['Keywords_List'])
    df1 = pd.DataFrame(df.Keywords_List.str.split(' ',1).tolist(),columns = ['Subject','Keyword'])
    df2 = pd.DataFrame(df1.Keyword.str.split('(',1).tolist(),columns = ['Keyword', 'Count'])
    df3 = pd.concat([df1['Subject'],df2['Keyword'], df2['Count']], axis =1) 
    df3['Count'] = df3['Count'].apply(lambda x: x.rstrip(")"))
    
    name2 = link #os.path.splitext(base)[0] 
       
    name3 = pd.read_csv(StringIO(name2),names = ['Candidate Name'])
    
    dataf = pd.concat([name3['Candidate Name'], df3['Subject'], df3['Keyword'], df3['Count']], axis = 1)
    dataf['Candidate Name'].fillna(dataf['Candidate Name'].iloc[0], inplace = True)
    dataf['link'] = link

    return(dataf)



@eval.route('/eval', methods=['POST', 'GET'])
def index6():
    if request.method =='POST':
        if ('key_skills' not in request.files or 'resume_files[]' not in request.files) and not request.form.get('hh_link'): 
            flash('Необходимо загрузить файлы')
            return redirect(request.url)

        files = request.files.getlist("resume_files[]")

        basedir = os.path.abspath(os.path.dirname(__file__))
        if not request.form.get('hh_link'):
            for resumes in files:
                filename = secure_filename(resumes.filename)
                resumes.save(os.path.join(basedir, 'uploads', filename))
            key_skills = request.files['key_skills']
            if key_skills:
                filename1 = secure_filename(key_skills.filename)
                key_skills.save(os.path.join(basedir, 'csv_files', filename1))
            
            
            mypath=os.path.join(basedir, 'uploads') #enter your path here where you saved the resumes
            onlyfiles = [os.path.join(mypath, f) for f in os.listdir(mypath) if os.path.isfile(os.path.join(mypath, f))]

            #code to execute/call the above functions

            final_database=pd.DataFrame()
            i = 0 
            while i < len(onlyfiles):
                file = onlyfiles[i]
                try:
                    dat = create_profile(file, os.path.join(os.path.join(basedir, 'csv_files') ,filename1))
                    final_database = final_database.append(dat)
                except:
                    pass
                i +=1

            #code to count words under each category and visulaize it through Matplotlib

            final_database2 = final_database['Keyword'].groupby([final_database['Candidate Name'], final_database['Subject']]).count().unstack()
            final_database2.reset_index(inplace = True)
            final_database2.fillna(0,inplace=True)
            new_data = final_database2.iloc[:,1:]
            new_data.index = final_database2['Candidate Name']
            import matplotlib.pyplot as plt
            plt.rcParams.update({'font.size': 10})
            ax = new_data.plot.barh(title="Навыки по категорями", legend=False, figsize=(25,7), stacked=True)
            labels = []
            for j in new_data.columns:
                for i in new_data.index:
                    label = str(j)+": " + str(new_data.loc[i][j])
                    labels.append(label)
            patches = ax.patches
            for label, rect in zip(labels, patches):
                width = rect.get_width()
                if width > 0:
                    x = rect.get_x()
                    y = rect.get_y()
                    height = rect.get_height()
                    ax.text(x + width/2., y + height/2., label, ha='center', va='center')

            # сгенерировать уникальное имя файла и можно также сделать имя папки, в которую заливать резюме, а потом удалять её
            plt.savefig(os.path.join(os.path.join(basedir, 'static\\img').replace("\\Routes", ""),'figure1'))
            directory = os.path.join(os.path.join(basedir, 'static\\img').replace("\\Routes", ""),'figure1.png')
            return render_template('evalcandidates.html', flag = 1, basedir = directory)

        if (request.form.get('hh_link')):
            hh_link = request.form.get('hh_link')
            basedir = os.path.abspath(os.path.dirname(__file__))

            resumes, links = hhru(hh_link)

            key_skills = request.files['key_skills']
            if key_skills:
                filename1 = secure_filename(key_skills.filename)
                key_skills.save(os.path.join(basedir, 'csv_files', filename1))
            
            mypath=os.path.join(basedir, 'uploads') 

            final_database=pd.DataFrame()
            i = 0 
            while i < len(resumes):
                file = resumes[i]
                link = links[i]
                try:
                    dat = create_profile_hh(file, link, os.path.join(os.path.join(basedir, 'csv_files') ,filename1))
                    final_database = final_database.append(dat)
                except:
                    pass
                i +=1


            final_database2 = final_database['Keyword'].groupby([final_database['Candidate Name'], final_database['Subject']]).count().unstack()
            final_database2.reset_index(inplace = True)
            final_database2.fillna(0,inplace=True)
            new_data = final_database2.iloc[:,1:]
            new_data["link"] = final_database2['Candidate Name']
            counter = 1
            indexs = []
            # сделать ещё один датафрейм и просто оттуда брать индекс ссылку, а отсюда брать индекс число.
            for i in range(len(new_data.index)):
                indexs.append(counter)
                counter += 1
            new_data["Номер ссылки"] = indexs
            new_data.set_index(['Номер ссылки'], inplace = True)
            import matplotlib.pyplot as plt
            plt.rcParams.update({'font.size': 10})
            ax = new_data.plot.barh(title="Навыки по категорям", legend=False, figsize=(25,7), stacked=True)
            labels = []
            links_for_hr = []
            counter = 1
            for j in new_data.columns:
                for i in new_data.index:
                    links_for_hr.append(new_data.loc[i]['link'])
                    label = str(j)+": " + str(new_data.loc[i][j])
                    #label = counter
                    labels.append(label)
                    counter += 1
            patches = ax.patches
            myset = set(links_for_hr)
            links_for_hr = list(myset)

            for i in range(len(links_for_hr)):
                links_for_hr[i] = str(i+1) + ". " + links_for_hr[i]
            for label, rect in zip(labels, patches):
                width = rect.get_width()
                if width > 0:
                    x = rect.get_x()
                    y = rect.get_y()
                    height = rect.get_height()
                    ax.text(x + width/2., y + height/2., label, ha='center', va='center')

            plt.savefig(os.path.join(os.path.join(basedir, 'static\\img').replace("\\Routes", ""),'figure2'))
            directory = os.path.join(os.path.join(basedir, 'static\\img').replace("\\Routes", ""),'figure2.png')
            return render_template('evalcandidates.html', flag = 2, basedir = directory, links_for_hr = links_for_hr)


    return render_template('evalcandidates.html')
