import pandas as pd
import folium
import numpy as np

def map_maker():
    import folium
    #url to the 
    import datetime
    today= datetime.datetime.today() 
    yesterday=datetime.timedelta(days=1)
    yesterday_str= (today-yesterday).strftime('%m-%d-%Y')
    url = f'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_daily_reports/{yesterday_str}.csv'
    

    #read in data
    corona_df = pd.read_csv(url)
    corona_df= corona_df.loc[corona_df['Country_Region']== 'India']
    corona_df.dropna(subset=['Lat'], inplace = True)
    lat1 = 28.646519
    long1 = 77.10898
    m = folium.Map(location = [lat1, long1], zoom_start=5, tiles = 'Stamen toner')
    folium.Circle(location = [lat1, long1], 
                  radius = 1000, 
                  color = 'red', 
                  fill = True).add_to(m)

    def circle_maker(x):
        folium.Circle(location = [x[0], x[1]], 
                  radius = float(np.max([x[2]*3, 5])), 
                  color = 'red', 
                  popup = f'<h5 style="backgroundcolor:black;fontcolor:white">{x[4]}</h5>\n<strong>Deaths</strong>:  {x[3]}</h5>\n<strong>Confirmed</strong>:  {x[2]}',
                  fill = True).add_to(m)

    corona_df[['Lat', 'Long_', 'Confirmed', 'Deaths','Combined_Key']].iloc[1:].apply(lambda x: circle_maker(x), axis = 1);
    return m._repr_html_()

def find_top_confirmed(n = 15):
    '''
    This function accepts a date and returns
    DataFrames with confirmed, death, recovered,
    and active information on top n countries.
    '''
    import datetime
    today= datetime.datetime.today() 
    yesterday=datetime.timedelta(days=1)
    yesterday_str= (today-yesterday).strftime('%m-%d-%Y')
    url = f'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_daily_reports/{yesterday_str}.csv'
    corona_df = pd.read_csv(url)

        
     
    corona_df= corona_df.loc[corona_df['Country_Region']== 'India']
    corona_df.dropna(subset=['Lat'], inplace = True)
    by_state = corona_df.groupby('Province_State').sum()[['Confirmed', 'Deaths', 'Recovered', 'Active']]
    cdf = by_state.nlargest(n, 'Confirmed')[['Confirmed']]
    return cdf
   

dfs = find_top_confirmed()
pairs = [(a, b) for a,b in zip(dfs.index, dfs['Confirmed'])]
cdf = dfs.to_html()    

cmap = map_maker()
from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('df.html', frame = cdf, vmap = cmap, pairs= pairs)


if __name__ == '__main__':
    app.run(debug = True,  use_reloader=False)