from __future__ import annotations

import re
import csv
import json
import requests
import pandas as pd
from random import randint
from bs4 import BeautifulSoup
from urllib.parse import quote
from urllib.parse import urlencode
from ZillowSession import Zillow_Session


class ZillowScraper:
  header = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'en-US,en;q=0.9',
    'cache-control': 'max-age=0',
    'cookie': 'zguid=24|%24c02c415b-4576-4389-94be-e23c11b18ffa; zgsession=1|169e56d7-e2bd-43af-9c4e-9866ea7ccd57; zjs_anonymous_id=%22c02c415b-4576-4389-94be-e23c11b18ffa%22; zjs_user_id=null; zg_anonymous_id=%2280f2467d-3d8b-4592-adf7-fd20323eeb99%22; _ga=GA1.2.1216532562.1698163414; _gid=GA1.2.2029951140.1698163414; pxcts=e28b86cd-7286-11ee-a8ba-6e800c2813fc; _pxvid=e28b70a3-7286-11ee-a8ba-b3419cc79c66; x-amz-continuous-deployment-state=AYABeDHNAM6iUFGCGI0sw0WuC78APgACAAFEAB1kM2Jsa2Q0azB3azlvai5jbG91ZGZyb250Lm5ldAABRwAVRzA3MjU1NjcyMVRZRFY4RDcyVlpWAAEAAkNEABpDb29raWUAAACAAAAADOQAZYRehRHfkjb%2FsAAwnQHaY4QSweSkEGsegXIi%2FdVHt8mqxDS3%2FTwM1IQUoMiy0l6GLdtjybsUolKVF%2FZEAgAAAAAMAAQAAAAAAAAAAAAAAAAAALZ94DCgc4CATmeo7z%2F86xb%2F%2F%2F%2F%2FAAAAAQAAAAAAAAAAAAAAAQAAAAxEZY03Pz0VyvEa%2FE3HMhpLFiYvrtYasKi68hnr; _gcl_au=1.1.1857945718.1698163416; DoubleClickSession=true; __pdst=6cd7d6b392384405ae770919ec731f62; _pin_unauth=dWlkPU4yVmtOMlZsTXpBdE5ETTNPQzAwTURVekxXRTBabVF0WVRBME5UUTJObUl4WmpaaQ; _cs_c=0; _cs_id=783c21ae-d902-a9fa-fe4a-21f24a10e719.1698163531.2.1698165979.1698165970.1.1732327531000; FSsampler=918145208; _clck=a0wk5j|2|fg5|0|1392; _pxff_tm=1; _hp2_id.1215457233=%7B%22userId%22%3A%227540853962200912%22%2C%22pageviewId%22%3A%227252990841852008%22%2C%22sessionId%22%3A%228328645617928294%22%2C%22identity%22%3Anull%2C%22trackerVersion%22%3A%224.0%22%7D; _hp2_ses_props.1215457233=%7B%22ts%22%3A1698272685891%2C%22d%22%3A%22www.zillow.com%22%2C%22h%22%3A%22%2F%22%7D; JSESSIONID=8802E3C43FA4EB8EC66D0B2ED373C6A0; g_state={"i_p":1698877494923,"i_l":3}; _gat=1; _pxff_cc=U2FtZVNpdGU9TGF4Ow==; _pxff_cfp=1; _pxff_bsco=1; AWSALB=gkmoKaeQUU4X4inRe9hvUqaC7+OK68nLNpU2g7vCCz/4Wqa9lwz7HCBUr8F/irSDstjOZ8PFtA6B3eInhpRiRjpOCh0YeL530HUwkcItvdOTluFOvgsopbR98jNt; AWSALBCORS=gkmoKaeQUU4X4inRe9hvUqaC7+OK68nLNpU2g7vCCz/4Wqa9lwz7HCBUr8F/irSDstjOZ8PFtA6B3eInhpRiRjpOCh0YeL530HUwkcItvdOTluFOvgsopbR98jNt; search=6|1700864890043%7Crect%3D36.85589814914472%252C-86.356778703125%252C35.52485876134722%252C-87.213712296875%26rid%3D6118%26disp%3Dmap%26mdm%3Dauto%26p%3D1%26z%3D1%26listPriceActive%3D1%26fs%3D0%26fr%3D1%26mmm%3D0%26rs%3D0%26ah%3D0%26singlestory%3D0%26housing-connector%3D0%26abo%3D0%26garage%3D0%26pool%3D0%26ac%3D0%26waterfront%3D0%26finished%3D0%26unfinished%3D0%26cityview%3D0%26mountainview%3D0%26parkview%3D0%26waterview%3D0%26hoadata%3D1%26zillow-owned%3D0%263dhome%3D0%26featuredMultiFamilyBuilding%3D0%26excludeNullAvailabilityDates%3D0%26commuteMode%3Ddriving%26commuteTimeOfDay%3Dnow%09%096118%09%7B%22isList%22%3Atrue%2C%22isMap%22%3Atrue%7D%09%09%09%09%09; _px3=fb5b8c1aeabe138bd069efd2e04f97e1d86261a9e740491a8278f137b3f29f3c:uSLJrY4z+/Y0+JyeTMUn0AFFwAMRBo0p25ebOhwkC4dvi8lsTbjYDU+QwNb9Fagp6LAEAvdBvZ0yL+c7cEAqCQ==:1000:EM7QRQW+3tjt43cbXrpzSg7CWYvwHKq9z/JtWDr97WNLiqvpTrdLdgmXocKwNWT46mR1sTF7uNwqFjD2kZ2IqkrIh1jdPqiveplWQkKYRf9qOsSeTwlHheIugbFkWaT3FcDGVfwKu8V8ge9LvivjHFIVQbiK82DRlhPc/DgZPGbe+b3s+A44MXHB33UvXBtooXFZAyvmpmWsRCoPiMycwBQvCsy+4YbfPJXeMRYOCSk=; _uetsid=e354adc0728611ee96177d94a8663afd; _uetvid=b3108c10a4b511ed9117bd9dbe7780dc; _derived_epik=dj0yJnU9eVdBbk9RamFTZlFKQWRYU2N0VWM0MmRnb3N5dlR3eTQmbj1meTlZSUdmVmFOWWVFUHVuVUw2TmJBJm09MSZ0PUFBQUFBR1U1bG53JnJtPTEmcnQ9QUFBQUFHVTVsbncmc3A9Mg; _clsk=1cvcko0|1698272893199|8|0|s.clarity.ms/collect',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36'
  }

  filters = {
    "isForSaleForeclosure": {"value": False},
    "isMultiFamily": {"value": False},
    "isAllHomes": {"value": True},
    "isAuction": {"value": False},
    "isNewConstruction": {"value": False},
    "isForRent": {"value": True},
    "isLotLand": {"value": False},
    "isManufactured": {"value": False},
    "isForSaleByOwner": {"value": False},
    "isComingSoon": {"value": False},
    "isForSaleByAgent": {"value": False},
  }

  def __init__(self, zipCodes:list[str]):
    df = pd.read_csv('ValidZipCodes.csv', converters={'DELIVERY ZIPCODE':str})
    self.validZipCodes = list(df['DELIVERY ZIPCODE'])

    for zipCode in zipCodes:
      if zipCode not in self.validZipCodes:
        raise ValueError(f'Invalid Zip-Code: {zipCode}')

    self.z_session = Zillow_Session('http_proxies.txt')

    csvFile = 'Listings.csv'
    with open(csvFile, 'w') as f:
      writeFile = csv.writer(f)
      writeFile.writerow(['zipCode', 'latitude', 'longitude', 'price', 'numBeds', 'numBaths', 'area', 'address', 'timeOnZillow', 'detailURL'])

    self.zipCodes = zipCodes
    self.ScrapeZipcodeListings(self.zipCodes)
    
    
  def ScrapeZipcodeListings(self, zipCodes:list[str]):
    for zipCode in zipCodes:
      queryData = self.GetQueryData(zipCode)
      listings = self.GetListings(queryData)
      self.ParseListings(listings, zipCode)

  
  def GetQueryData(self, zipCode:str):
    url = f'https://www.zillow.com/homes/for_rent/{zipCode}_rb/'
    response = self.z_session.get(url, header=self.header)
    soup = BeautifulSoup(response.content, 'html.parser')

    mapBounds = re.findall(r'("mapBounds":\{[^}]+\})', str(soup))[0]
    mapBounds = f"{{{mapBounds}}}"
    
    queryData = json.loads(mapBounds)
    queryData["filterState"] = self.filters

    return queryData
  

  def GetListings(self, queryData:dict):
    parameters = {
        "searchQueryState": {
            "pagination": {},
            "usersSearchTerm": "Nashville, TN",
            "mapBounds": queryData["mapBounds"],
            "filterState": queryData["filterState"]
        },
        "wants": {
            "cat1": ["listResults", "mapResults"], "cat2": ["total"]
        },
        "requestId": randint(2, 10),
    }
    
    url = "https://www.zillow.com/search/GetSearchPageState.htm?"
    url += urlencode(parameters)
    response = self.z_session.get(url, header=self.header)
    listings = response.json()["cat1"]["searchResults"]["mapResults"]
    return listings


  def GetZillowResponse(self, url:str):
    with requests.Session() as session:
      response = session.get(url, headers=self.header)
    
    if response.status_code != 200:
      raise ValueError('GET request failed')
    else:
      return response
  

  def ParseListings(self, listings:list[dict], zipCode:str):    
    csvFile = 'Listings.csv'
    f = open(csvFile, 'a')
    writeFile = csv.writer(f)
    
    for listing in listings:
      if listing['statusType'] == 'FOR_RENT':
        if 'latLong' in listing.keys():
          latitude = listing['latLong']['latitude']
          longitude = listing['latLong']['longitude']
        else:
          latitude = None
          longitude = None

        if 'minBeds' in listing.keys():
          numBeds = listing['minBeds']
        elif 'beds' in listing.keys():
          numBeds = listing['beds']
        elif ('hdpData' in listing.keys()) and ('homeInfo' in listing['hdpData'].keys()) and ('bedrooms' in listing['hdpData']['homeInfo'].keys()):
          numBeds = listing['hdpData']['homeInfo']['bedrooms']
        else:
          numBeds = None

        if 'minBaths' in listing.keys():
          numBaths = listing['minBaths']
        elif 'baths' in listing.keys():
          numBaths = listing['baths']
        elif ('hdpData' in listing.keys()) and ('homeInfo' in listing['hdpData'].keys()) and ('bathrooms' in listing['hdpData']['homeInfo'].keys()):
          numBaths = listing['hdpData']['homeInfo']['bathrooms']
        else:
          numBaths = None

        if 'minArea' in listing.keys():
          area = listing['minArea']
        elif 'area' in listing.keys():
          area = listing['area']
        elif ('hdpData' in listing.keys()) and ('homeInfo' in listing['hdpData'].keys()) and ('livingArea' in listing['hdpData']['homeInfo'].keys()):
          area = listing['hdpData']['homeInfo']['livingArea']
        else:
          area = None
        
        if 'address' in listing.keys():
          address = listing['address']
        elif ('hdpData' in listing.keys()) and ('homeInfo' in listing['hdpData'].keys()) and ('streetAddress' in listing['hdpData']['homeInfo'].keys()):
          address = listing['hdpData']['homeInfo']['streetAddress']
        else:
          address = None

        if 'price' in listing.keys():
          price = listing['price']
          price = re.sub('[^0-9,]', "", price).replace(",", "")
          price = float(price)
        else:
          price = None
        
        timeOnZillow = listing['timeOnZillow'] if 'timeOnZillow' in listing.keys() else None
        detailURL = listing['detailUrl'] if 'detailUrl' in listing.keys() else None

        writeFile.writerow([str(zipCode), latitude, longitude, price, numBeds, numBaths, area, address, timeOnZillow, detailURL])



if __name__ == '__main__':
  zipCodes = ['37920', '37076']
  zs = ZillowScraper(zipCodes)
