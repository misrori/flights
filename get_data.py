from dotenv import load_dotenv
import os
from datetime import datetime
import pandas as pd
import requests
from pandas import json_normalize
from datetime import datetime, timedelta
import json
import os
load_dotenv()

def get_one_dest(destination_id):

    params = {
        'fly_from': START_LOCATION_ID,
        'fly_to': destination_id,
        'date_from': current_date_string ,
        'date_to': future_date_string,
        'adults': '1',
        'nights_in_dst_from':MIN_STAY,
        'nights_in_dst_to':MAX_STAY

    }

    response = requests.get('https://api.tequila.kiwi.com/v2/search', params=params, headers=headers)

    data = response.json()

    file_path = JSON_DATA + '/' + datetime.now().strftime("%Y_%m_%d_") + START_LOCATION_ID + '-' +destination_id + '.csv'
    with open(file_path, 'w') as json_file:
        # Step 4: Use json.dump() to write the dictionary to the file
        json.dump(data, json_file, indent=4)

    df = pd.DataFrame(list(map(lambda x: {
        'from': x['cityFrom'], 
        'to':x['cityTo'],
        'price': x['price'], 
        'outgoing_start' : x['local_departure'], 
        'incomming_start': x['route'][-1]['local_departure'],
        'incomming_arrival': x['route'][-1]['local_arrival'],
        'night_in_dest': x['nightsInDest'],
        'link':x['deep_link'] 
        'stop': x['technical_stops']
        },data['data'] )))
    

    return(df)


KIWI_API_KEY = os.environ.get('KIWI_TOKEN')
START_LOCATION_ID = "BUD"
MAX_PLAN_FORWARD_DAYS = 180
MAX_RADIUS=6000
MIN_STAY = 0
MAX_STAY = 7
JSON_DATA = 'json_data'
CSV_DATA ='csv_data'
LAST_PRICE = CSV_DATA + '/last_prices.csv'

if not os.path.exists(JSON_DATA):
    os.makedirs(JSON_DATA)

if not os.path.exists(CSV_DATA):
    os.makedirs(CSV_DATA)

headers = {
    'accept': 'application/json',
    'apikey': KIWI_API_KEY,
}

params = {
    'lat': '47',
    'lon': '19',
    'radius': MAX_RADIUS,
    'locale': 'en-US',
    'location_types': 'airport',
    'limit': '500',
    'sort':'rank',
    'active_only': 'true',
}

response = requests.get('https://api.tequila.kiwi.com/locations/radius', params=params, headers=headers)

data = response.json()
locations = pd.DataFrame(list(map(lambda x:{
    'id': x['id'],
    'name': x['name'],
    'city': x['city']['name'],
    'country': x['city']['country']['name'],
    'continent': x['city']['continent']['name'],
    'region': x['city']['region']['name'],
    'lon': x['location']['lon'],
    'lat': x['location']['lat'], 
    'rank':x['rank']
},  data['locations'] )))


locations.to_csv(f'{CSV_DATA}/airportrs.csv', index=False)

airport_ids = list(locations[locations['continent']== 'Europe']['id'])


current_date_string = datetime.now().strftime("%d/%m/%Y")
future_date = datetime.now() + timedelta(days = MAX_PLAN_FORWARD_DAYS)
future_date_string = future_date.strftime("%d/%m/%Y")


data_frames = []


for airport_id in airport_ids[0:5]:
    try:
        df = get_one_dest(airport_id)
        df['dest_id'] = airport_id
        data_frames.append(df)
    except:
        print(f'error: {airport_id}')

combined_df = pd.concat(data_frames, ignore_index=True)

combined_df = combined_df[combined_df['price']<200]

combined_df.to_csv(f'{CSV_DATA}/{datetime.now().strftime("%Y_%m_%d_")}BUD', index=False)

combined_df.to_csv(LAST_PRICE, index=False)