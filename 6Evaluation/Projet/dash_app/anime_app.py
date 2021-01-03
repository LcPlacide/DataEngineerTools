# -*- coding: Utf-8 -*-
# 
# Imports
#
import dash
import dash_core_components as dcc
import dash_html_components as html
import pymongo
import datetime
from datetime import time, MAXYEAR, timedelta

from anime_request import make_request, select_anime, init_components


#
# Data
#

client = pymongo.MongoClient()
database = client.anime
collection = database.myanimelist
options=init_components(collection)

#
# Main
#

if __name__ == '__main__':

    app = dash.Dash(__name__) 

    app.layout=html.Div(children=[
        # Dropdown Type
        html.H3('Type:'),
        dcc.Dropdown(id='type_drop',
            options=[{'label':Type,'value':Type} for Type in options["Type_val"]+["All types"]],
            value=["All types"],
            multi=True
        ),

        # Dropdown Rated
        html.H3('Rated:'),
        dcc.Dropdown(id='rating_drop',
            options=[{'label':rating,'value':rating} for rating in options["rating_val"]+["All ratings"]],
            value=["All ratings"],
            multi=True
        ),

        # Dropdown Status
        html.H3('Status:'),
        dcc.Dropdown(id='status_drop',
            options=[{'label':status,'value':status} for status in options["status_val"]+["All status"]],
            value=["All status"],
            multi=True
        ),

        # RangeSlider score
        html.H3("Score:"),
        dcc.RangeSlider(id='score_slider',
            min=0,
            max=10,
            step=1,
            marks=dict([(i,str(i)) for i in range(11)]),
            value=[5, 10]
        ), 

        # RangeSlider duration
        html.H3("Duration:"),
        dcc.RangeSlider(id='duration_slider',
            min=options["duration_val"][0],
            max=options["duration_val"][-1],
            step=None,
            marks=dict([(v,l) for v,l in zip(options["duration_val"],options["duration_label"])]),
            value=[options["duration_val"][0], options["duration_val"][4]]
        ), 

        # RangeSlider episodes
        html.H3('Episodes:'),
        dcc.RangeSlider(id='episodes_slider',
            min=options["episodes_val"][0],
            max=options["episodes_val"][-1],
            step=0.01,
            marks=dict([(v,str(v)) for v in options["episodes_val"]]),
            value=[options["episodes_val"][0], options["episodes_val"][4]]
        ),

        # RangeSlider popularity
        html.H3('Popularity:'),
        dcc.RangeSlider(id='popularity_slider',
            min=options["popularity_val"][0],
            max=options["popularity_val"][-1],
            step=None,
            marks=dict([(v,"{}k".format(v//1000)) for v in options["popularity_val"]]),
            value=[options["popularity_val"][3], options["popularity_val"][-1]]
        ),  

        # RangeSlider ranked
        html.H3('Ranked:'),
        dcc.RangeSlider(id='ranked_slider',
            min=options["ranked_val"][0],
            max=options["ranked_val"][-1],
            step=None,
            marks=dict([(v,str(v//1000)+"k") if (v//1000)!=0 else (v,str(v)) for v in options["ranked_val"]]),
            value=[options["ranked_val"][0], options["ranked_val"][3]]
        ), 
        
        # RangeSlider start year
        html.H3('Start year:'),
        dcc.RangeSlider(id='year_slider',
            min=options["year_val"][0],
            max=options["year_val"][-1],
            step=None,
            marks=dict([(v,str(v)) for v in options["year_val"]]),
            value=[options["year_val"][2], options["year_val"][-1]]
        ),   

        # Checklist genres
        html.H3('Genres:'),
        dcc.RadioItems(id='genres_radio',
            options=[{'label': v, 'value': v} for v in options["radio_genres"]],
            value='All genres',
            labelStyle={'display': 'inline-block'}),
        dcc.Checklist(id='genres_check',
            options=[{'label':v+"    ",'value':v} for v in options["genres_val"]],
            labelStyle={'display': 'inline-block'},
            value=[]
        ), 

        # Dropdown producers
        html.H3('Producers:'),
        dcc.RadioItems(id='producers_radio',
            options=[{'label': v, 'value': v} for v in options["radio_producers"]],
            value='All producers',
            labelStyle={'display': 'inline-block'}),
        dcc.Dropdown(id='producers_drop',
            options=[{'label':prod,'value':prod} for prod in options["producers_val"]],
            value=[],
            multi=True
        ), 

        # Résultat de la requête
        html.Div(id='mongo_request')
    ])


    # Mise à jour de la requête mongo
    @app.callback(
        dash.dependencies.Output('mongo_request', 'children'),
        [dash.dependencies.Input('type_drop', 'value'),
        dash.dependencies.Input('rating_drop', 'value'),
        dash.dependencies.Input('status_drop', 'value'),
        dash.dependencies.Input('score_slider', 'value'),
        dash.dependencies.Input('duration_slider', 'value'),
        dash.dependencies.Input('episodes_slider', 'value'),
        dash.dependencies.Input('popularity_slider', 'value'),
        dash.dependencies.Input('ranked_slider', 'value'),
        dash.dependencies.Input('year_slider', 'value'),
        dash.dependencies.Input('genres_radio', 'value'),
        dash.dependencies.Input('genres_check', 'value'),
        dash.dependencies.Input('producers_radio', 'value'),
        dash.dependencies.Input('producers_drop', 'value'),
        dash.dependencies.Input('year_slider', 'value')])
    def anime_request(Type,rating,status,score,duration,episodes,popularity,ranked,year,genres_r,genres_c,producers_r,producers_d,start_year):
        request=make_request(Type,rating,status,score,duration,episodes,popularity,ranked,year,genres_r,genres_c,producers_r,producers_d,start_year)
        selection=select_anime(request,collection,max_result=1)
        return str(selection) 


    #
    # RUN APP
    #

    app.run_server(debug=True)