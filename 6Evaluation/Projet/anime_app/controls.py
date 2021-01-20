# -*- coding: utf-8 -*-
import datetime
from datetime import time,MAXYEAR,timedelta
import pandas as pd
import numpy as np

# Text du popup associé au bouton "lear more"
popup=["What is this app?\n",
"This dash app is composed of two tabs: Advance search and Recommendation.",
"The first one does advance anime search by filtering them by:",
"    - genres",
"    - type",
"    - duration per episode",
"    - rating",
"    - producers",
"    - score",
"    - episode number",
"    - status",
"    - start year",
"The last one gives you recommendations based on other animes you enjoyed.",
"In both case, the selected animes are sorted by score and popularity.",
"All information about animes come from the following website https://myanimelist.net/."]
popup="\n".join(popup)


def to_time(timedelta,to_datetime=False):
    """
    Conversion d'une durée en secondes
    en un datetime.time ou datetime.datetime

    Args:
        timedelta: une durée ou un liste de durée en secondes
        to_datetime: choix du format datetime.datetime

    Returns:
        variable(s) datetime.time ou datetime.datetime associée(s)
    """
    if type(timedelta)==int:
        res=time()
        if timedelta!=0 and timedelta%3600==0 or timedelta-3600>0:
            res=res.replace(hour=timedelta//3600)
            timedelta-=res.hour*3600
        if timedelta!=0 and timedelta%60==0 or timedelta-60>0:
            res=res.replace(minute=timedelta//60)
            timedelta-=res.minute*60
        if timedelta!=0:
            res=res.replace(second=timedelta)
        if to_datetime:
            res=datetime.datetime(year=MAXYEAR,month=12,day=31,hour=res.hour,minute=res.minute,second=res.second)
        return res
    elif type(timedelta)==list:
        return [to_time(d,to_datetime) for d in timedelta]


def init_components(collection):
    """
    Création des labels et des valeurs des dropdowns,sliders 
    et Checklist de l'onglet "Advance Search"

    Args:
        collection: collection comportant les animés à requêter
    
    Returns:
        dictionnaire contenant:
            - Type_val: valeurs et labels du dropdown "type"
            - rating_val: valeurs et labels du dropdown "rating"
            - status_val: valeurs et labels du dropdown "status"
            - duration_val, duration_label: valeurs et labels du slider "duration"
            - episode_val: valeurs et labels du slider "episodes"
            - year_val: valeurs et labels du slider "start_year"
            - genres_val: valeurs et labels de la checklist "genres"
            - radio_genres: valeurs et labels de radioItems "genres"
            - producers_val: valeurs et labels de la checklist "producers"
            - radio_producers: valeurs et labels de radioItems "producers"
            - titles: valeurs et labels de la barre de recherche "titles"
    """
    # Création des valeurs et labels des dropdowns
    Type_val=collection.aggregate([{"$group" : {"_id" : "$Type"}}])
    Type_val=[val["_id"] for val in list(Type_val) if val["_id"]!=None]

    rating_val=collection.aggregate([{"$group" : {"_id" : "$rating"}}])
    rating_val=[val["_id"] for val in list(rating_val) if val["_id"]!=None]

    status_val=collection.aggregate([{"$group" : {"_id" : "$status"}}])
    status_val=[val["_id"] for val in list(status_val) if val["_id"]!=None]


    # Création des valeurs et labels des sliders
    durations=collection.aggregate([{"$group" : {"_id" : "$duration"}}])
    max_duration=max([val["_id"].hour for val in list(durations) if type(val["_id"])==type(datetime.datetime.today())])
    hours=4*[0]+2*[1]+[2,max_duration+1]
    minutes=[i for i in range(0,46,15)]+[0,30,0,0]
    duration_val=[int(timedelta(hours=h,minutes=m).total_seconds()) for h,m in zip(hours,minutes)]
    duration_label=["{}h{}min".format(h,m) if h!=0 and m!=0 
                    else "{}h".format(h) if h!=0 
                    else "{}min".format(m) 
                    for h,m in zip(hours,minutes)]

    episodes=collection.aggregate([{"$group" : {"_id" : "$episodes"}}])
    max_episodes=max([val["_id"] for val in list(episodes) if type(val["_id"])==int])
    episodes_val=[1,50,200,300,500,700,(max_episodes//1000+1)*1000]

    year=collection.aggregate([{"$group" : {"_id" : "$aired.start"}}])
    year=[int(val["_id"].year) if type(val["_id"])==type(datetime.datetime.today())
        else int(val["_id"]) if str(val["_id"]).isdigit()
        else -1 for val in list(year)]
    year=[val for val in year if val!=-1]
    max_year,min_year=max(year),min(year)
    year_val=[(min_year//10)*10]+[i for i in range(1930,1990,30)]+[i for i in range(2000,2016,7)]+[max_year]


    # Création des valeurs et labels des checklists et radioItems
    genres=collection.aggregate([{"$group" : {"_id" : "$genres"}}])
    genres=[val["_id"] for val in genres if val["_id"]!=None ]
    genres_val=[]
    for g in genres:
        genres_val= genres_val+g
    genres_val=set(genres_val)
    genres_val= sorted(list(genres_val),key=str.lower)
    radio_genres=["All genres","Limit to","Exactly with","Exclude"]

    producers=collection.aggregate([{"$group" : {"_id" : "$producers"}}])
    producers=[val["_id"] for val in producers if val["_id"]!=[] ]
    producers_val=[]
    for p in producers:
        producers_val= producers_val+p
    producers_val=set(producers_val)
    producers_val= sorted(list(producers_val),key=str.lower)
    radio_producers=["All producers","Limit to","Exactly with","Exclude"]


    # Création de la barre de recherche de l'onglet "Recommendation"
    animes=list(collection.find({}))
    Titles=sorted([anime["main_title"] for anime in animes],key=str.lower)
    titles=[{"label":title.replace("U+002F","/"),"value":title} for title in Titles]

    # Création du dictionnaire de sortie
    keys=["Type_val","rating_val","status_val","duration_val",
            "duration_label","episodes_val","year_val","genres_val",
            "radio_genres","producers_val","radio_producers","titles"]
    values=[Type_val,rating_val,status_val,duration_val,
            duration_label,episodes_val,year_val,genres_val,
            radio_genres,producers_val,radio_producers,titles]
    return dict(list(zip(keys,values)))


def make_request(Type=["All types"],rating=["All ratings"],status=["All status"],
    score={"check":[],"slider":[]},duration={"check":[],"slider":[],"reco":False},
    episodes={"check":[],"slider":[],"reco":False},year={"check":[],"slider":[]},
    genres={'radio':'','check':[]},producers={'radio':'','drop':[]},
    titles=[],options=dict()):
    """
    Réalisation d'une requête mongo 
    à partir des filtres passé en arguments

    Args:
        filtres utilisés pour construire la requête
        concernant les champs: main_title, other_titles, 
        genres, Type, duration, aired.start, episodes, status, 
        score, producers
    
    Returns:
        rêquete mongo adéquate
    """ 
    # Initialisation des filtres et de la requête
    champs=['titles','score','genres','producers',
            'Type','episodes','status','duration','rating','aired']
    filters=dict([(champ,None) for champ in champs])
    request={"$and":[]}

    # Edition des filtres 
    # (titles,Type,status,rating,duration, genres, producers, score, episodes, aired.start)
    if len(titles)>0:
        filters["titles"]={"$or":[{"main_title":{"$in":titles}},{"other_titles":{"$in":titles}}]}

    if "All types" not in Type:
        filters["Type"]={"Type":{"$in":Type}}

    if "All status" not in status:
        filters["status"]={"status":{"$in":status}}

    if "All ratings" not in rating:
        filters["rating"]={"rating":{"$in":rating}}

    if len(duration["slider"])>0:
        if duration["reco"]==False and [(d>=0 and d<len(duration["slider"])) for d in duration["slider"]]==len(duration["slider"])*[True]:
            d=to_time([options["duration_val"][i] for i in duration["slider"]],True)
        elif duration["reco"] and [d>=0 for d in duration["slider"]]==len(duration["slider"])*[True]:
            d=to_time(duration["slider"],True)
        else:
            d=to_time([min(options["duration_val"]),max(options["duration_val"])],True)
        filters["duration"]={ "$and": [ {"duration":{"$gte":min(d)}} , {"duration":{"$lte":max(d)}} ] }
        if "Include N\\A" in duration["check"]:
            filters["duration"]={"$or":[filters["duration"],{"duration":None}]}

    if genres["radio"]=="Limit to" and len(genres["check"])>0:
        filters["genres"]={"genres":{"$in":genres["check"]}}
    elif genres["radio"]=="Exclude" and len(genres["check"])>0:
        filters["genres"]={"genres":{"$nin":genres["check"]}}
    elif genres["radio"]=="Exactly with" and len(genres["check"])>0:
        filters["genres"]={"genres":{"$all":genres["check"]}}

    if producers["radio"]=="Limit to" and len(producers["drop"])>0:
        filters["producers"]={"producers":{"$in":producers["drop"]}}
    elif producers["radio"]=="Exclude" and len(producers["drop"])>0:
        filters["producers"]={"producers":{"$nin":producers["drop"]}}
    elif producers["radio"]=="Exactly with" and len(producers["drop"])>0:
        filters["producers"]={"producers":{"$all":producers["drop"]}}

    if len(score["slider"])>0:
        filters["score"]={ "$and": [ {"score":{"$gte": min(score["slider"])}} , {"score":{"$lte": max(score["slider"])}} ] }
        if "Include N\\A" in score["check"]:
            filters["score"]={"$or":[filters["score"],{"score":None}]}

    if len(episodes["slider"])>0:
        if episodes["reco"]==False and [(e>=0 and e<len(options["episodes_val"])) for e in episodes["slider"]]==len(episodes["slider"])*[True]:
            nb_epi=[options["episodes_val"][i] for i in episodes["slider"]]
        elif episodes["reco"] and [e>0 for e in episodes["slider"]]==len(episodes["slider"])*[True]:
           nb_epi=episodes["slider"]
        else:
            nb_epi=[min(options["episodes_val"]),max(options["episodes_val"])]
        filters["episodes"]={ "$and": [ {"episodes":{"$gte": min(nb_epi)}} , {"episodes":{"$lte": max(nb_epi)}} ] }
        if "Include N\\A" in episodes["check"]:
            filters["episodes"]={"$or":[filters["episodes"],{"episodes":None}]}

    if len(year["slider"])>0:
        if [(y>=0 and y<len(options["year_val"])) for y in year["slider"]]==len(year["slider"])*[True]:
            years=[options["year_val"][i] for i in year["slider"]]
        elif [y>=1900 for y in year["slider"]]==len(year["slider"])*[True]:
            years=year["slider"]
        else:
            years=[min(options["year_val"]),max(options["year_val"])]
        start={"$or":[{"aired.start":{"$gte":years[0]}},{"aired.start":{"$gte":datetime.datetime(years[0],1,1)}}]}
        end={"$or":[{"aired.start":{"$lte":years[1]}},{"aired.start":{"$lt":datetime.datetime(years[1],12,31)}}]}
        filters["aired"]={"$and":[start,end]}
        if "Include N\\A" in year["check"]:
            filters["aired"]={"$or":[filters["aired"],{'aired':None}]}
    
    # Edition de la requête
    for key in filters.keys():
        if filters[key]!=None:
            request["$and"].append(filters[key])   
    if len(request["$and"])==0:
        request={}

    return request


def select_anime(request,collection,champs=[],max_result=10**30,sort={"fields":None,"order":None}):
    """
    Sélection des animés de collections 
    correspondant à request

    Args:
        request: requête mongo
        colletion: colletion à parcourir
        champs: liste de champs à récupérer
        sort: dict indiquant si on doit trier les documents de clé champs et order
        max_result: taille maximale de la liste de sortie
    
    Return:
        liste d'animés validant request
    """
    # Choix des champs à récupérés
    champs = dict([(champ,1) for champ in champs])

    # Lancement de la requête
    if sort["fields"]==None or sort["order"]==None: 
        if len(champs)>1:
            res=list(collection.find(request,champs))
        elif len(champs)==1:
            res=[elt[list(champs.keys())[0]] for elt in list(collection.find(request,champs))]
        else:
            res= list(collection.find(request))
    else:
        sorting=[(c,o) for c,o in zip(sort["fields"],sort["order"])]
        if len(champs)>1:
            res=list(collection.find(request,champs).sort(sorting))
        elif len(champs)==1:
            res=[elt[list(champs.keys())[0]] for elt in list(collection.find(request,champs).sort(sorting))]
        else:
            res= list(collection.find(request).sort(sorting))
    
    # Limitation du nombre de résultat
    if len(res)>0:
        return res[0:min(max_result,len(res))]
    
    return list(collection.find(request))


def print_infos(selection,idx,NaN=''):
    """
    Mise en forme de la chaine de caractère
    contenant les infos relatives à l'anime
    de rang idx de selection:

    Args:
        selection: liste d'animés séletionnés
        idx: rang de l'animé dont les infos sont à affichés
    
    Returns:
        Chaine de caractères contenant les infos demandées
        Url menant à l'image correspondant à l'animé
        Indice de l'animé dont les infos sont affichés
        Table des animés qui sont liés
    """
    # Chaine de formatage des infos
    infos='''
    #### Main information

    *** Other titles: ***{}\n
    *** Type: ***{}\n
    *** Genres: ***{}\n
    *** Producers: ***{}\n
    *** Status: ***{}\n
    *** Rating: ***{}\n
    *** Score: ***{}\n
    *** Popularity: ***{}\n
    *** Ranked: ***{}\n
    *** Start date: ***{}\n
    *** End date: ***{}\n
    *** Duration: ***{}\n
    *** Episodes: ***{}\n
    *** Synopsis: ***{}\n
    '''

    # Valeurs par défaut des affichages
    fields=["other_titles","Type",
            "genres","producers","status","rating",
            "score","popularity","ranked",
            "start date","end date","duration",
            "episodes","synopsis","related_anime"]
    fields=dict([(field,NaN) if field!="main_title" else (field,"...") for field in fields])
    image="https://static.thenounproject.com/png/1554490-200.png"
    result_title="#### 0 Results"

    # Edition de infos avec les champs de selection[idx]
    NA=[[],{},'None',None]
    table=[{'Link':'','Titles':''}]
    if len(selection)>0:
        anime=selection[idx]
        for k in anime.keys():
            if anime[k] not in NA:
                if k in ["main_title","Type","status","score","popularity","synopsis","episodes","ranked","rating"]:
                    fields[k]=anime[k]
                elif k in ["other_titles","genres","producers"]:
                    fields[k]=", ".join(anime[k])
                elif k=="aired":
                    if "start" in anime[k].keys():
                        if type(anime[k]["start"])==int:
                            fields["start date"]=anime[k]["start"]
                        else:
                            fields["start date"]=str(anime[k]["start"].date())
                    if "end" in anime[k].keys():
                        if type(anime[k]["end"])==int:
                            fields["end date"]=anime[k]["end"]
                        else:
                            fields["end date"]=str(anime[k]["end"].date())
                elif k=="duration":
                    fields[k]=str(anime[k].time())
                elif k=="related_anime":
                    for key in anime[k].keys():
                        table=[]
                        link= ['''[{}]({})'''.format(title,'http://localhost:8050/page/'+title.replace(" ","%20").replace("/","U+002F")) for title in anime[k][key]]
                        table.append({'Link':key,'Titles':'\n'.join(link)})
                elif k=="image":
                    image=anime[k]
        result_title='''#### {} \nResult {} on {}'''.format(fields["main_title"].replace("U+002F","/"),idx+1,len(selection))

    return infos.format(fields["other_titles"],
                        fields["Type"],fields["genres"],
                        fields["producers"], fields["status"],
                        fields["rating"], fields["score"],
                        fields["popularity"], fields["ranked"],
                        fields["start date"], fields["end date"],
                        fields["duration"], fields["episodes"],
                        fields["synopsis"], fields["related_anime"]),image,result_title,table


def clean_selection(selection,collection,clean_yet=False):
    """
    Suppression dans une sélection d'animés
    des animés liées entre eux

    Args:
        selection: liste de récommandations à traiter
    Return:
        liste d'animés à traiter
    """
    if not clean_yet:
        ref_infos=find_references(selection,collection,champs=["main_title","related_anime"])
        selection=pd.Series(selection)
        for i in selection.index:
            if not pd.Series(selection[i]).isna()[0]:
                related_anime=ref_infos["related_anime"][ref_infos["main_title"].index(selection[i])]
                selection[i+1:]=selection[i+1:].apply(lambda x: np.NaN if x in related_anime else x)
        return list(selection.dropna())
    return selection


def find_references(references,collection,champs,NaN=None):
    """
    Extraction des infos de références pour l'algo de Recommendation

    Args:
        references: titres des animés de références
        collection: base de données comportant tous les animés
        champs: liste de champs utilisés pour la Recommendation
        NaN: format des données manquantes

    Return:
        infos de références corretement formatées
    """
    NA=[None,[],'None',NaN]
    request=make_request(titles=references)
    selection=select_anime(request,collection,champs)
    infos=dict()
    for anime in selection:
        for champ in anime.keys():
            if anime[champ] not in NA and champ!="_id":
                if not champ in infos.keys():
                    infos[champ]=[anime[champ]]
                else:
                    infos[champ].append(anime[champ])
    if "duration" in infos.keys():
        infos["duration"]=[elt.time() for elt in infos["duration"]]
        infos["duration"]=[datetime.timedelta(hours=elt.hour,minutes=elt.minute,seconds=elt.second)for elt in infos["duration"]]
        infos["duration"]=[int(elt.total_seconds()) for elt in infos["duration"]]
    if "aired" in infos.keys():
        infos["aired"]=[elt["start"].year if "start" in elt.keys() and type(elt["start"])==type(datetime.datetime.today())
                        else elt["start"] for elt in infos["aired"]]
    if "related_anime" in infos.keys():
        for i in range(len(infos["related_anime"])):
            related_anime=[]
            for k in infos["related_anime"][i].keys():
                if k!="Adaptation":
                    related_anime = related_anime  + infos["related_anime"][i][k]
            infos["related_anime"][i]=related_anime
    return infos


def partiesliste(seq):
    """
    Calcul des différents sous-ensembles
    issus de la liste passée en argument
    
    Args:
        seq: liste dont sera issus les sous-ensembles

    Returns:
        liste des sous-ensembles de seq
    """
    if len(seq)>1:
        p = []
        i, imax = 0, 2**len(seq)-1
        while i <= imax:
            s = []
            j, jmax = 0, len(seq)-1
            while j <= jmax:
                if (i>>j)&1 == 1:
                    s.append(seq[j])
                j += 1
            if len(s)>1:
                p.append(s)
            i += 1
        p.sort(key=len,reverse=True)
        return p
    return seq


def genre_combinations(genres):
    """
    Détermination des différentes combinaisons de genres
    pouvant plaire à l'utilisateur

    Args:
        genres: liste des genres plaisant à l'utilisateur
    
    Returns:
        liste des combinaisons pouvant plaire
    """
    list_genres=[set(elt) for elt in genres]
    intersection= list_genres[0]
    for elt in list_genres:
        intersection= intersection & elt
    if len(intersection)==0:
        list_genres=[]
        for elt in genres:
            list_genres = list_genres + elt
        return partiesliste(list_genres)
    return partiesliste(list(intersection)) 


def anime_Recommendation(titles,collection,options,champs=["genres","duration","episodes","aired.start","main_title"],max_result=100):
    """
    Recommendation d'animés à partir d'autres d'animés

    Args:
        titles: titres des animés utilisé comme références
        collection: base de données comportant tous les animés
        champs: liste de champs utilisés pour la Recommendation 
        max_result: taille maximale de la liste de Recommendation
        options: valeur prises par les sliders, dropdowns et checklist de l'UI
    
    Returns:
        liste d'animés recommandés
    """
    # Récupération d'infos sur les animés de références
    ref_infos=find_references(titles,collection,champs)

    # Recherche d'animés partageant possédeant les genres de référence
    under_max,selection=False,[]
    clean_yet=False
    if "genres" in ref_infos.keys():
        genres_c=[]
        for elt in ref_infos["genres"]:
            genres_c= genres_c + elt
        request=make_request(options=options,genres={"radio":'Limit to',"check":list(set(genres_c))})
        select=select_anime(request,collection,champs=["main_title"],sort={"fields":["score","popularity"],"order":[-1,-1]})
        select= set(select).difference(ref_infos["main_title"])
        selection.append(clean_selection(list(select),collection))
        clean_yet=True
        under_max=(len(selection[-1])<=max_result & len(selection[-1])>0)
        if not under_max:
            common_genres=genre_combinations(ref_infos["genres"])
            if len(common_genres)==1:
                request=make_request(options=options,genres={'radio':'Exactly with',"check":common_genres})
                select=select_anime(request,collection,champs=["main_title"],
                                    sort={"fields":["score","popularity"],"order":[-1,-1]})
                select= set(select).difference(ref_infos["main_title"])
                if len(select)>0:
                    selection.append(clean_selection(list(select),collection,clean_yet))
                    clean_yet=True
                    under_max=(len(selection[-1])<=max_result)
            elif len(common_genres)>1:
                len_common=-1
                selection2,Request=[],[]
                for elt in common_genres:
                    request=make_request(options=options,genres={'radio':'Exactly with',"check":elt})
                    if len_common!=len(elt):
                        Request.append([])
                    Request[-1].append(request)
                    len_common=len(elt)
                for r in Request:
                    select=select_anime({"$or":r},collection,champs=["main_title"],sort={"fields":["score","popularity"],"order":[-1,-1]})
                    select=set(select).difference(ref_infos["main_title"])
                    selection2.append(clean_selection(list(select),collection,True))
                len_selection2=pd.Series([len(l) if len(l)!=0 else 10**30 for l in selection])
                best_selection2=len_selection2[len_selection2<=max_result]
                if len(best_selection2)>0:
                    selection.append(selection2[np.argmax(best_selection2)])
                else:
                    best_selection2=len_selection2[len_selection2>max_result]
                    selection.append(selection2[np.argmin(best_selection2)])
                under_max=(len(selection[-1])<=max_result & len(selection[-1])>0)


    # Recherche d'animés ayant environ la même durée
    if "duration" in ref_infos.keys() and not under_max:
        mean_duration=np.mean(ref_infos["duration"])
        limits=[round(0.75*mean_duration),round(1.25*mean_duration)]
        request=make_request(options=options,titles=selection[-1],duration={"check":[],"slider":limits,"reco":True})
        select=select_anime(request,collection,champs=["main_title"],sort={"fields":["score","popularity"],"order":[-1,-1]})
        if len(select)>0:
            selection.append(clean_selection(select,collection,clean_yet))
            clean_yet=True
            under_max=(len(selection[-1])<=max_result)

    # Recherche d'animés ayant environ le même nombre d'épisodes
    if "episodes" in ref_infos.keys() and not under_max:
        mean_episodes=np.mean(ref_infos["episodes"])
        limits=[round(0.75*mean_episodes),round(1.25*mean_episodes)]
        request=make_request(options=options,titles=selection[-1],episodes={"check":[],"slider":limits,"reco":True})
        select=select_anime(request,collection,champs=["main_title"],sort={"fields":["score","popularity"],"order":[-1,-1]})
        if len(select)>0:
            selection.append(clean_selection(select,collection,clean_yet))
            clean_yet=True
            under_max=(len(selection[-1])<=max_result)

    # Recherche d'animés ayant environ le même année
    if "aired" in ref_infos.keys() and not under_max:
        mean_year=np.mean(ref_infos["aired"])
        limits=[round(mean_year)-20,round(mean_year)+20]
        request=make_request(options=options,titles=selection[-1],year={"check":[],"slider":limits})
        select=select_anime(request,collection,champs=["main_title"],sort={"fields":["score","popularity"],"order":[-1,-1]})
        if len(select)>0:
            selection.append(clean_selection(select,collection,clean_yet))
            clean_yet=True
            under_max=(len(selection[-1])<=max_result)
    
    # Renvoi de la meilleur sélection
    len_selection=pd.Series([len(l) if len(l)!=0 else 10*30 for l in selection])
    best_selection=selection[np.argmin(len_selection)]
    request=make_request(options=options,
    titles=clean_selection(best_selection,collection,clean_yet))
    best_selection= select_anime(request,collection,max_result=max_result,
                                    sort={"fields":["score","popularity"],"order":[-1,-1]})
    return best_selection