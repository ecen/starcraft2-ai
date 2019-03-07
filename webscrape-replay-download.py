import requests
import zipfile as z
import os
length = 137


for page in range(length):
    url = "https://lotv.spawningtool.com/zip/?query=&after_played_on=&before_played_on=&tag=12&adv=1&after_time=&patch=140&coop=&before_time=&order_by=&p="+str(page+1)
    r = requests.get(url)
    if page == 0:
        with open("replay.zip", 'wb') as f:
            f.write(r.content)
            f.close()
        print("Downloaded 1 zip")
    else:
        with open("replay2.zip", 'wb') as f:
            f.write(r.content)
            f.close()
        with z.ZipFile('replay.zip', 'a', z.ZIP_DEFLATED) as z1:
            z2 = z.ZipFile('replay2.zip', 'r')
            for n in z2.namelist():
                z1.writestr(n, z2.open(n).read())
        os.remove("replay2.zip")
        print("Downloaded "+str(page+1)+" zips and merged")


