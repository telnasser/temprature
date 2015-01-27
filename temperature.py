import datetime
import requests
import sqlite3 as lite
import pandas as pd
import matplotlib.pyplot as plt

# today 
start_date = datetime.datetime.now() - datetime.timedelta(days=30)
API_KEY = '6a645a921a0eec43c124a9df39334ffd'
API_URL = 'https://api.forecast.io/forecast/'
#/31.9333,%2035.9333


cities = {
	"Atlanta": '33.762909,-84.422675',
            "Austin": '30.303936,-97.754355',
            "Boston": '42.331960,-71.020173',
            "Chicago": '41.837551,-87.681844',
            "Cleveland": '41.478462,-81.679435'
            #"Amman": '31.9333,35.9333'
}


con = lite.connect('weather.db')
cur = con.cursor()


cities.keys()
citi_names_string = ''

for k,v in cities.iteritems():
	citi_names_string += k + ' REAL,' 

citi_names_string = citi_names_string[:-1]
#print citi_names_string


with con:
    cur.execute('CREATE TABLE daily_temp ( day_of_reading INT, ' + citi_names_string + ');') #use your own city names instead of city1...

end_date = datetime.datetime.now()
query_date = end_date - datetime.timedelta(days=30) #the current value being processed

with con:
    while query_date < end_date:
        cur.execute("INSERT INTO daily_temp(day_of_reading) VALUES (?)", (int(query_date.strftime('%s')),))
        query_date += datetime.timedelta(days=1)

# for citi in cities:
# 	# Do the API call
# 	city_name = citi
# 	city_latlong = cities[citi]
# 	#print city_name, city_latlong
# 	print API_URL + API_KEY + '/' + city_latlong
# 	r = requests.get(API_URL + API_KEY + '/' + city_latlong)

for k,v in cities.iteritems():
    query_date = end_date - datetime.timedelta(days=30) #set value each time through the loop of cities
    while query_date < end_date:
        #query for the value
        r = requests.get(API_URL + API_KEY + '/' + v + ',' +  query_date.strftime('%Y-%m-%dT12:00:00'))
        print API_URL + API_KEY + '/' + v + ',' +  query_date.strftime('%Y-%m-%dT12:00:00')
        with con:
            #insert the temperature max to the database
            cur.execute('UPDATE daily_temp SET ' + k + ' = ' + str(r.json()['daily']['data'][0]['temperatureMax']) + ' WHERE day_of_reading = ' + query_date.strftime('%s'))

        #increment query_date to the next day for next operation of loop
        query_date += datetime.timedelta(days=1) #increment query_date to the next day

# Get the data from the Database and store it on DataFrame
df = pd.read_sql('SELECT * FROM daily_temp', con)

# below is a silly approach getting the mean and other data looping it out. This is not effecient in mho!
# Printing the mean temperature per city. 
for header in df.columns[1:]:
        print 'The mean temperature of >'+ header + ' is: ' + str(df[header].mean())
        df[header].plot()
        plt.show()

# A better approach than the above:!
df.iloc[:,1:].mean()

# To plot the variance and changes:
df.iloc[:,1:].plot()
plt.show()



con.close() # a good practice to close connection to database
