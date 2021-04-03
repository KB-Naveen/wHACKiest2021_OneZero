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
    for file_name in cv:
        if flag_print:
            print('\n')
            print('*'*25)
            print(file_name)
            print('*'*25)

        main_file_handler = open(file_name, 'r', encoding='latin-1')
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

        dict_of_data_series[file_name.split('original')[-1][1:]] = curr_data_series
    if flag_print:
        print(curr_data_series)
    main_file_handler.close()
    data_frame = pd.DataFrame(dict_of_data_series)
    data_frame.to_csv(jdcsv, sep='\t')

    return True

import os, math
import pandas as pd
import numpy as np

def get_closest(word, n):
    '''Get n most similar words by words.'''
    #This function can easily be expanded to get similar words to phrases--
    #using sent2vec() method defined in WithWord2Vec notebook.
    word = word.lower()
    words = [word]
    similar_vals = [1]
    try:
        similar_list = model.most_similar(positive=[word],topn=n)

        for tupl in similar_list:
            words.append(tupl[0])
            similar_vals.append(tupl[1])
    except:
        #If word not in vocabulary return same word and 1 similarity--
        #see initialisation of words, similarities.
        pass

    return words, similar_vals

def rankcvs(CVs,desc,num,t):
    cvs = pd.read_csv(CVs, sep='\t')

    cvs = cvs.set_index('Unnamed: 0')


    prc_description = desc

    word_value = {}
    similar_words_needed = 2
    for word in prc_description.split():
        similar_words, similarity = get_closest(word, similar_words_needed)
        for i in range(len(similar_words)):
            word_value[similar_words[i]] = word_value.get(similar_words[i], 0)+similarity[i]
            print(similar_words[i], word_value[similar_words[i]])

    no_of_cv = t

    count = {}
    idf = {}
    for word in word_value.keys():
        count[word] = 0
        for i in range(no_of_cv):
            try:
                if word in cvs.loc(0)['skill'][i].split() or word in cvs.loc(0)['exp'][i].split():
                    count[word] += 1
            except:
                pass
        if (count[word] == 0):
            count[word] = 1
        idf[word] = math.log(no_of_cv/count[word])
    print(count)
    print(idf)

    score = {}
    for i in range(no_of_cv):
        score[i] = 0
        try:
            for word in word_value.keys():
                tf = cvs.loc(0)['skill'][i].split().count(word) + cvs.loc(0)['exp'][i].split().count(word)
                score[i] += word_value[word]*tf*idf[word]
        except:
            pass


    sorted_list = []
    for i in range(no_of_cv):
        sorted_list.append((score[i], i))

    sorted_list.sort(reverse = True)
    sorteded=[]
    sort2=[]
    for s, i in sorted_list:
        k=[]
        if list(cvs)[i] != '.DS_Store':
            print(list(cvs)[i], ':', s)
            k.append(list(cvs)[i])
            k.append(s)
            sorteded.append((list(cvs)[i], ':', s))
            sort2.append(k)
    return  sorteded[:num],sort2


import spacy
from .pdftotext import convertPDFToText

nlp = spacy.load('en_core_web_md')

def jobmatch(cv,desc):
    if str(cv[-3:])=='pdf':
        text=convertPDFToText(cv)
    elif str(cv[-4:])=='docx':
        import docx2txt
        text = docx2txt.process(cv)

    elif str(cv[-3:])=='txt':
        f = open(cv,'r')
        text=f.read()
    else:
        text=cv

    doc = nlp(text)
    doc2 = nlp(desc)
    return doc.similarity(doc2)*100


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
        appli = Application(name=name, jobId=id ,resume=file)
        appli.save()

        return render(request,"applied.html",{'name':name})

def rankings(request):
    if request.method == "POST":
        id = request.POST['id']
        length = request.POST['length']
        desc = Job.objects.get(id=id).description

        paths = []
        app = Application.objects.filter(jobId=id)
        for a in app:
            paths.append(a.resume.path)


        print(type(paths[0]))
        fileName = "resumes/converted/csv-"+str(id)+".csv"

        texttocsv(paths,fileName)
        k,s = rankcvs(fileName,desc,5,5)

        for i in s:
            pk = "original/"+i[0]
            name = Application.objects.get(resume=pk)
            i.append(name)
            i[1] = round(i[1],2)

        return render(request,"ranking.html",{'s':s})

def match(request):
    return render(request,"match.html")

def matched(request):
    if request.method == "POST":
        file = request.FILES['file']
        text = ""
        for c in file.chunks():
            text = text + str(c)
        desc = request.POST['description']

        points = jobmatch(text,desc)

        if points>=85:
            mes = "Hurry ! Go Ahead, you'r on right path"
        elif 60<points>85:
            mes = "You need some more practice"
        else:
            mes = "You need to improve your resume and skills"

        return render(request,"matched.html",{'points':points,'mes':mes})