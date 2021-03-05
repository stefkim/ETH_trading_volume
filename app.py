from flask import Flask, render_template
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
import matplotlib.dates as mdates
import matplotlib.ticker as tick
from io import BytesIO
import base64
from bs4 import BeautifulSoup 
import requests

#don't change this
matplotlib.use('Agg')
app = Flask(__name__) #do not change this

#insert the scrapping here
link = 'https://www.coingecko.com/en/coins/ethereum/historical_data/usd?end_date=2021-01-31&start_date=2021-01-01#panel'
url_get = requests.get(link)
soup = BeautifulSoup(url_get.content,"html.parser")

table = soup.find('table', attrs={'class':'table table-striped text-sm text-lg-normal'})
tr = table.find_all('tr')
temp = [] #initiating a tuple

for i in range(1, len(tr)):
#insert the scrapping process here
    row = table.find_all('tr')[i]
    
    if(len(row)!=1):
        date = row.find_all('th')[0].text
        date = date.strip()
        
        volume = row.find_all('td')[1].text
        volume = volume.strip()
        
        temp.append((date,volume))

temp = temp[::-1]

#change into dataframe
data = pd.DataFrame(temp, columns = ('date','volume'))

#insert data wrangling here
# mengubah tipe data kolom date menjadi datetime64
data['date'] = pd.to_datetime(data['date'])

# menghapus karakter $ dan koma pada nilai volume
data['volume'] = data['volume'].str.replace('$','').str.replace(',','')

# mengubah tipe data kolom volume menjadi int64
data['volume'] = data['volume'].astype('int64')

#end of data wranggling 

@app.route("/")
def index():
    card_data = f'USD {data["volume"].mean()}'

	# generate plot
    fig, ax = plt.subplots(figsize=(20,6))
    ax.plot(data["date"],data["volume"])
    ax.set(xlabel="Date", ylabel="Volume (per 10M USD)")
    ax.xaxis.set_major_locator(mdates.DayLocator(interval=1))
    format = DateFormatter("%m/%d")
    ax.xaxis.set_major_formatter(format)
    
    
	
	# Rendering plot
	# Do not change this
    figfile = BytesIO()
    plt.savefig(figfile, format='png', transparent=True)
    figfile.seek(0)
    figdata_png = base64.b64encode(figfile.getvalue())
    plot_result = str(figdata_png)[2:-1]
    
    


	# render to html
    return render_template('index.html',
        card_data = card_data, 
		plot_result=plot_result,
        historical_data=[data.to_html(classes='data')]
		)


if __name__ == "__main__": 
    app.run(debug=True)
