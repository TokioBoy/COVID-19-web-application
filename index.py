import dash
import dash_core_components as dcc
import plotly.graph_objs as go
from dash.dependencies import Input, Output
import dash_html_components as html
import pandas as pd

confirmed_link = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv'
death_link = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv'
vaccinations_link = 'https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/vaccinations/vaccinations-by-manufacturer.csv'

confirmed = pd.read_csv(confirmed_link)
deaths = pd.read_csv(death_link)
vaccinations = pd.read_csv(vaccinations_link)

#remove column from data frame
vaccinations = vaccinations.drop(columns = "vaccine")
vaccinations_1 = vaccinations.drop(columns= ["location" , "date"])

# Unpivot data frames
data_first = confirmed.columns[4:]
total_confirmed = confirmed.melt(id_vars=['Province/State', 'Country/Region', 'Lat', 'Long'], value_vars=data_first, var_name='date', value_name='confirmed')
date_second = deaths.columns[4:]
total_deaths = deaths.melt(id_vars=['Province/State', 'Country/Region', 'Lat', 'Long'], value_vars=date_second, var_name='date', value_name='death')

# Merging data frames
covid_data = total_confirmed.merge(right=total_deaths, how='left', on=['Province/State', 'Country/Region', 'date', 'Lat', 'Long'])

# Converting date column from string to proper date format
covid_data['date'] = pd.to_datetime(covid_data['date'])

# grouping data frames
covid_data_1 = covid_data.groupby(['date'])[['confirmed', 'death']].sum().reset_index()

covid_data_2 = covid_data.groupby(['date', 'Country/Region'])[['confirmed', 'death']].sum().reset_index()

covid_data_v = vaccinations.groupby(['date', 'location', 'total_vaccinations']).sum().reset_index()

covid_data_v_2 = vaccinations_1.groupby(['total_vaccinations']).sum().reset_index()



# create dictionary of list
covid_data_dict = covid_data[['Country/Region', 'Lat', 'Long']]
list_locations = covid_data_dict.set_index('Country/Region')[['Lat', 'Long']].T.to_dict('dict')


app = dash.Dash(__name__, meta_tags=[{"name": "viewport", "content": "width=device-width"}])

app.layout = html.Div([
    html.Div([
        html.Div([
            html.Img(src=app.get_asset_url('Covid-logo.png'),
                     id='corona-image',
                     style={
                         "height": "60px",
                         "width": "auto",
                         "margin-bottom": "25px",
                     },
                     )
        ],
            className="one-third column",
        ),
        html.Div([
            html.Div([
                html.H3("COVID-19", style={"margin-bottom": "0px", 'color': 'aquamarine'}),
                html.H5("TRACK COVID-19 CASES", style={"margin-top": "0px", 'color': 'aquamarine'}),
            ])
        ], className="one-half column", id="title"),

        html.Div([
            html.H6('The last update was in: ' + str(covid_data_1['date'].iloc[-1].strftime("%B %d, %Y")) + '  00:01 (UTC)',
                    style={'color': '#DC143C'}),

        ], className="one-third column", id='title1'),

    ], id="header", className="row flex-display", style={"margin-bottom": "25px"}),

    html.Div([
        html.Div([
            html.H6(children='Global Cases',
                    style={
                        'textAlign': 'center',
                        'color': 'white'}
                    ),

            html.P(f"{covid_data_1['confirmed'].iloc[-1]:,.0f}",
                   style={
                       'textAlign': 'center',
                       'color': 'aquamarine',
                       'fontSize': 40}
                   ),

            html.P('new:  ' + f"{covid_data_1['confirmed'].iloc[-1] - covid_data_1['confirmed'].iloc[-2]:,.0f} "
                   + ' (' + str(round(((covid_data_1['confirmed'].iloc[-1] - covid_data_1['confirmed'].iloc[-2]) /
                                       covid_data_1['confirmed'].iloc[-1]) * 100, 2)) + '%)',
                   style={
                       'textAlign': 'center',
                       'color': 'aquamarine',
                       'fontSize': 15,
                       'margin-top': '-18px'}
                   )], className="card_container three columns",
        ),

        html.Div([
            html.H6(children='Global Vaccinations',
                    style={
                        'textAlign': 'center',
                        'color': 'white'}
                    ),

            html.P(f"{covid_data_v_2['total_vaccinations'].iloc[-1]:,.0f}",
                   style={
                       'textAlign': 'center',
                       'color': 'Blue',
                       'fontSize': 40}
                   ),

            html.P('new:  ' + f"{covid_data_v_2['total_vaccinations'].iloc[-1] - covid_data_v_2['total_vaccinations'].iloc[-2]:,.0f} "
                   + ' (' + str(round(((covid_data_v_2['total_vaccinations'].iloc[-1] - covid_data_v_2['total_vaccinations'].iloc[-2]) /
                                      covid_data_v_2['total_vaccinations'].iloc[-1]) * 100, 2)) + '%)',
                   style={
                       'textAlign': 'center',
                       'color': 'Blue',
                       'fontSize': 15,
                       'margin-top': '-18px'}
                   )], className="card_container three columns",
        ),


        html.Div([
            html.H6(children='Global Deaths',
                    style={
                        'textAlign': 'center',
                        'color': 'white'}
                    ),

            html.P(f"{covid_data_1['death'].iloc[-1]:,.0f}",
                   style={
                       'textAlign': 'center',
                       'color': '#dd1e35',
                       'fontSize': 40}
                   ),

            html.P('new:  ' + f"{covid_data_1['death'].iloc[-1] - covid_data_1['death'].iloc[-2]:,.0f} "
                   + ' (' + str(round(((covid_data_1['death'].iloc[-1] - covid_data_1['death'].iloc[-2]) /
                                       covid_data_1['death'].iloc[-1]) * 100, 2)) + '%)',
                   style={
                       'textAlign': 'center',
                       'color': '#dd1e35',
                       'fontSize': 15,
                       'margin-top': '-18px'}
                   )], className="card_container three columns",
        )

        
        

    ], className="row flex-display"),

    html.Div([
        html.Div([

                    html.P('Select Country:', className='fix_label',  style={'color': 'white'}),

                     dcc.Dropdown(id='w_countries',
                                  multi=False,
                                  clearable=True,
                                  value='US',
                                  placeholder='Select Countries',
                                  options=[{'label': c, 'value': c}
                                           for c in (covid_data['Country/Region'].unique())], className='dcc_compon'),

                     html.P('New Cases : ' + '  ' + ' ' + str(covid_data_2['date'].iloc[-1].strftime("%B %d, %Y")) + '  ', className='fix_label',  style={'color': 'white', 'text-align': 'center'}),
                     dcc.Graph(id='confirmed', config={'displayModeBar': False}, className='dcc_compon',
                     style={'margin-top': '20px'},
                     ),

                      dcc.Graph(id='death', config={'displayModeBar': False}, className='dcc_compon',
                      style={'margin-top': '20px'},
                      ),

        ], className="create_container three columns", id="cross-filter-options"),
            html.Div([
                      dcc.Graph(id='pie_chart',
                              config={'displayModeBar': 'hover'}),
                              ], className="create_container four columns"),

                    html.Div([
                        dcc.Graph(id="line_chart")

                    ], className="create_container five columns"),

        ], className="row flex-display"),

html.Div([
        html.Div([
            dcc.Graph(id="map")], className="create_container1 twelve columns"),

            ], className="row flex-display"),

    ], id="mainContainer",
    style={"display": "flex", "flex-direction": "column"})

@app.callback(
    Output('confirmed', 'figure'),
    [Input('w_countries', 'value')])
def update_confirmed(w_countries):
    covid_data_2 = covid_data.groupby(['date', 'Country/Region'])[['confirmed', 'death']].sum().reset_index()

    value_confirmed = covid_data_2[covid_data_2['Country/Region'] == w_countries]['confirmed'].iloc[-1] - covid_data_2[covid_data_2['Country/Region'] == w_countries]['confirmed'].iloc[-2]
    delta_confirmed = covid_data_2[covid_data_2['Country/Region'] == w_countries]['confirmed'].iloc[-2] - covid_data_2[covid_data_2['Country/Region'] == w_countries]['confirmed'].iloc[-3]
    return {
            'data': [go.Indicator(
                    mode='number+delta',
                    value=value_confirmed,
                    delta={'reference': delta_confirmed,
                              'position': 'right',
                              'valueformat': ',g',
                              'relative': False,

                              'font': {'size': 15}},
                    number={'valueformat': ',',
                            'font': {'size': 20},

                               },
                    domain={'y': [0, 1], 'x': [0, 1]})],
            'layout': go.Layout(
                title={'text': 'New Confirmed',
                       'y': 1,
                       'x': 0.5,
                       'xanchor': 'center',
                       'yanchor': 'top'},
                font=dict(color='aquamarine'),
                paper_bgcolor='#191b1a',
                plot_bgcolor='#191b1a',
                height=50
                ),

            }

@app.callback(
    Output('death', 'figure'),
    [Input('w_countries', 'value')])
def update_confirmed(w_countries):
    covid_data_2 = covid_data.groupby(['date', 'Country/Region'])[['confirmed', 'death']].sum().reset_index()

    value_death = covid_data_2[covid_data_2['Country/Region'] == w_countries]['death'].iloc[-1] - covid_data_2[covid_data_2['Country/Region'] == w_countries]['death'].iloc[-2]
    delta_death = covid_data_2[covid_data_2['Country/Region'] == w_countries]['death'].iloc[-2] - covid_data_2[covid_data_2['Country/Region'] == w_countries]['death'].iloc[-3]
    return {
            'data': [go.Indicator(
                    mode='number+delta',
                    value=value_death,
                    delta={'reference': delta_death,
                              'position': 'right',
                              'valueformat': ',g',
                              'relative': False,

                              'font': {'size': 15}},
                    number={'valueformat': ',',
                            'font': {'size': 20},

                               },
                    domain={'y': [0, 1], 'x': [0, 1]})],
            'layout': go.Layout(
                title={'text': 'New Death',
                       'y': 1,
                       'x': 0.5,
                       'xanchor': 'center',
                       'yanchor': 'top'},
                font=dict(color='#dd1e35'),
                paper_bgcolor='#191b1a',
                plot_bgcolor='#191b1a',
                height=50
                ),

            }
# Creates pie chart
@app.callback(Output('pie_chart', 'figure'),
              [Input('w_countries', 'value')])

def update_graph(w_countries):
    covid_data_2 = covid_data.groupby(['date', 'Country/Region'])[['confirmed', 'death']].sum().reset_index()
    new_confirmed = covid_data_2[covid_data_2['Country/Region'] == w_countries]['confirmed'].iloc[-1]
    new_death = covid_data_2[covid_data_2['Country/Region'] == w_countries]['death'].iloc[-1]
    colors = ['aquamarine', '#dd1e35', 'green', 'gold']

    return {
        'data': [go.Pie(labels=['Confirmed', 'Death'],
                        values=[new_confirmed, new_death],
                        marker=dict(colors=colors),
                        hoverinfo='label+value+percent',
                        textinfo='label+value',
                        textfont=dict(size=13),
                        hole=.7,
                        rotation=45


                        )],

        'layout': go.Layout(
            plot_bgcolor='#191b1a',
            paper_bgcolor='#191b1a',
            hovermode='closest',
            title={
                'text': 'Total Cases In ' + (w_countries),


                'y': 0.93,
                'x': 0.5,
                'xanchor': 'center',
                'yanchor': 'top'},
            titlefont={
                       'color': 'white',
                       'size': 20},
            legend={
                'orientation': 'h',
                'bgcolor': '#191b1a',
                'xanchor': 'center', 'x': 0.5, 'y': -0.07},
            font=dict(
                family="sans-serif",
                size=12,
                color='white')
            ),


        }

# Create bar chart

@app.callback(Output('line_chart', 'figure'),
              [Input('w_countries', 'value')])
def update_graph(w_countries):
    covid_data_2 = covid_data.groupby(['date', 'Country/Region'])[['confirmed', 'death']].sum().reset_index()
# Confirmed per day
    covid_data_3 = covid_data_2[covid_data_2['Country/Region'] == w_countries][['Country/Region', 'date', 'confirmed']].reset_index()
    covid_data_3['daily confirmed'] = covid_data_3['confirmed'] - covid_data_3['confirmed'].shift(1)
    covid_data_3['Rolling Ave.'] = covid_data_3['daily confirmed'].rolling(window=7).mean()

    return {
        'data': [go.Bar(x=covid_data_3[covid_data_3['Country/Region'] == w_countries]['date'].tail(30),
                        y=covid_data_3[covid_data_3['Country/Region'] == w_countries]['daily confirmed'].tail(30),

                        name='Daily confirmed',
                        marker=dict(
                            color='#E75480'),
                        hoverinfo='text',
                        hovertext=
                        '<b>Date</b>: ' + covid_data_3[covid_data_3['Country/Region'] == w_countries]['date'].tail(30).astype(str) + '<br>' +
                        '<b>Daily confirmed</b>: ' + [f'{x:,.0f}' for x in covid_data_3[covid_data_3['Country/Region'] == w_countries]['daily confirmed'].tail(30)] + '<br>' +
                        '<b>Country</b>: ' + covid_data_3[covid_data_3['Country/Region'] == w_countries]['Country/Region'].tail(30).astype(str) + '<br>'


                        ),
                 go.Scatter(x=covid_data_3[covid_data_3['Country/Region'] == w_countries]['date'].tail(30),
                            y=covid_data_3[covid_data_3['Country/Region'] == w_countries]['Rolling Ave.'].tail(30),
                            mode='lines',
                            name='Rolling average of the last seven days - daily confirmed cases',
                            line=dict(width=3, color='aquamarine'),
                            hoverinfo='text',
                            hovertext=
                            '<b>Date</b>: ' + covid_data_3[covid_data_3['Country/Region'] == w_countries]['date'].tail(30).astype(str) + '<br>' +
                            '<b>Rolling Ave.(last 7 days)</b>: ' + [f'{x:,.0f}' for x in covid_data_3[covid_data_3['Country/Region'] == w_countries]['Rolling Ave.'].tail(30)] + '<br>'
                            )],

                                
        'layout': go.Layout(
             plot_bgcolor='#191b1a',
             paper_bgcolor='#191b1a',
             title={
                'text': 'Last 30 Days Confirmed Cases In ' + (w_countries),
                'y': 0.93,
                'x': 0.5,
                'xanchor': 'center',
                'yanchor': 'top'},
             titlefont={
                        'color': 'white',
                        'size': 20},

             hovermode='x',
             margin = dict(r = 0),
             xaxis=dict(title='<b>Date</b>',
                        color='white',
                        showline=True,
                        showgrid=True,
                        showticklabels=True,
                        linecolor='white',
                        linewidth=2,
                        ticks='outside',
                        tickfont=dict(
                            family='Arial',
                            size=12,
                            color='white'
                        )

                ),

             yaxis=dict(title='<b>Daily confirmed Cases</b>',
                        color='white',
                        showline=True,
                        showgrid=True,
                        showticklabels=True,
                        linecolor='white',
                        linewidth=2,
                        ticks='outside',
                        tickfont=dict(
                           family='Arial',
                           size=12,
                           color='white'
                        )

                ),

            legend={
                'orientation': 'h',
                'bgcolor': '#191b1a',
                'xanchor': 'center', 'x': 0.5, 'y': -0.3},
                          font=dict(
                              family="sans-serif",
                              size=12,
                              color='white'),

                 )

    }

# Creates scattermapbox
@app.callback(Output('map', 'figure'),
              [Input('w_countries', 'value')])

def update_graph(w_countries):
    covid_data_3 = covid_data.groupby(['Lat', 'Long', 'Country/Region'])[['confirmed', 'death']].max().reset_index()
    if w_countries:
        zoom = 4
        zoom_lat = list_locations[w_countries]['Lat']
        zoom_lon = list_locations[w_countries]['Long']

    return {
        'data': [go.Scattermapbox(
                         lon=covid_data_3['Long'],
                         lat=covid_data_3['Lat'],
                         mode='markers',
                         marker=go.scattermapbox.Marker(
                                  size=covid_data_3['confirmed'] / 1700,
                                  color=covid_data_3['confirmed'],
                                  colorscale='hsv',
                                  showscale=False,
                                  sizemode='area',
                                  opacity=0.26),

                         hoverinfo='text',
                         hovertext=
                         '<b>Country</b>: ' + covid_data_3['Country/Region'].astype(str) + '<br>' +
                         '<b>Longitude</b>: ' + covid_data_3['Long'].astype(str) + '<br>' +
                         '<b>Latitude</b>: ' + covid_data_3['Lat'].astype(str) + '<br>' +
                         '<b>Confirmed</b>: ' + [f'{x:,.0f}' for x in covid_data_3['confirmed']] + '<br>' +
                         '<b>Death</b>: ' + [f'{x:,.0f}' for x in covid_data_3['death']] + '<br>'

                        )],


        'layout': go.Layout(
             margin={"r": 0, "t": 0, "l": 0, "b": 0},
             hovermode='closest',
             mapbox=dict(
                accesstoken='pk.eyJ1IjoidG9raW9ib3kiLCJhIjoiY2w1ODIxMjV2MWRkeTNrcGJtbTdtdnhzciJ9.pPOEquxCJnl4OihAYBsBeQ',
                center=go.layout.mapbox.Center(lat=zoom_lat, lon=zoom_lon),
                style='dark',
                zoom=zoom
             ),
             autosize=True,

        )

    }


if __name__ == '__main__':
    app.run_server(debug=True)
