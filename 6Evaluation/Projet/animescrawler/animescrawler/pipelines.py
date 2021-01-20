# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from datetime import datetime,MAXYEAR
import pymongo

class AnimescrawlerPipeline:
    def process_item(self, item, spider):
        """
        Nettoyage des champs des AnimeItems:
        - supression des espaces en fin et en début des chaines de caractères
        - conversion des champs score, ranked et popularity en entier ou réel
        - conversion des champs duration et aired en datetime ou en dict de datetime
        - remplissage des champs manquant par des None, [] ou {}
        - jointure des lignes du champ synopsis en une seul chaine de caractères
        - suppression dans les champs comportant des listes des doublons

        Returns:
            AnimeItem traité devant être stocké dans une base mongo
        """
        if item["main_title"]:
            item["main_title"]=clean_string(item["main_title"]).replace("/","U+002F")
        if item["score"]:
            item["score"]=clean_number(item["score"],"float")
        if item["synopsis"]:
            item["synopsis"]=clean_string(item["synopsis"],to_join=True)
        if item["Type"]:
            item["Type"]=clean_string(item["Type"])
        if item["genres"]:
            item["genres"]=clean_string(item["genres"])
        if item["other_titles"]:
            item["other_titles"]= clean_string(item["other_titles"],as_set=True)
        if item["producers"]:
            item["producers"]= clean_string(item["producers"],as_set=True)
        if item["ranked"]:
            item["ranked"]=clean_number(item["ranked"],"int")
        if item["popularity"]:
            item["popularity"]=clean_number(item["popularity"],"int")
        if item["related_anime"]:
            item["related_anime"]=clean_string(item["related_anime"])
        if item["duration"]:
            item["duration"] = clean_duration(item["duration"])
        if item["rating"]:
            item["rating"]=clean_string(item["rating"])
        if item["episodes"]:
            item["episodes"]=clean_number(item["episodes"],"int")
        if item["status"]:
            item["status"]=clean_string(item["status"])
        if item["aired"]:
            item["aired"]=clean_aired(item["aired"])
        return item

def clean_string(field,as_set=False,to_join=False,NaN=None):
    """
    Suppression des espaces inutiles dans les strings
    et formatage des données manquantes

    Args:
        field: champs à traiter
        as_set: booléen indiquant si on veut supprimer les doublons de field
        to_join: booléen indiquant si on veut joindre les éléments de field en
                une seul chaine de caractère
        NaN: format choisi pour les données manquantes de field après nettoyage

    Returns:
        chaine de caractères, dict ou liste suivant le type
        de field dont les éléments ont été traité
    """
    NA=['','None',"N/A",'Unknown',None,[],dict(),set(),NaN]
    if type(field)==str and field.strip() not in NA:
        return field.strip()
    elif type(field)==list and field not in NA:
        res=[elt.strip() for elt in field if elt.strip() not in NA]
        if to_join and res not in NA:
            res=" ".join(res)
            if  res not in NA and res.find("No synopsis")==-1:
                return res
        elif as_set and res not in NA:
            return clean_string(set(res))
        elif res not in NA:
            return res
    elif type(field)==set and field not in NA:
        res=list({elt.strip() for elt in field if elt.strip() not in NA})
        if res not in NA:
            return res
    elif type(field)==dict and field not in NA:
        res=dict([(key,clean_string(field[key])) for key in field.keys() if clean_string(field[key]) not in NA])
        if res not in NA:
            return res
    return NaN

def clean_number(field,type,NaN=None,suppr="#"):
    """
    Conversion de chaines de caractères
    en entier ou réel

    Args:
        field: chaine de caractères à convertir
        type: type choisie (int ou float)
        NaN: format choisi pour les données non convertissable
        suppr: caractère devant être supprimer de field avant conversion

    Returns:
        field converti en un entier ou un réel selon type ou NaN
    """
    try:
        if type=="int":
            return int(field.replace(suppr,""))
        elif type=="float":
            return float(field.replace(suppr,""))
    except (ValueError,AttributeError):
        return NaN

def clean_duration(field,NaN=None):
    """
    Conversion de chaines de caractères en datetime

    Args:
        field: chaine de caractères à convertir
        NaN: format choisi pour les données non convertissable
    
    Returns:
        field converti en datetime ou NaN
    """
    NA=['','None',"N/A",'Unknown',None,[],dict(),set(),NaN]
    field=clean_string(field,NaN=NaN)
    if field not in NA and type(field)==type(""):
        d, field_list= set(["hr.","min.","sec."]), field.split(" ")
        if len(field)>1 and not set(field_list).isdisjoint(d):
            d=dict([(key,int(field_list[field_list.index(key)-1])) if key in field_list[1:] else (key,0) for key in d])
            return datetime(year=MAXYEAR,month=12,day=31,hour=d["hr."],minute=d["min."],second=d["sec."],microsecond=0)
    return NaN

def find_month(name):
    """
    Conversion d'un nom de mois en numéro de mois

    Args:
        name: nom du mois

    Returns:
        numéro du mois correspondant à name
    """
    months=["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
    if clean_string(name) in months:
        nb=dict([(months[i],i+1) for i in range(len(months))])
        return nb[clean_string(name)]
    return None

def to_date(day=None,month=None,year=None,NaN=None):
    """
    Création de datetime à partir
    d'un n° de jour, d'un n° de mois et d'une d'année

    Args:
        day: numéro du jour
        month: numéro du mois
        year: année au format yyyy
        NaN: format choisi pour les données non convertissables

    Returns:
        datetime correspondant au day, month et year saisis ou Nan
    """
    try:
        d=clean_number(day,"int",suppr=",")
        m=find_month(month)
        y=clean_number(year,"int")
        return datetime(day=d,month=m,year=y)
    except (TypeError, ValueError):
        try:
            return datetime(month=m,year=y)
        except (TypeError, ValueError):
            if y!=None and y>1000:
                return y
            return NaN

def clean_aired(field,NaN=None):
    """
    Conversion d'une chaine de caractères
    en une date de début et une date de fin

    Args:
        field: chaine de caractères à convertir de format '* to *'
        NaN: format choisi pour les données non convertissables

    Returns:
        dict contenant ayant au max. 2 clés start et end associés
        à des datetimes ou NaN
    """
    NA=['','None',"N/A",'Unknown',"?",None,[],dict(),set(),NaN]
    res=clean_string(field)
    if res not in NA:
        for key in ["Aired:","Premiered:"]:
            if key=="Aired:" and key in res.keys() and res[key] not in NA:
                res[key]=res[key].split(" to ")
                if len(res[key])==2:
                    res[key]=[date.split(" ") for date in res[key]]
                    res[key]=[to_date(date[1],date[0],date[2]) if len(date)==3 
                            else NaN for date in res[key]]
                elif len(res[key])==1:
                    res[key]=res[key][0].split(" ")
                    res[key]=[to_date(year=res[key][0]) if len(res[key])==1
                        else to_date(res[key][1], res[key][0],res[key][2]) if len(res[key])==3
                        else NaN]+[NaN]
            elif key=="Premiered:" and key in res.keys() and res[key] not in NA:
                if len(res[key].split(" "))==2:
                    res[key]=res[key].split(" ")
            else:
                res[key]=[NaN,NaN]
        res_key=["start","end","season","year"]
        res_val=[res["Aired:"][0],res["Aired:"][1],res["Premiered:"][0],res["Premiered:"][1]]
        if res_val[0] in NA and res_val[-1] not in NA:
            res_val[0]=res_val[-1]
        res_val[-2],res_val[-1]=None,None
        res= dict([(key,val) for key,val in zip(res_key,res_val) if val not in NA])
        if res not in NA:
            return res
    return NaN


class MongoPipeline(object):

    collection_name = 'myanimelist'

    def open_spider(self, spider):
        """
        Ouverture de la BDD
        """
        self.client = pymongo.MongoClient("mongo")
        self.db = self.client["anime"]

    def close_spider(self, spider):
        """
        Fermeture de la BDD
        """
        self.client.close()

    def process_item(self, item, spider):
        """
        Insertion de l'AnimeItem courant précédemment 
        nettoyé dans la collection myanimelist
        """
        self.db[self.collection_name].insert_one(dict(item))
        return item
