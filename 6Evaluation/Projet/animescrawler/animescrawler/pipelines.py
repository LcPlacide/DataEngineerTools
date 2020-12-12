# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import pandas as pd


class AnimescrawlerPipeline:
    def process_item(self, item, spider):
        if item["score"]:
            try:
                item["score"]=float(item["score"])
            except ValueError:
                item["score"]=None
        if item["other_titles"]:
            item["other_titles"]= [elt.strip() for elt in item["other_titles"] if elt.strip()!='']
        if item["producers"]:
            item["producers"]= set(item["producers"])
        if item["ranked_popularity"]:
            item["ranked_popularity"]= {"rank":item["ranked_popularity"][0].replace("#",""),
                                        "popularity":item["ranked_popularity"][1].replace("#","")}
        if item["related_anime"]:
            item["related_anime"]["rownames"]=[elt for elt in item["related_anime"]["rownames"] if elt.find(":")!=-1]
            item["related_anime"] = clean_related_anime(item["related_anime"]["table"], 
                                                item["related_anime"]["rownames"], 
                                                item["related_anime"]["names"])
        if item["duration_rating"]:
            item["duration_rating"] = clean_duration_rating(item["duration_rating"])                             
        return item

def clean_related_anime(table,rowname,name):
    if len(table)>0:
        res,l=[None,[]]*len(rowname),rowname+name
        table=pd.Series(table)
        for elt in l:
            find_elt=table.str.contains(">"+elt+"<",regex=False)
            if find_elt.sum()!=0:
                n=find_elt.argmax()
            else:
                continue
            if elt in name:
                res[n]=res[n]+[elt]
            else:
                res[n]=elt[:len(elt)-1]
        res = dict([(res[i],res[i+1]) for i in range(0,len(res),2) if res[i+1]!=[]])
        return res
    return None

def clean_duration_rating(duration_rating):
    duration_rating = pd.Series([elt.strip() for elt in duration_rating if elt.strip()!='']) 
    duration_line = duration_rating.str.contains("hr.|min.|per ep.").argmax()
    return {"duration":duration_rating.iloc[duration_line],
            "rating":duration_rating.iloc[duration_line+1]}
