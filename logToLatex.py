logFile = open("log.log", "r")

#print("score time")
#line = logFile.readline()
#line = "line"

i = 0
for line in logFile:
    i += 1
    if (i % 1 != 0): # Rendering all points takes time in LaTeX, skip some
        continue
    words = line.split()
    score = words[0]
    time = words[2].replace("s", "")
    minutes = int(time)/60.0
    print(score + " " + str(round(minutes, 2)) + "")
    
logFile.close()