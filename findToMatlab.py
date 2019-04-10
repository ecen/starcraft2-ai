import re 
logFile = open("win-loss.log", "r")

#print("score time")
#line = logFile.readline()
#line = "line"

episodes = 0
for line in logFile:
    episodes += 1
    if (episodes % 1 != 0): # Rendering all points takes time in LaTeX
        continue
    line = re.search(r"[^/]+$", line).group(0).replace('.h5\n', '')
    words = line.split('-')
    nr = words[0]
    trainLoss = words[1].replace('L[', '').replace(']', '')
    validationLoss = words[2].replace('VL[', '').replace(']', '')
    #score = words[0].replace("score=", "")
    #explore = words[1].replace("explore=", "")
    #time = words[2].replace("time=", "").replace("s", "")
    #steps = words[3].replace("steps=", "").replace("\n", "")
    #supplyWorkers = words[4].replace("supplyWorkers=", "").replace("\n", "")
    #minutes = int(time)/60.0
    #print(score + " " + str(round(minutes, 2)) + "") # Time
    print("{} {} {}".format(nr, trainLoss, validationLoss))
    
logFile.close()