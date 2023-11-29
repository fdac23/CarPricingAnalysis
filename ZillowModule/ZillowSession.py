import requests 


class ZillowSession():
  def __init__(self, proxyFile:str = ''):
    self.session = requests.Session()
    self.proxy_list = set(open(proxyFile, "r").read().strip().split("\n")) if proxyFile != '' else self.RequestProxiesList()
    self.working = set()

  def RequestProxiesList(self):
    print('getting a list of proxies')
    try:
      response = self.session.get("https://api.proxyscrape.com/v2/", params={'request':'displayproxies','protocol':'http','timeout':10000,'country':'all','ssl':'all','anonymity':'all'}, timeout=30)
    except Exception as e:
      print('API failed... could not get proxy list')
      return None
    
    response = response.content.decode('utf-8').strip().split('\r\n')
    print(len(response), 'proxies found')
    return response


  def GetProxy(self):
    if len(self.proxy_list) != 0:
      proxy = self.proxy_list.pop()
    else:
      proxy = list(self.working)[0]
    return proxy


  # Finds a proxy and provides a session
  def ProvideProxy(self):
    print('checking proxy connection...')
    proxy = None
    response = None
    while True:
      proxy = self.GetProxy()
      try:
        response = self.session.get('https://ident.me/', proxies={'http': f"http://{proxy}"}, timeout=15)
        if response.status_code == 200:
          self.working.add(proxy)
          print(f'proxy found: {proxy}')
          break
        else:
          if len(self.proxy_list) and len(self.working):
            print('Out of proxies')
            break
          self.working.discard(proxy)
          print(f'connection failed: {proxy}')
          proxy = self.GetProxy()
      except KeyError as ke:
        if ke.args[0] == 'pop from an empty set':
          print('Proxy list empty')
          return None
      except Exception as e:
        print(e)
        self.working.discard(proxy)

    return proxy


  # Performs a get request with the given url and proxy
  def get(self, url:str, header:dict()={}, params:dict()={}, proxy='', attempts=5):
    # if proxy not provided get one
    if proxy == '':
      proxy = self.ProvideProxy()

    while True:
      try:
        response = self.session.get(url, proxies={'http': f"http://{proxy}"}, timeout=30, headers=header, params=params)
        print(response.status_code)
        # if response.status_code <= 200 or response.status_code >= 300:
        #   raise 'Response failed'
        break
      except Exception as e:
        if attempts <= 0:
          print('Max attempts reached...')
          break
        print('proxy failed... getting a new proxy')
        proxy = self.ProvideProxy()
        attempts -= 1

    return response


# main function is for testing purposes
if __name__ == '__main__':
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

  z_session = ZillowSession('')
  zipCode = '37916'
  print(z_session.get(f'https://www.zillow.com/homes/for_rent/{zipCode}_rb/', header))
