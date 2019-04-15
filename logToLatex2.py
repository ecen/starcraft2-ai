logFile = open("log.log", "r")

#print("score time")
#line = logFile.readline()
#line = "line"

episodes = 0
for line in logFile:
    episodes += 1
    if (episodes % 1 != 0): # Rendering all points takes time in LaTeX
        continue
    words = line.split(',')
    score = words[0].replace("score=", "")
    explore = words[1].replace("explore=", "")
    time = words[2].replace("time=", "").replace("s", "")
    steps = words[3].replace("steps=", "").replace("\n", "")
    supplyWorkers = words[4].replace("supplyWorkers=", "").replace("\n", "")
    supplyArmy = words[5].replace("supplyArmy=", "").replace("\n", "")
    totalUnits = words[6].replace("totalUnits=", "").replace("\n", "")
    totalUnitsKilled = words[7].replace("totalUnitsKilled=", "").replace("\n", "")
    totalStructuresKilled = words[8].replace("totalStructuresKilled=", "").replace("\n", "")
    minutes = int(time)/60.0
    #print(score + " " + str(round(minutes, 2)) + "") # Time
    print("{} {} {} {} {} {} {} {}".format(score, episodes, steps, supplyWorkers, supplyArmy, totalUnits, totalUnitsKilled, totalStructuresKilled))
    
logFile.close()