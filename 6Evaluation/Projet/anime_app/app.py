# -*- coding: Utf-8 -*-
# 
# Imports
#
from flask import Flask, flash, redirect, render_template, \
     request, url_for,redirect
from werkzeug.middleware.dispatcher  import DispatcherMiddleware 
from werkzeug.serving import run_simple 
from random import randint
from forms import MyForm   
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import pymongo
import datetime
import json
from datetime import time, MAXYEAR, timedelta
from dash.dependencies import Input, Output, State
from controls import init_components, make_request, select_anime, print_infos, anime_Recommendation,popup

#
# Data
#

# Ouverture de la base
client = pymongo.MongoClient("mongo")
database = client.anime
collection = database.myanimelist

# Chargement éventuel de la BDD originale
if "anime" not in client.list_database_names():
    with open("Original_BDD.json") as f:
        DOCUMENTS = json.load(f)
    for i in range(len(DOCUMENTS)):
        DOCUMENTS[i]["_id"]=i
        if DOCUMENTS[i]["duration"]!=None:
            DOCUMENTS[i]["duration"]=datetime.datetime.strptime(DOCUMENTS[i]["duration"], '%Y-%m-%d %H:%M:%S')
        if DOCUMENTS[i]["aired"]!=None:
            for k in DOCUMENTS[i]["aired"].keys():
                if type(DOCUMENTS[i]["aired"][k])==str and not DOCUMENTS[i]["aired"][k].isdigit():
                    DOCUMENTS[i]["aired"][k]=datetime.datetime.strptime(DOCUMENTS[i]["aired"][k],'%Y-%m-%d %H:%M:%S')
                elif type(DOCUMENTS[i]["aired"][k])==str and DOCUMENTS[i]["aired"][k].isdigit():
                    DOCUMENTS[i]["aired"][k]=int(DOCUMENTS[i]["aired"][k])
    collection.insert_many(DOCUMENTS)

# Création des labels des composants dash
options=init_components(collection)
start_tab="tab1"

#
# Dash app
#

def build_banner():
    """
    Création de la bannière commune
    aux deux onglets de l'app

    Returns:
        div html définissant l'en-tête de l'app
    """
    return html.Div([html.Div([html.A(html.Button("Home", id="home-button",style={"background-color":"#f9f9f9"}),href="http://localhost:8050/home")],className="one-third column"),
                html.Div([html.Div([html.H3("ANIMES Recommendation PROJECT",
                                    style={"margin-bottom": "0px"},id="textopaque"),
                          html.H5("Advance search & Recommendation by other titles", 
                                style={"margin-top": "0px"})
                        ])
            ], className="pretty_container one-half column", id="title",style={"background-color":"#f9f9f9","opacity": "0.85"}),

            html.Div([
                dcc.ConfirmDialogProvider(
                            children=html.Button("Learn More", id="learn-more-button",style={"background-color":"#f9f9f9"}),
                            id='learn_popup',
                            message=popup,
                            
                        )
                #html.Button("Learn More", id="learn-more-button")
                    ], className="one-third column", id="button"
                ),
            ],
            id="header",
            className="row flex-display",
            style={"margin-bottom": "25px"},
        )

def build_tabs(start_tab="tab2"):
    """
    Création des deux onglets
    "Advance search" et "Recommendation
    Args:
        start_tab: tab affiché par défaut

    Returns:
        div html définissant les deux onglets
    """
    return html.Div(
        id="tabs",
        className="tabs",
        children=[
            dcc.Tabs(
                id="app-tabs",
                value=start_tab,
                className="custom-tabs",
                children=[
                    dcc.Tab(
                        id="Ad-search-tab",
                        label="Advance search",
                        value="tab1",
                        className="custom-tab",
                        selected_className="custom-tab--selected",
                    ),
                    dcc.Tab(
                        id="Reco-tab",
                        label="Recommendation",
                        value="tab2",
                        className="custom-tab",
                        selected_className="custom-tab--selected",
                    ),
                ],
            )
        ],style={"background-color":"#f9f9f9","opacity": "0.9"}
    )

def build_advance_search():
    """
    Construction de l'onglet "Advance search"

    Returns:
        liste décrivant la struture de l'onglet
    """
    return [html.Div([
                html.Div([
                    html.Div([
                        html.Div([
                        html.P("Filter by start year:", className="control_label"),
                        dcc.Checklist(id='year_check',
                                    options=[{'label':"Include N\\A",'value':"Include N\\A"}],
                                    value=[]
                        )]),
                        dcc.RangeSlider(id='year_slider',
                                min=0,
                                max=len(options["year_val"])-1,
                                step=None,
                                marks=dict([(i,str(options["year_val"][i])) 
                                        for i in range(len(options["year_val"]))]),
                                value=[2, len(options["year_val"])-1],
                                className="dcc_control",
                        ),
                        html.P("Filter by status:", className="control_label"),
                        html.Div([
                            dcc.Dropdown(id='status_drop',
                                    options=[{'label':status,'value':status} 
                                                for status in options["status_val"]+["All status"]],
                                    value="All status",
                                    multi=False
                            )],id="status_div"),
                        html.P("Filter by rating:", className="control_label"),
                        html.Div([                      
                            dcc.Dropdown(id='rating_drop',
                                options=[{'label':rating,'value':rating} for rating in options["rating_val"]+["All ratings"]],
                                value="All ratings",
                                multi=False
                        )],id="rating_div"),
                        html.P("Filter by type:", className="control_label"),
                        html.Div([
                            dcc.Dropdown(id='type_drop',
                                    options=[{'label':Type,'value':Type} for Type in options["Type_val"]+["All types"]],
                                    value="All types",
                                    multi=False
                        )],id='type_div'),
                        html.P("Filter by score:", className="control_label"),
                        dcc.Checklist(id='score_check',
                                    options=[{'label':"Include N\\A",'value':"Include N\\A"}],
                                    value=[]
                        ),
                        dcc.RangeSlider(id='score_slider',
                                min=0,
                                max=10,
                                step=1,
                                marks=dict([(i,str(i)) for i in range(11)]),
                                value=[5, 10]
                        ), 
                        html.P("Filter by duration:", className="control_label"),
                        dcc.Checklist(id='duration_check',
                                    options=[{'label':"Include N\\A",'value':"Include N\\A"}],
                                    value=[]
                        ),
                        dcc.RangeSlider(id='duration_slider',
                                min=0,
                                max=len(options["duration_val"])-1,
                                step=None,
                                marks=dict([(v,l) for v,l in zip([i for i in range(len(options["duration_val"]))],options["duration_label"])]),
                                value=[0, 4]
                        ),
                        html.P("Filter by episode number:", className="control_label"),
                        dcc.Checklist(id='episodes_check',
                                    options=[{'label':"Include N\\A",'value':"Include N\\A"}],
                                    value=[]
                        ),
                        dcc.RangeSlider(id='episodes_slider',
                                min=0,
                                max=len(options["episodes_val"])-1,
                                step=None,
                                marks=dict([(i,str(options["episodes_val"][i])) for i in range(len(options["episodes_val"]))]),
                                value=[0, 4]
                        ),
                    ], className="pretty_container four columns", id="cross-filter-options"),
                        html.Div([
                            html.Div([
                                html.P("Filter by producers:", className="control_label"),
                                dcc.RadioItems(id='producers_radio',
                                        options=[{'label': v, 'value': v} for v in options["radio_producers"]],
                                        value='All producers',
                                        labelStyle={'display': 'inline-block'}),
                                html.Div([
                                    dcc.Dropdown(id='producers_drop',
                                            options=[{'label':prod,'value':prod} for prod in options["producers_val"]],
                                            value=[],
                                            multi=True
                                        )],id='producers_div')
                                ], className="mini_container",
                            ),
                            html.Div([ 
                                html.P("Filter by genres:", className="control_label"),       
                                dcc.RadioItems(id='genres_radio',
                                        options=[{'label': v, 'value': v} for v in options["radio_genres"]],
                                        value='All genres',
                                        labelStyle={'display': 'inline-block'}
                                ),
                                html.Div([
                                    dcc.Checklist(id='genres_check',
                                            options=[{'label':v,'value':v} for v in options["genres_val"]],
                                            labelStyle={'display': 'inline-block'},
                                            value=[])],id='genres_div')
                                ],className="pretty_container",
                            ),
                            html.Div([
                                html.Div([html.Button("Submit",id="submit-button",className="btn")],className='mini_container'),
                                html.Div([html.Button("Back",id="back-button",className="btn")],className='mini_container'),
                                html.Div([html.Button("Next",id="next-button",className="btn")],className='mini_container')
                            ],className="row container-display",style={"margin-left":"auto","margin-right":"auto"})
                        ],id="right-column",className="eight columns")
                    ],className="row flex-display"),
                html.Div([
                        html.Div([dcc.Markdown(id="anime_infos")],className="pretty_container six columns",style={"background-color":  "rgb(117, 173, 156)"}),
                        html.Div([
                            dcc.Markdown(id="result_idx",
                                        style={"margin-left":"auto","margin-right":"auto","text-align":"center"},),
                            html.Img(id="anime_image",
                                style={"display":"block",
                                        "margin-bottom":"auto", "margin-top":"auto",
                                        "margin-left": "auto", "margin-right":"auto","background-color": "rgb(117, 173, 156)"}),
                            dcc.Markdown("***\n***Related anime: ***",id="table_name",style={"background-color": "rgb(117, 173, 156)"}),
                            dash_table.DataTable(id='related_anime_table',
                                                style_cell={'whiteSpace': 'normal','height': 'auto'},
                                                columns=[{"name": i, "id": i,"presentation":"markdown"} for i in ["Link","Titles"]])
                            ],className="pretty_container five columns",style={"background-color": "rgb(117, 173, 156)"})
                    ], className="inline-block",style={"background-color": "rgb(117, 173, 156)"})
            ],)   
        ]

def build_Recommendation():
    """
    Construction de l'onglet "Recommendation"

    Returns:
        liste définissant la structure de l'onglet
    """
    return [html.Div([
                html.Div([
                    html.P("Enter the titles of animes you enjoyed: ", className="control_label"),
                    html.Div([
                        html.Div([dcc.Dropdown(id='titles_search_bar', options= options["titles"], value=[], multi=True)
                            ],className='ten columns'),
                        html.Button("Submit",id="submit-button-reco",className="btn")],className='row display'),
                    html.Div([html.P("Max. number of Recommendations:",className="control_label"),
                        html.Div([
                            dcc.Input(id="max-result-input", placeholder='Enter a value...',type='number',value=100,min=1)
                            ],id='input_div'),
                        dcc.Checklist(id="print-all-check", options=[{'label':"See all results",'value':"See all results"}],value=[]),
                        ],className='row flex-display'),
                    ],className='pretty_container eleven columns'),
                    html.Div([
                            html.Div([html.Div([html.Button("Back",id="back-button-reco",className="btn")],className='mini_container'),
                            html.Div([html.Button("Next",id="next-button-reco",className="btn")],className='mini_container')
                            ],className="row container-display",
                              style={'textAlign':'center','width': '220px','margin':'auto'})
                    ],className='eleven columns'),
                html.Div([
                    html.Div([dcc.Markdown(id="anime_infos_reco")],className="pretty_container six columns",style={"background-color": "rgb(117, 173, 156)"}),
                    html.Div([
                        dcc.Markdown(id="result_idx_reco",
                                    style={"margin-left":"auto","margin-right":"auto","text-align":"center"}),
                        html.Img(id="anime_image_reco",
                            style={"display":"block",
                                    "margin-bottom":"auto", "margin-top":"auto",
                                    "margin-left": "auto", "margin-right":"auto"}),
                        dcc.Markdown("***\n***Related anime: ***",id="table_name_reco",style={"background-color": "rgb(117, 173, 156)"}),
                        dash_table.DataTable(id='related_anime_table_reco',
                                style_cell={'whiteSpace': 'normal','height': 'auto'},
                                columns=[{"name": i, "id": i,"presentation":"markdown"} for i in ["Link","Titles"]])
                        ],className="pretty_container five columns",style={"background-color": "rgb(117, 173, 156)"})
                    ], className="inline-block",style={"background-color": "rgb(117, 173, 156)"})
                ])
            ]

def update_drop(id,current_val,all_var,options,radio_val=[],permit_disable=True):
    """
    Mise à jour du format des dropdowns
    selon les valeurs sélectionnés

    Args:
        id: identifiant du nouveau dropdown
        current_val: valeurs actuelles du dropdown
        all_val: valeur englobant toutes les possibilités
        options: ensembles des valeurs que peut prendre le dropdown
        radio_val: valeurs des radios items associés au dropdown
        permit_disable: activation de la possibilité de désactivation du dropdown
    
    Return:
        dropdown dont le format à été mis à jour
    """
    if permit_disable and all_var in radio_val:
        to_disable=True
    else:
        to_disable=False
    if all_var in current_val or all_var in radio_val:
        return dcc.Dropdown(id=id,options=options,value=all_var,multi=False,disabled=to_disable)
    return dcc.Dropdown(id=id,options=options,value=current_val,multi=True,disabled=to_disable)

if __name__ == '__main__':

    server = Flask(__name__) 
    app = dash.Dash(__name__,server=server, url_base_pathname='/dash/',suppress_callback_exceptions=True)

    app.layout=html.Div(children=[
        build_banner(),
        html.Div(
            id="app-container",
            children=[
                build_tabs(start_tab),
                html.Div(id="app-content"),
            ],
        ),
    ])

    # Affichage de l'onglet sélectionné dans l'UI
    @app.callback(
        [Output("app-content", "children")],
        [Input("app-tabs", "value")],
    )
    def render_tab_content(tab_switch):
        global selection
        selection=[]
        global current_result_idx
        current_result_idx=0

        # Choix de l'onglet à affiché
        if tab_switch == "tab1":
            return build_advance_search()
        elif tab_switch == "tab2":
            return build_Recommendation()


    # Mise à jours de la liste d'animés selon 
    # les filters sélectionnés dans l'UI
    # de l'onglet "Advance search"
    @app.callback(
        [Output("anime_infos","children"),
        Output("anime_image","src"),
        Output("result_idx","children"),
        Output("related_anime_table","data"),
        Output('type_div', 'children'),
        Output('rating_div', 'children'),
        Output('status_div', 'children'),
        Output('producers_div', 'children'),
        Output('genres_div', 'children')],
        [Input("submit-button","n_clicks"),
        Input("back-button","n_clicks"),
        Input("next-button","n_clicks"),
        Input('type_drop', 'value'),
        Input('rating_drop', 'value'),
        Input('status_drop', 'value'),
        Input('score_slider', 'value'),
        Input('score_check','value'),
        Input('duration_slider', 'value'),
        Input('duration_check','value'),
        Input('episodes_slider', 'value'),
        Input('episodes_check','value'),
        Input('year_slider', 'value'),
        Input('year_check', 'value'),
        Input('genres_radio', 'value'),
        Input('genres_check', 'value'),
        Input('producers_radio', 'value'),
        Input('producers_drop', 'value')]
    )
    def print_advance_search_result(submit,back,next,Type,rating,status,score_s,score_c,duration_s,
        duration_c,episodes_s,episodes_c,year_s,year_c,genres_r,genres_c,producers_r,producers_d):
        changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]

        # Mise à jour des dropdowns et checklist
        type_div=update_drop("type_drop",Type,'All types',
                [{'label':Type,'value':Type} for Type in options["Type_val"]+["All types"]])
        rating_div=update_drop("rating_drop",rating,"All ratings",
                [{'label':rating,'value':rating} for rating in options["rating_val"]+["All ratings"]])
        status_div=update_drop("status_drop",status,"All status",
                [{'label':status,'value':status} for status in options["status_val"]+["All status"]])
        producers_div=update_drop("producers_drop",producers_d,"All producers",
                [{'label':prod,'value':prod} for prod in options["producers_val"]],producers_r,True)
        if "All genres" in genres_r:
            genres_div= dcc.Checklist(id='genres_check',
                                options=[{'label':v,'value':v} for v in options["genres_val"]],
                                labelStyle={'display': 'inline-block'},value=[])
        else:
            genres_div= dcc.Checklist(id='genres_check',
                                options=[{'label':v,'value':v} for v in options["genres_val"]],
                                labelStyle={'display': 'inline-block'},value=genres_c)

        # Lancement de la requête sur l'appui du bouton "submit"
        if 'submit-button' in changed_id:
            global current_result_idx
            current_result_idx=0
            global selection
            request=make_request(Type=Type,rating=rating,status=status,
                                    score={"check":score_c,"slider":score_s},
                                    duration={"check":duration_c,"slider":duration_s,"reco":False},
                                    episodes={"check":episodes_c,"slider":episodes_s,"reco":False},
                                    year={"check":year_c,"slider":year_s},
                                    genres={"radio":genres_r,"check":genres_c},
                                    producers={"radio":producers_r,"drop":producers_d},
                                    options=options)
            selection=select_anime(request,collection,sort={"fields":["score","popularity"],"order":[-1,-1]})
        
        # Défilement des résultats de la requête de sélection d'animés
        elif 'next-button' in changed_id:
            if len(selection)>0 and current_result_idx!=len(selection)-1:
                current_result_idx+=1
        elif 'back-button' in changed_id:
            if len(selection)>0 and current_result_idx!=0:
                current_result_idx-=1
        output=print_infos(selection,current_result_idx)
        return output[0],output[1],output[2],output[3],type_div,rating_div,status_div,producers_div,genres_div
    

    # Mise à jour de la liste de recommandation
    # selon les titres d'animés sélectionnés dans l'UI
    # de l'onglet "Recommendation"
    @app.callback(
        [Output("anime_infos_reco","children"),
        Output("anime_image_reco","src"),
        Output("result_idx_reco","children"),
        Output("related_anime_table_reco","data"),
        Output('input_div','children')],
        [Input("submit-button-reco","n_clicks"),
        Input("back-button-reco","n_clicks"),
        Input("next-button-reco","n_clicks"),
        Input('titles_search_bar', 'value'),
        Input('print-all-check','value'),
        Input('max-result-input','value')]
    )
    def print_Recommendation_result(submit,back,next,titles,allResult,max_result):
        changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]

        # Verrouillage de "producers_drop" selon la valeur de "producers_radio"
        if allResult!=["See all results"]:
                input=dcc.Input(id="max-result-input", placeholder='Enter a value...',type='number',value=max_result,min=1)
                nb_results=max_result
        else:
                input=dcc.Input(id="max-result-input",disabled=True, placeholder='Enter a value...',type='number',value=max_result,min=1)
                nb_results=10**50

        # Lancement de l'algo de recommendations avec l'appui sur "submit"
        if 'submit-button-reco' in changed_id and len(titles)>0:
            global current_result_idx
            current_result_idx=0
            global selection
            selection=anime_Recommendation(titles,collection,options,max_result=nb_results)

        # Défilement des résultats de sélection d'animés
        elif 'next-button-reco' in changed_id and len(titles)>0:
            if len(selection)>0 and current_result_idx!=len(selection)-1:
                current_result_idx+=1
        elif 'back-button-reco' in changed_id and len(titles)>0:
            if len(selection)>0 and current_result_idx!=0:
                current_result_idx-=1
        output=print_infos(selection,current_result_idx)
        return output[0],output[1],output[2],output[3],input

#
# Flask app
#

if __name__ == "__main__":
    server.config['SECRET_KEY'] = 'you-will-never-guess'

    @server.route('/')
    def rien():
        return "Rien ici... <a href='/home'> voir là </a> "

    @server.route('/home', methods=('GET', 'POST'))
    def home():
        form = MyForm()
        res=".*"+str(form.name.data)+".*"
        results=list(collection.find({"main_title" : {"$regex": res,'$options': 'i'}}))
        NA=[[],None,{}]
        NaN=""
        for anime in results:
            for key in anime.keys():
                if anime[key] not in NA:
                    if key=="aired" and "start" in anime[key].keys():
                        if type(anime[key]["start"])==int:
                            anime[key]["start"]=str(anime[key]["start"])
                        elif type(anime[key]["start"])==type(datetime.datetime.today()):
                            anime[key]["start"]=str(anime[key]["start"].date())
                    elif key in ["score","episoded","ranked","popularity"]:
                        anime[key]==str(anime[key])
                    elif key=="main_title":
                        anime["main_title"]={'url':anime["main_title"],"print":anime["main_title"].replace("U+002F","/")}
                    
                else:
                    if key=="aired":
                        anime[key]={"start":NaN}
                    else:
                        anime[key]=NaN
        
                    
        if form.validate_on_submit():
            return render_template('search_bar.html',tasks=results,form=form)
        return render_template('search_bar.html',tasks=results,form=form)

    @server.route('/page/<string:user>')
    def page(user):
        results=list(collection.find({"main_title":user}))
        NA=[[],None,{}]
        NaN=""
        for anime in results:
            for key in anime.keys():
                if anime[key] not in NA:
                    if key=="main_title":
                        anime["main_title"]=anime["main_title"].replace("U+002F","/")
                    elif key=="aired" and "start" in anime[key].keys():
                        if type(anime[key]["start"])==int:
                            anime[key]["start"]=str(anime[key]["start"])
                        elif type(anime[key]["start"])==type(datetime.datetime.today()):
                            anime[key]["start"]=str(anime[key]["start"].date())
                    elif key in ["score","episoded","ranked","popularity","duration"]:
                        anime[key]==str(anime[key])
                    elif type(anime['duration'])==type(datetime.datetime.today()):
                            anime['duration']=str(anime['duration'].time())
                    elif key in ["genres","other_titles","producers"]:
                        anime[key]=", ".join(anime[key])
                    elif key=="aired" and "end" in anime[key].keys():
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

    @server.route('/dash') 
    def render_advance_search(): 
        return redirect('/dash1') 

    app1 = DispatcherMiddleware(server, { '/dash1': app.server}) 
    run_simple('0.0.0.0',8050, app1, use_reloader=True, use_debugger=True, threaded=True)
    app.run_server(debug=True, port=8050, host="0.0.0.0")