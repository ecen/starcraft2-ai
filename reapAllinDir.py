import os
#directory = os.path.dirname(os.path.realpath(__file__))
directory = "C:\\Users\\Mattias\\Downloads\\replay4+folders\\some"

print(os.listdir(directory))
for filename in os.listdir(directory):
    if filename.endswith(".SC2Replay"):
        #print (directory+"\\"+filename)
        os.system("sc2reaper ingest "+directory+"\\"+filename)
        #break
