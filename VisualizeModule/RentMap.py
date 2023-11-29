import plotly.express as px
from urllib.request import urlopen
import json
import pandas as pd
import numpy as np
from pyzipcode import ZipCodeDatabase
from ZillowModule.ZillowScraper import ZillowScraper
import ZillowModule as zm

state_dict = {
  'al': 'alabama',
  'ak': 'alaska',
  'az': 'arizona',
  'ar': 'arkansas',
  'ca': 'california',
  'co': 'colorado',
  'ct': 'connecticut',
  'dc': 'district_of_columbia',
  'de': 'delaware',
  'fl': 'florida',
  'ga': 'georgia',
  'hi': 'hawaii',
  'id': 'idaho',
  'il': 'illinois',
  'in': 'indiana',
  'ia': 'iowa',
  'ks': 'kansas',
  'ky': 'kentucky',
  'la': 'louisiana',
  'me': 'maine',
  'md': 'maryland',
  'ma': 'massachusetts',
  'mi': 'michigan',
  'mn': 'minnesota',
  'ms': 'mississippi',
  'mo': 'missouri',
  'mt': 'montana',
  'ne': 'nebraska',
  'nv': 'nevada',
  'nh': 'new_hampshire',
  'nj': 'new_jersey',
  'nm': 'new_mexico',
  'ny': 'new_york',
  'nc': 'north_carolina',
  'nd': 'north_dakota',
  'oh': 'ohio',
  'ok': 'oklahoma',
  'or': 'oregon',
  'pa': 'pennsylvania',
  'ri': 'rhode_island',
  'sc': 'south_carolina',
  'sd': 'south_dakota',
  'tn': 'tennessee',
  'tx': 'texas',
  'ut': 'utah',
  'vt': 'vermont',
  'va': 'virginia',
  'wa': 'washington',
  'wv': 'west_virginia',
  'wi': 'wisconsin',
  'wy': 'wyoming',
}

class RentMap:
  def __init__(self, city,state:str,distric_name=''):
    self.state = state
    # get valid zipcodes for place
    df = pd.read_csv(zm.ValidZipCodesPath, converters={'DELIVERY ZIPCODE':str})
    df = df[['DELIVERY ZIPCODE','PHYSICAL CITY', 'PHYSICAL STATE','DISTRICT NAME']]

    if distric_name != '':
      self.city = city
      self.zipcode_data = df[df['DISTRICT NAME'] == distric_name.upper()]
      print(self.zipcode_data)
    elif type(city) == str and state != '':
      self.city = city
      self.zipcode_data = df[df['PHYSICAL CITY'] == city.upper()] if state == '' else df[(df['PHYSICAL CITY'] == city.upper()) & (df['PHYSICAL STATE'] == state.upper())]
    elif type(city) == list:
      self.city = city
      self.zipcode_data = pd.DataFrame()
      for c in city:
        self.zipcode_data = pd.concat([self.zipcode_data, df[df['PHYSICAL CITY'] == c.upper()]], axis=0)
    else:
      raise f'Invalid city type {city}'

    if len(self.zipcode_data) == 0:
      raise 'Could not find any zip codes... Check city is valid'

  # runner with get all of the units for the selected area and generate a map
  def runner(self, csv_name=''):
    if csv_name == '':
      csv_name = self.city.replace(' ','') + '.csv'
    self.GetRentForZipcodes(csv_name)
    zipcode_data = pd.read_csv(csv_name)
    zipcode_data
    self.GenerateChoroplethMap(zipcode_data)

  def GetRentForZipcodes(self, csv_name):
    zip_list = self.zipcode_data['DELIVERY ZIPCODE']
    ZillowScraper.ValidateZipcodes(zip_list)
    self.scraper = ZillowScraper(zip_list, False)
    self.scraper.WriteListingToCSV(['zipCode','price'], csv_name)

  def GenerateChoroplethMap(self, csv_name=''):
    print('Generating Choropleth Map')
    if csv_name == '':
      csv_name = self.city.replace(' ','') + '.csv'
    zipcode_data = pd.read_csv(csv_name)
    
    zip_averages = []
    for zc in zipcode_data['zipCode'].unique():
      zip_averages.append({'zipCode':zc, 'price' : zipcode_data[zipcode_data['zipCode'] == zc]['price'].mean(), 'numHomes': zipcode_data[zipcode_data['zipCode'] == zc].count()[0]})
    df = pd.DataFrame(zip_averages)
    
    with urlopen(f'https://raw.githubusercontent.com/OpenDataDE/State-zip-code-GeoJSON/master/{self.state.lower()}_{state_dict[self.state.lower()]}_zip_codes_geo.min.json') as r:
      zipcodes = json.load(r)

    # create map plot
    fig = px.choropleth(
      df,
      geojson=zipcodes, 
      locations='zipCode',
      color='price',
      color_continuous_scale="rdbu",
      featureidkey="properties.ZCTA5CE10",
      range_color=(df['price'].min(), df['price'].max()),
      labels={'zipCode':'Zip Code','price':'Rent Prices','numHomes':'Number of houses'},
      hover_data={'zipCode': True, 'price': True, 'numHomes': True},
    )
    fig.update_geos(fitbounds="locations", visible=False) # removes underlaying map
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    fig.show()


if __name__ == '__main__':
  rm = RentMap('New York', 'NY', 'NEW YORK 1')
  rm.runner()
