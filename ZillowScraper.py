from __future__ import annotations

import json
import requests
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup


requestHeader = {
  'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
  'accept-encoding': 'gzip, deflate, br',
  'accept-language': 'en-US,en;q=0.9',
  'cache-control': 'max-age=0',
  'cookie': 'zguid=23|%24d14f0059-d03b-4422-9f57-5862fcd13490; _ga=GA1.2.1741285320.1590755697; zjs_user_id=null; zjs_anonymous_id=%22d14f0059-d03b-4422-9f57-5862fcd13490%22; __gads=ID=1050523ba93d593d:T=1590755700:S=ALNI_MZlJJ_xqSbd51oJisV_HY4g017Ehw; _gcl_au=1.1.2000298647.1590755705; KruxPixel=true; _fbp=fb.1.1590755705919.1815197270; _pxvid=d6c5ec75-a1a8-11ea-b8a9-0242ac120009; KruxAddition=true; JSESSIONID=3E7EBDB1F8931DF7D0DE9992546AE0B3; zgsession=1|200e23e0-9534-4d27-931f-caa3de6b483b; _gid=GA1.2.1328942480.1590858452; _gat=1; DoubleClickSession=true; GASession=true; _uetsid=fdde22d5-862a-8a7d-93e4-a16c574edf91; _pin_unauth=YzUyOGQ2OGMtMmQ3YS00NGZkLTg3MmEtOGJlODM1YWMwMTA1; _px3=026336d3721eec42bcdec3278ad2d3ac2014d5e65707b21624fb2e743d9a89be:mq3WRz2RNL5PBIvbYNHCxq5VfXHXy2YKC+8Lqn97pIw8MiKppH7Cx7AjKzbAFi1zcehKGY36aIgsnE9NiPKwlw==:1000:4U1o3ogIQ0KzfyMd2QYEFGDnD1augezy5bJlzEn9ZHE89B2uEIxDg8BmsGj8szPwyIz1Yv15S2V0TV5P+0jCFisfGk92XM4DM7K13GCtNr0HXhNGftVBFxVrCv8ApRphw/Qwj7AcagCh9i6FPiQGLFruxVASJXLsNpFeWimekVY=; AWSALB=ZKAGBcH2BwM6D1bRKOPynbOqyclySGz5U/fZB+wO3MYQ91UR9A5rFVtFsmjOkrMASUJguhtsJRZDM7IlBiWVT/pGw2S0BjxgEZmpFPrBZEqU2lWTE2NMArtecZD2; AWSALBCORS=ZKAGBcH2BwM6D1bRKOPynbOqyclySGz5U/fZB+wO3MYQ91UR9A5rFVtFsmjOkrMASUJguhtsJRZDM7IlBiWVT/pGw2S0BjxgEZmpFPrBZEqU2lWTE2NMArtecZD2; search=6|1593450465587%7Crect%3D40.843698984643765%252C-73.50417109960938%252C40.567821651427245%252C-74.45174190039063%26rid%3D6181%26disp%3Dmap%26mdm%3Dauto%26p%3D2%26z%3D0%26lt%3Dfsbo%26fs%3D1%26fr%3D0%26mmm%3D0%26rs%3D0%26ah%3D0%26singlestory%3D0%26housing-connector%3D0%26abo%3D0%26garage%3D0%26pool%3D0%26ac%3D0%26waterfront%3D0%26finished%3D0%26unfinished%3D0%26cityview%3D0%26mountainview%3D0%26parkview%3D0%26waterview%3D0%26hoadata%3D1%26zillow-owned%3D0%263dhome%3D0%09%096181%09%09%09%09%09%09',
  'sec-fetch-dest': 'document',
  'sec-fetch-mode': 'navigate',
  'sec-fetch-site': 'same-origin',
  'sec-fetch-user': '?1',
  'upgrade-insecure-requests': '1',
  'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36'
}

class ZillowScraper:
  def __init__(self, zipCode:str=None):
    # Use default example if no zipcode is provided
    if zipCode == None:
      with open('ExampleResponses/ZipCode_37076.html') as file:
        soup = BeautifulSoup(file, 'html.parser')
    else:
      response = self.GetZillowResponse(zipCode)
      soup = BeautifulSoup(response.content, 'html.parser')
    
    print(soup)


  def GetZillowResponse(self, zipCode):
    url = f'https://www.zillow.com/homes/for_rent/{zipCode}_rb/'
    with requests.Session() as session:
      response = session.get(url, headers=requestHeader)
    
    if response.status_code != 200:
      raise ValueError('GET request failed')
    else:
      return response



if __name__ == '__main__':
  zipCode = '37076'

  zs = ZillowScraper(zipCode)
  # zs = ZillowScraper()