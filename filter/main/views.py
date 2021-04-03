import spacy
from spacy.vectors import Vectors
import os
import pandas as pd
import numpy as np
nlp = spacy.load('en_core_web_sm')
vectors = Vectors(shape=(10000, 300))
nlp.vocab.vectors = vectors
print(nlp.vocab.vectors.shape)
import re
re_c = re.compile(r'\w+')

flag_print = True

# switch to clear existing data
flag_clear = True

#threshold value for determining section
threshold = 0.5

similar_to = {
    'edu' : ['education', 'study', 'academics', 'institute', 'school', 'college'],
    'exp' : ['job', 'internship', 'training', 'research', 'career', 'profession', 'role'
                                                                                  'project', 'responsibility', 'description', 'work experience', 'workshop', 'conference'],
    'skill' : ['skill', 'languages', 'technology', 'framework', 'tools', 'database'],
    'extra' : ['introduction', 'intro', 'achievement', 'hobby', 'links', 'additional',
               'personal', 'award', 'objective', 'miscellaneous', 'interest']
}

list_of_sections = similar_to.keys()

# to bring similar_words to their normal forms
for section in list_of_sections:
    new_list = []

    for word in similar_to[section]:
        docx = nlp(word)
        new_list.append(docx[0].lemma_)

    if flag_print:
        print(section, new_list)

    similar_to[section] = new_list

def modify(word):
    try:
        symbols = '''~'`!@#$%^&*)(_+-=}{][|\:;",./<>?'''
        mod_word = ''

        for char in word:
            if (char not in symbols):
                mod_word += char.lower()

        docx = nlp(mod_word)

        if (len(mod_word) == 0 or docx[0].is_stop):
            return None
        else:
            return docx[0].lemma_
    except:
        return None # to handle the odd case of characters like 'x02', etc.

if flag_print:
    test_words = ['Hello!!', '.,<>', 'India', 'of', '..freedoM..', 'e-mail']

    for word in test_words:
        print(word, '--returned-->', modify(word))
def is_empty(line):
    for c in line:
        if (c.isalpha()):
            return False
    return True

if flag_print:
    test_words = ['.', '<.>', 'Speak', 'out', '"Eric"', 'freemail...']

    for word in test_words:
        print(word, '--returned-->', (word))
dict_of_data_series = {}
flag_print = False

def texttocsv(cv,jdcsv):
    dict_of_data_series = {}
    file_name=cv
    main_file_handler = open(cv, 'r', encoding='latin-1')
    previous_section  = 'extra'
    print(file_name)
    curr_data_series = pd.Series([""]*len(list_of_sections), index=list_of_sections)

    for line in main_file_handler:
        # skip line if empty
        if (len(line.strip()) == 0 or is_empty(line)):
            continue

        # processing next line
        list_of_words_in_line = re_c.findall(line)
        list_of_imp_words_in_line  = []

        for i in range(len(list_of_words_in_line)):
            modified_word = modify(list_of_words_in_line[i])

            if (modified_word):
                list_of_imp_words_in_line.append(modified_word)

        curr_line = ' '.join(list_of_imp_words_in_line)
        doc = nlp(curr_line)
        section_value = {}

        # initializing section values to zero
        for section in list_of_sections:
            section_value[section] = 0.0
        section_value[None] = 0.0

        # updating section values
        for token in doc:
            for section in list_of_sections:
                for word in similar_to[section]:
                    word_token = doc.vocab[word]
                    section_value[section] = max(section_value[section], float(word_token.similarity(token)))

        # determining the next section based on section values and threshold
        most_likely_section = None
        for section in list_of_sections:
            #print '>>', section, section_value[section]
            if (section_value[most_likely_section] < section_value[section] and section_value[section] > threshold):
                most_likely_section = section

        # updating the section
        if (previous_section != most_likely_section and most_likely_section is not None):
            previous_section = most_likely_section


        # writing data to the pandas series
        try:
            docx = nlp(line)
        except:
            continue  # to handle the odd case of characters like 'x02', etc.
        mod_line = ''
        for token in docx:
            if (not token.is_stop):
                mod_line += token.lemma_ + ' '

        curr_data_series[previous_section] += mod_line

    dict_of_data_series[file_name] = curr_data_series
    if flag_print:
        print(curr_data_series)
    main_file_handler.close()
    data_frame = pd.DataFrame(dict_of_data_series)
    data_frame.to_csv(jdcsv, sep='\t',mode = 'a', header = True)

    return True

from django.shortcuts import render,HttpResponse,HttpResponseRedirect,redirect
from .models import Job,Application,CSVfiles

# Create your views here.
def index(request):
    return render(request,"index.html")

def create(request):
    return render(request,"create.html")

def apply(request):
    jobs = Job.objects.all()
    return render(request,"apply.html",{'jobs':jobs})

def applyFor(request,id):
    job = Job.objects.get(id=id)
    return render(request, "applyFor.html",{'job':job})

def rank(request):
    return render(request,"rank.html")

def submit(request):
    if request.method == "POST":
        cname = request.POST['cname']
        title = request.POST['title']
        description = request.POST['description']
        job = Job(companyName=cname, title=title, description=description, )
        job.save()
        return HttpResponseRedirect("submitted")

    return HttpResponseRedirect('/create/')

def submitted(request):
    return render(request, 'created.html')

def upload(request):
    if request.method == "POST":
        file = request.FILES['file']
        id = request.POST['id']
        name = request.POST['name']

        for i in file:
            print(i.name)
            print(i.size)
        return HttpResponse("Success")