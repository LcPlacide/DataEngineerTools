# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from datetime import datetime
import pymongo

server_name=None
server_name="mongo"

class AnimescrawlerPipeline:
    def process_item(self, item, spider):
        if item["main_title"]:
            item["main_title"]=clean_string(item["main_title"])
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
        return item

def clean_string(field,as_set=False,to_join=False,NaN=None):
    NA=['','None',"N/A",'Unknown',None,[],dict(),set(),NaN]
    if type(field)==str and field.strip() not in NA:
        return field.strip()
    elif type(field)==list and field not in NA:
        res=[elt.strip() for elt in field if elt.strip() not in NA]
        if to_join and res not in NA:
            res=" ".join(res)
            if res not in NA and res.find("No synopsis")==-1:
                return res
        elif as_set and res not in NA:
            return list(set(res))
        if res not in NA:
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

def clean_number(field,type,NaN=None):
    try:
        if type=="int":
            return int(field.replace("#",""))
        elif type=="float":
            return float(field.replace("#",""))
    except ValueError:
        return NaN

def clean_duration(field,NaN=None):
    NA=['','None',"N/A",'Unknown',None,[],dict(),set(),NaN]
    field=clean_string(field,NaN=NaN)
    if field not in NA and type(field)==type(""):
        d, field_list= set(["hr.","min.","sec."]), field.split(" ")
        if len(field)>1 and not set(field_list).isdisjoint(d):
            d=dict([(key,int(field_list[field_list.index(key)-1])) if key in field_list[1:] else (key,0) for key in d])
            return datetime.today().replace(hour=d["hr."],minute=d["min."],second=d["sec."],microsecond=0)
    return NaN

class MongoPipeline(object):

    collection_name = 'scrapy_items'

    def open_spider(self, spider):
        if server_name!=None:
            self.client = pymongo.MongoClient(server_name)
        else:
            self.client = pymongo.MongoClient()
        self.db = self.client["anime"]

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        self.db[self.collection_name].insert_one(dict(item))
        return item