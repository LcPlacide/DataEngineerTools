
#!/usr/bin/env python
from flask import Flask, flash, redirect, render_template, \
     request, url_for 
from pymongo import MongoClient
from random import randint
import json
import datetime
from forms import MyForm   


client=MongoClient('mongodb://localhost:27017/?readPreference=primary&ssl=false')
db=client.anime
collection=db.myanimelist

# with open("anime_complet3.json") as f:
#     DOCUMENTS = json.load(f)
#     for i in range(len(DOCUMENTS)):
#         DOCUMENTS[i]["_id"]=i
#         if DOCUMENTS[i]["duration"]!=None:
#             DOCUMENTS[i]["duration"]=datetime.datetime.strptime(DOCUMENTS[i]["duration"], '%Y-%m-%d %H:%M:%S')
            
# collection.drop()
# collection.insert_many(DOCUMENTS)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'you-will-never-guess'

@app.route('/')
def rien():
    return "Rien ici... <a href='/home'> voir là </a> "

@app.route('/home', methods=('GET', 'POST'))
def home():
    form = MyForm()
    res=".*"+str(form.name.data)+".*"
    results=list(collection.find({"main_title" : {"$regex": res,'$options': 'i'}}))
    NA=[[],None,{}]
    NaN="N\A"
    for anime in results:
        for key in anime.keys():
            if anime[key] not in NA:
                if key=="aired" and "start" in anime[key].keys():
                    if type(anime[key]["start"])==int:
                        anime[key]["start"]=str(anime[key]["start"])
                    elif type(anime[key]["start"])==type(datetime.datetime.today()):
                        anime[key]["start"]=str(anime[key]["start"].date())
                if key in ["score","episoded","ranked","popularity"]:
                    anime[key]==str(anime[key])
                
            else:
                if key=="aired":
                    anime[key]={"start":NaN}
                else:
                    anime[key]=NaN
    
                
    if form.validate_on_submit():
        return render_template('search_bar.html',tasks=results,form=form)
    return render_template('search_bar.html',tasks=results,form=form)
    
    

@app.route('/page/<string:user>')
def page(user):
    results=list(collection.find({"main_title":user}))
    NA=[[],None,{}]
    NaN="N\A"
    for anime in results:
        for key in anime.keys():
            if anime[key] not in NA:
                if key=="aired" and "start" in anime[key].keys():
                    if type(anime[key]["start"])==int:
                        anime[key]["start"]=str(anime[key]["start"])
                    elif type(anime[key]["start"])==type(datetime.datetime.today()):
                        anime[key]["start"]=str(anime[key]["start"].date())
                if key in ["score","episoded","ranked","popularity","duration"]:
                    anime[key]==str(anime[key])
                elif type(anime['duration'])==type(datetime.datetime.today()):
                        anime['duration']=str(anime['duration'].time())
                elif key in ["genres","other_titles","producers"]:
                    anime[key]=",".join(anime[key])
                if key=="aired" and "end" in anime[key].keys():
                    if type(anime[key]["end"])==int:
                        anime[key]["end"]=str(anime[key]["end"])
                    elif type(anime[key]["end"])==type(datetime.datetime.today()):
                        anime[key]["end"]=str(anime[key]["end"].date())

            else:
                if key=="aired":
                    anime[key]={"start":NaN}
                else:
                    anime[key]=NaN

    return render_template('information.html',info=results)



#@app.route('/success/<username>')
#def sucess(username):
#    form = MyForm()
#    return render_template("search_bar.html",form=form)



if __name__=='__main__':
    app.run(debug=True, port=2747)