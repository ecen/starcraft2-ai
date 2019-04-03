import requests
import zipfile as z
import os
from bs4 import BeautifulSoup
import json
length = 1000

for page in range(length):
    url = 'https://gggreplays.com/api/v1/matches?game_type=1v1&page='+str(page+1)+'&paginate=false&race=terran&replay=true&vs_race=terran'
    j = requests.get(url)
    loaded_json = j.json()
    for i in range(len(loaded_json['collection'])):
        x = loaded_json['collection'][i]
        match_url = 'https://gggreplays.com/matches/'+str(x['id'])+'/replay'
        r = requests.get(match_url)

        open(str(x['id'])+'.SC2Replay', 'wb').write(r.content)
    
        if page == 0 and i == 0:
            with z.ZipFile("replay.zip", 'w') as f:
                f.write(str(x['id'])+'.SC2Replay')
                f.close()
            print("Downloaded 1 zip")
        else:
            with z.ZipFile("temp.zip", 'w') as f:
                f.write(str(x['id'])+'.SC2Replay')
                f.close()
            with z.ZipFile('replay.zip', 'a', z.ZIP_DEFLATED) as z1:
                z2 = z.ZipFile('temp.zip', 'r')
                for n in z2.namelist():
                    z1.writestr(n, z2.open(n).read())
            os.remove("temp.zip")
            print("Downloaded page: "+str(page+1)+" replay: "+str(i+1)+" zips and merged")
        os.remove(str(x['id'])+'.SC2Replay')
    
