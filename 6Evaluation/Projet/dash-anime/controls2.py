import datetime
from datetime import time,MAXYEAR,timedelta


def to_time(timedelta,to_datetime=False):
    """
    Conversion d'une durée en secondes
    en un datetime.time ou datetime.datetime

    Args:
        timedelta: une durée ou un liste de durée en secondes
        to_datetime: choix du format datetime.datetime

    Returns:
        varible(s) datetime.time ou datetime.datetime associée(s)
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
            - popularity_val: valeurs du slider "popularity"
            - ranked_val: valeur et labels du slider "ranked"
            - year_val: valeurs et labels du slider "start_year"
            - genres_val: valeurs et labels de la checklist "genres"
            - radio_genres: valeurs et labels de radioItems "genres"
            - producers_val: valeurs et labels de la checklist "producers"
            - radio_producers: valeurs et labels de radioItems "producers"
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

    popularity=collection.aggregate([{"$group" : {"_id" : "$popularity"}}])
    max_popularity=max([val["_id"] for val in list(popularity) if type(val["_id"])==int])
    popularity_val=[i for i in range(0,10001,2000)]+[(max_popularity//1000+1)*1000]

    ranked=collection.aggregate([{"$group" : {"_id" : "$ranked"}}])
    max_ranked=max([val["_id"] for val in list(ranked) if type(val["_id"])==int])
    ranked_val=[1,1000]+[i for i in range(2000,8001,2000)]+[(max_ranked//1000+1)*1000]

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
    radio_genres=["All genres","Limit to","Exactly with","Exclude"]

    producers=collection.aggregate([{"$group" : {"_id" : "$producers"}}])
    producers=[val["_id"] for val in producers if val["_id"]!=[] ]
    producers_val=[]
    for p in producers:
        producers_val= producers_val+p
    producers_val=set(producers_val)
    radio_producers=["All producers","Limit to","Exactly with","Exclude"]


    # Création du dictionnaire de sortie
    keys=["Type_val","rating_val","status_val",
            "duration_val","duration_label","episodes_val",
            "popularity_val","ranked_val","year_val","genres_val",
            "radio_genres","producers_val","radio_producers"]
    values=[Type_val,rating_val,status_val,duration_val,
            duration_label,episodes_val,popularity_val,
            ranked_val,year_val,genres_val,
            radio_genres,producers_val,radio_producers]
    return dict(list(zip(keys,values)))


def make_request(Type=["All types"],rating=["All ratings"],status=["All status"],
    score={"check":[],"slider":[]},duration={"check":[],"slider":[]},
    episodes={"check":[],"slider":[]},
    popularity=[],ranked=[],year={"check":[],"slider":[]},
    genres={'radio':'','check':[]},producers={'radio':'','drop':[]},
    titles=[],options=dict()):
    """
    Réalisation d'une requête mongo 
    à partir des filtres passé en arguments

    Args:
        filtres utilisé pour construire la requête
    
    Returns:
        rêquete mongo adéquate
    """ 
    # Initialisation des filtres et de la requête
    champs=['titles','score','ranked',
            'popularity','genres','producers',
            'Type','episodes','status',
            'duration','rating','aired']
    filters=dict([(champ,None) for champ in champs])
    request={"$and":[]}

    # Edition des filtres
    if len(titles)>0:
        filters["titles"]={"$or":[{"main_title":{"$in":titles}},{"other_titles":{"$in":titles}}]}
    if "All types" not in Type:
        filters["Type"]={"Type":{"$in":Type}}
    if "All status" not in status:
        filters["status"]={"status":{"$in":status}}
    if "All ratings" not in rating:
        filters["rating"]={"rating":{"$in":rating}}
    if len(duration["slider"])>0:
        d=to_time([options["duration_val"][i] for i in duration["slider"]],True)
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
    if len(ranked)>0:
        filters["ranked"]={ "$and": [ {"ranked":{"$gte": min(ranked)}} , {"ranked":{"$lte": max(ranked)}} ] }
    if len(popularity)>0:
        filters["popularity"]={ "$and": [ {"popularity":{"$gte": min(popularity)}} , {"popularity":{"$lte": max(popularity)}} ] }
    if len(episodes["slider"])>0:
        nb_epi=[options["episodes_val"][i] for i in episodes["slider"]]
        filters["episodes"]={ "$and": [ {"episodes":{"$gte": min(nb_epi)}} , {"episodes":{"$lte": max(nb_epi)}} ] }
        if "Include N\\A" in episodes["check"]:
            filters["episodes"]={"$or":[filters["episodes"],{"episodes":None}]}
    if len(year["slider"])>0:
        years=[options["year_val"][i] for i in year["slider"]]
        start={"$or":[{"aired.start":{"$gte":min(years)}},{"aired.start":{"$gte":datetime.datetime(min(years),1,1)}}]}
        end={"$or":[{"aired.start":{"$lte":max(years)}},{"aired.start":{"$lt":datetime.datetime(max(years),12,31)}}]}
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


def select_anime(request,collection,champs=[],max_result=10**30):
    """
    Sélection des animes de colletions 
    correspondant à request

    Args:
        request: requête mongo
        colletion: colletion à parcourir
        champs: liste de champs à récupérer
        max_result: taille maximale de la liste de sortie
    
    Return:
        liste d'animés validant request
    """
    champs = dict([(champ,1) for champ in champs])
    if champs!={}:
        res=list(collection.find(request,champs))
    else:
        res= list(collection.find(request))
    if len(res)>0:
        return res[0:min(max_result,len(res))]
    return list(collection.find(request))

def print_infos(selection,idx):
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
    infos='''
    #### Main information

    *** Other titles: ***{}\n
    *** Type: ***{}\n
    *** Genres: ***{}\n
    *** Producers: ***{}\n
    *** Status: ***{}\n
    *** Score: ***{}\n
    *** Popularity: ***{}\n
    *** Ranked: ***{}\n
    *** Start date: ***{}\n
    *** End date: ***{}\n
    *** Duration: ***{}\n
    *** Episodes: ***{}\n
    *** Synopsis: ***{}\n
    '''
    fields=["other_titles","Type",
            "genres","producers","status",
            "score","popularity","ranked",
            "start date","end date","duration",
            "episodes","synopsis","related_anime"]
    fields=dict([(field,"N\A") if field!="main_title" else (field,"...") for field in fields])
    NA=[[],{},'None',None]
    table=[{'Link':'','Titles':''}]
    if len(selection)>0:
        anime=selection[idx]
        for k in anime.keys():
            if anime[k] not in NA:
                if k in ["main_title","Type","status","score","popularity","synopsis","episodes","ranked"]:
                    fields[k]=anime[k]
                elif k in ["other_titles","genres"]:
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
                        table.append({'Link':key,'Titles':', '.join(anime[k][key])})
                elif k=="image":
                    image=anime[k]
        idx='''#### {} \nResult {} on {}'''.format(fields["main_title"],idx+1,len(selection))
    else:
        image="https://media.istockphoto.com/vectors/no-image-available-icon-vector-id1216251206?k=6&m=1216251206&s=612x612&w=0&h=G8kmMKxZlh7WyeYtlIHJDxP5XRGm9ZXyLprtVJKxd-o="
        idx="#### 0 Results"
    return infos.format(fields["other_titles"],
                        fields["Type"],fields["genres"],
                        fields["producers"], fields["status"],
                        fields["score"],fields["popularity"],
                        fields["ranked"],
                        fields["start date"], fields["end date"],
                        fields["duration"], fields["episodes"],
                        fields["synopsis"], fields["related_anime"]),image,idx,table
            
