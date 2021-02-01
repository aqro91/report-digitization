import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go
from datetime import datetime
import pandas as pd
from datetime import date
import dash_auth


USERNAME_PASSWORD_PAIRS = [['murwy', 'alejandro']]
app = dash.Dash()
auth = dash_auth.BasicAuth(app,USERNAME_PASSWORD_PAIRS)

df = pd.read_csv("produccion.csv", encoding='latin-1')
df = df[["fecha", "TURNO", "hora","orden", "excavadora", "tipo", "tonelaje"]]
df["fecha"] = pd.to_datetime(df.fecha, format = "%d-%m-%y")

resumen = pd.read_csv("resumenxturno.csv", encoding='latin-1')
resumen["fecha"] = pd.to_datetime(resumen.fecha, format = "%d-%m-%y")
resumen['turno'] = resumen.turno.apply(lambda x: str(x).upper())

app.layout = html.Div([
                    html.Div([
                                html.H1("Cerro Corona Producción MUR WY",
                                style={'textAlign': 'center','backgroundColor': '#5DADE2','padding':20, 'color': 'white'})
                                                                ]),
                    html.Div([
                                html.H3("Elegir fecha".title(),style={'paddingRight':'30px'}),
                                dcc.DatePickerSingle(
                                    id='calendario',
                                    date=datetime.today(),
                                    style={'fontSize':24})
                                                                ], style={'display':'inline-block', 'verticalAlign':'top'}),
                    html.Div([
                                html.H3('Elegir Turno', style={'paddingRight':'40px'}),
                                dcc.Dropdown(
                                            id='opciones',
                                            options=[{'label':'Día','value':'Mañana'},
                                                      {'label': 'Noche', 'value': 'Noche'}],
                                            value='Mañana',style={'fontSize':24}
                                                        )
                                ], style={'display':'inline-block'}),
                    html.Div([
                                html.Button(
                                    id='submit-button',
                                    n_clicks=0,
                                    children='MOSTRAR',
                                    style={'fontSize':16, 'marginLeft':'60px', 'backgroundColor': '#F3E512', 'border-radius': '8px',
                                    'padding': '12px 28px', 'border': '2px solid #F3E512','cursor': 'pointer', 'overflow': 'hidden',
                                    'font-weight': 'bold'}
                                    ),
                            ], style={'display':'inline-block'}),
                    dcc.Graph(id= 'figura1'),
                    dcc.Graph(id='figura2'),
                    html.Div([html.H2("Resumen del turno".title())]),
                    html.Div([dcc.Graph(id='figura3')],style={'width':'50%','display':'inline-block'}),
                    html.Div([dcc.Graph(id='figura4')],style={'width':'50%','display':'inline-block'})
])

@app.callback(
    Output('figura1', 'figure'),
    [Input('submit-button', 'n_clicks')],
    [State('calendario', 'date'),
    State('opciones', 'value')])
def update_graph(n_clicks, date, value):
    fecha =  datetime.strptime(date[:10], '%Y-%m-%d')
    df["TURNO"] = df.TURNO.apply(lambda x: str(x).upper())
    df1=df[(df.fecha == fecha) & (df.TURNO == value.upper())]
    df1 =df1.groupby(["hora","orden"]).tonelaje.sum().reset_index().sort_values(by='orden')
    df1["acumulado"] = df1.tonelaje.cumsum()
    data1 = go.Scatter(x= df1.hora, y = df1.acumulado, mode="markers+lines", name="tonelaje acumulado".title())
    data2= go.Scatter(x=df1.hora, y=df1.tonelaje, mode="markers+lines", name="tonelaje por hora".title())
    data = [data1,data2]
    if value == "Mañana":
        layout= go.Layout(title = "Producción En Turno Día".format(value.upper()),xaxis = dict(title = 'Hora'),
        yaxis = dict(title = 'Tonelaje'), hovermode='x')
    else:
        layout= go.Layout(title = "Producción En Turno {}".format(value.title()),xaxis = dict(title = 'Hora'),
        yaxis = dict(title = 'Tonelaje'), hovermode='x')
    fig = go.Figure(data =data, layout=layout)
    return fig

@app.callback(
                Output('figura2','figure'),
                [Input('submit-button','n_clicks')],
                [State('calendario','date'),
                State('opciones','value')])
def segunda_grafica(n_clicks, date, value):
    fecha =  datetime.strptime(date[:10], '%Y-%m-%d')
    df["excavadora"] = df.excavadora.apply(lambda x: str(x).upper())
    df["TURNO"] = df.TURNO.apply(lambda x: str(x).upper())
    turno_dia=pd.DataFrame({'hora':['07:00:00', '08:00:00', '09:00:00', '10:00:00', '11:00:00','12:00:00','13:00:00',
                                '14:00:00', '15:00:00','16:00:00', '17:00:00', '18:00:00'],
                        'orden':[1,2,3,4,5,6,7,8,9,10,11,12]})
    turno_noche=pd.DataFrame({'hora':['19:00:00', '20:00:00', '21:00:00', '22:00:00','23:00:00',
                                  '00:00:00', '01:00:00', '02:00:00', '03:00:00','04:00:00',
                                  '05:00:00', '06:00:00'],
                          'orden': [1,2,3,4,5,6,7,8,9,10,11,12]})
    df1 = df[(df.fecha == fecha)&(df.TURNO==value.upper())]
    lista = df1.excavadora.unique().tolist()
    traces = []
    for x in lista:
        df2=df1[df1.excavadora==x]
        df2=df2.groupby(["hora",'orden']).tonelaje.sum().reset_index().sort_values(by="orden")
        if value.upper() == "MAÑANA":
            df3=pd.merge(turno_dia,df2,left_on="hora",right_on="hora",how="left")
            df3['tonelaje'] = df3.tonelaje.fillna(0)
            grafica = go.Bar(x=df3.hora, y=df3.tonelaje, name=x, text =df3.tonelaje, textposition='auto')
            traces.append(grafica)
        elif value.upper() =="NOCHE":
            df3=pd.merge(turno_noche,df2,left_on="hora",right_on="hora",how="left")
            df3['tonelaje'] = df3.tonelaje.fillna(0)
            grafica = go.Bar(x=df3.hora, y=df3.tonelaje, name=x, text =df3.tonelaje,textposition='auto')
            traces.append(grafica)
    layout=go.Layout(title="Producción por excavadora", barmode="stack")
    fig=go.Figure(data=traces, layout=layout)
    return fig


@app.callback(
    Output('figura3', 'figure'),
    [Input('submit-button', 'n_clicks')],
    [State('calendario', 'date'),
    State('opciones', 'value')])
def tercera_grafica(n_clicks, date, value):
    fecha3 =  datetime.strptime(date[:10], '%Y-%m-%d')
    resumen1 = resumen[(resumen.fecha == fecha3) & (resumen.turno == value.upper())]
    data=[go.Bar(x=resumen1["material"], y=resumen1["toneladas"],text=resumen1["toneladas"],
            textposition='auto')]
    layout = go.Layout(title='Producción por tipo de material'.title(),xaxis = dict(title = 'Tipo de material'.title()),
    yaxis = dict(title = 'Tonelaje'))
    fig = go.Figure(data = data, layout=layout)
    return fig

@app.callback(
                Output('figura4','figure'),
                [Input('submit-button','n_clicks')],
                [State('calendario','date'),
                State('opciones','value')])
def cuarta_grafica(n_clicks, date, value):
    fecha4 =  datetime.strptime(date[:10], '%Y-%m-%d')
    resumen2=resumen[(resumen.fecha == fecha4) & (resumen.turno == value.upper())]
    data= [go.Pie(labels=resumen2["material"], values=resumen2["toneladas"])]
    fig=go.Figure(data=data)
    return fig

if __name__ == '__main__':
    app.run_server()
