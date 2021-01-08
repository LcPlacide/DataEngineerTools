# -*- coding: Utf-8 -*-
# 
# Imports
#
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import pymongo
import datetime
from datetime import time, MAXYEAR, timedelta
from dash.dependencies import Input, Output, State
from controls import init_components, make_request, select_anime, print_infos, anime_recommandation2,popup

#
# Data
#
#client = pymongo.MongoClient()
client = pymongo.MongoClient("mongo")
database = client.anime
collection = database.myanimelist
options=init_components(collection)

#
# Structure
#
def build_banner():
    return html.Div(
            [html.Div([html.Img(
                            src=app.get_asset_url("dash-logo.png"),
                            id="plotly-image",
                            style={"height": "60px",
                                   "width": "auto",
                                   "margin-bottom": "25px"}
                        )], className="one-third column",
                ),
                html.Div([html.Div([html.H3("ANIMES RECOMMANDATION PROJECT",
                                    style={"margin-bottom": "0px"}),
                          html.H5("Advance search & Recommandation by other titles", 
                                style={"margin-top": "0px"})
                        ])
            ], className="one-half column", id="title"),

            html.Div([
                dcc.ConfirmDialogProvider(
                            children=html.Button("Learn More", id="learn-more-button"),
                            id='learn_popup',
                            message=popup
                        )
                #html.Button("Learn More", id="learn-more-button")
                    ], className="one-third column", id="button"
                ),
            ],
            id="header",
            className="row flex-display",
            style={"margin-bottom": "25px"},
        )

def build_tabs():
    return html.Div(
        id="tabs",
        className="tabs",
        children=[
            dcc.Tabs(
                id="app-tabs",
                value="tab2",
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
                        label="Recommandation",
                        value="tab2",
                        className="custom-tab",
                        selected_className="custom-tab--selected",
                    ),
                ],
            )
        ],
    )

def build_advance_search():
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
                        dcc.Dropdown(id='status_drop',
                                options=[{'label':status,'value':status} 
                                            for status in options["status_val"]+["All status"]],
                                value=["All status"],
                                multi=True
                        ),
                        html.P("Filter by rating:", className="control_label"),
                        dcc.Dropdown(id='rating_drop',
                            options=[{'label':rating,'value':rating} for rating in options["rating_val"]+["All ratings"]],
                            value=["All ratings"],
                            multi=True
                        ),
                        html.P("Filter by type:", className="control_label"),
                        dcc.Dropdown(id='type_drop',
                                options=[{'label':Type,'value':Type} for Type in options["Type_val"]+["All types"]],
                                value=["All types"],
                                multi=True
                        ),
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
                                dcc.Dropdown(id='producers_drop',
                                        options=[{'label':prod,'value':prod} for prod in options["producers_val"]],
                                        value=[],
                                        multi=True
                                    )], className="mini_container",
                            ),
                            html.Div([ 
                                html.P("Filter by genres:", className="control_label"),       
                                dcc.RadioItems(id='genres_radio',
                                        options=[{'label': v, 'value': v} for v in options["radio_genres"]],
                                        value='All genres',
                                        labelStyle={'display': 'inline-block'}
                                ),
                                dcc.Checklist(id='genres_check',
                                        options=[{'label':v,'value':v} for v in options["genres_val"]],
                                        labelStyle={'display': 'inline-block'},
                                        value=[]
                                )],className="pretty_container",
                            ),
                            html.Div([
                                html.Div([html.Button("Submit",id="submit-button")],className='mini_container'),
                                html.Div([html.Button("Back",id="back-button")],className='mini_container'),
                                html.Div([html.Button("Next",id="next-button")],className='mini_container')
                            ],className="row container-display",style={"margin-left":"auto","margin-right":"auto"})
                        ],id="right-column",className="eight columns")
                    ],className="row flex-display"),
                html.Div([
                        html.Div([dcc.Markdown(id="anime_infos")],className="pretty_container six columns"),
                        html.Div([
                            dcc.Markdown(id="result_idx",
                                        style={"margin-left":"auto","margin-right":"auto","text-align":"center"}),
                            html.Img(id="anime_image",
                                style={"display":"block",
                                        "margin-bottom":"auto", "margin-top":"auto",
                                        "margin-left": "auto", "margin-right":"auto"}),
                            dcc.Markdown("***\n***Related anime: ***",id="table_name"),
                            dash_table.DataTable(id='related_anime_table',
                                                style_cell={'whiteSpace': 'normal','height': 'auto'},
                                                columns=[{"name": i, "id": i} for i in ["Link","Titles"]])
                            ],className="pretty_container five columns")
                    ], className="inline-block")
            ])   
        ]

def build_recommandation():
    return [html.Div([
                html.Div([
                    html.P("Enter the titles of animes you enjoyed: ", className="control_label"),
                    html.Div([
                        html.Div([dcc.Dropdown(id='titles_search_bar', options= options["titles"], value=[], multi=True)
                            ],className='ten columns'),
                        html.Button("Submit",id="submit-button-reco")],className='row display'),
                    html.Div([html.P("Max. number of recommandations:",className="control_label"),
                        dcc.Input(id="max-result-input", placeholder='Enter a value...',type='number',value=100,min=1),
                        dcc.Checklist(id="print-all-check", options=[{'label':"See all results",'value':"See all results"}],value=[]),
                        ],className='row flex-display'),
                    ],className='pretty_container eleven columns'),
                    html.Div([
                            html.Div([html.Div([html.Button("Back",id="back-button-reco")],className='mini_container'),
                            html.Div([html.Button("Next",id="next-button-reco")],className='mini_container')
                            ],className="row container-display",
                              style={'textAlign':'center','width': '220px','margin':'auto'})
                    ],className='eleven columns'),
                html.Div([
                    html.Div([dcc.Markdown(id="anime_infos_reco")],className="pretty_container six columns"),
                    html.Div([
                        dcc.Markdown(id="result_idx_reco",
                                    style={"margin-left":"auto","margin-right":"auto","text-align":"center"}),
                        html.Img(id="anime_image_reco",
                            style={"display":"block",
                                    "margin-bottom":"auto", "margin-top":"auto",
                                    "margin-left": "auto", "margin-right":"auto"}),
                        dcc.Markdown("***\n***Related anime: ***",id="table_name_reco"),
                        dash_table.DataTable(id='related_anime_table_reco',
                                style_cell={'whiteSpace': 'normal','height': 'auto'},
                                columns=[{"name": i, "id": i} for i in ["Link","Titles"]])
                        ],className="pretty_container five columns")
                    ], className="inline-block")
                ])
            ]

#
# Main
#

if __name__ == '__main__':

    app = dash.Dash(__name__,suppress_callback_exceptions=True) 

    app.layout=html.Div(children=[
        build_banner(),
        html.Div(
            id="app-container",
            children=[
                build_tabs(),
                # Main app
                html.Div(id="app-content"),
            ],
        ),
    ])

    @app.callback(
        [Output("app-content", "children")],
        [Input("app-tabs", "value")],
    )
    def render_tab_content(tab_switch):
        global selection
        selection=[]
        global current_result_idx
        current_result_idx=0
        if tab_switch == "tab1":
            return build_advance_search()
        elif tab_switch == "tab2":
            return build_recommandation()

    @app.callback(
        [Output("anime_infos","children"),
        Output("anime_image","src"),
        Output("result_idx","children"),
        Output("related_anime_table","data")],
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
    def print_advance_search_result(submit,back,next,
        Type,rating,status,
        score_s,score_c,duration_s,
        duration_c,episodes_s,episodes_c,
        year_s,year_c,genres_r,
        genres_c,producers_r,producers_d):
        changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
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
        elif 'next-button' in changed_id:
            if len(selection)>0 and current_result_idx!=len(selection)-1:
                current_result_idx+=1
        elif 'back-button' in changed_id:
            if len(selection)>0 and current_result_idx!=0:
                current_result_idx-=1
        return print_infos(selection,current_result_idx)
    
    @app.callback(
        [Output("anime_infos_reco","children"),
        Output("anime_image_reco","src"),
        Output("result_idx_reco","children"),
        Output("related_anime_table_reco","data"),],
        [Input("submit-button-reco","n_clicks"),
        Input("back-button-reco","n_clicks"),
        Input("next-button-reco","n_clicks"),
        Input('titles_search_bar', 'value'),
        Input('print-all-check','value'),
        Input('max-result-input','value')]
    )
    def print_recommandation_result(submit,back,next,titles,allResult,max_result):
        changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
        if 'submit-button-reco' in changed_id and len(titles)>0:
            global current_result_idx
            current_result_idx=0
            global selection
            if allResult!=["See all results"]:
                selection=anime_recommandation2(titles,collection,options,max_result=max_result)
            else:
                selection=anime_recommandation2(titles,collection,options,max_result=10**50)
        elif 'next-button-reco' in changed_id and len(titles)>0:
            if len(selection)>0 and current_result_idx!=len(selection)-1:
                current_result_idx+=1
        elif 'back-button-reco' in changed_id and len(titles)>0:
            if len(selection)>0 and current_result_idx!=0:
                current_result_idx-=1

        return print_infos(selection,current_result_idx)

# Main
if __name__ == "__main__":
    app.run_server(debug=True, port=8050, host="0.0.0.0")
