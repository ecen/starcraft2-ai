logFile = open("log.log", "r")

line = logFile.readline()

while line:
    words = line.split()
    score = words[0]
    time = words[2].replace("s", "")
    print(score + " " + str(round(int(time)/60.0, 2)) + "")
    line = logFile.readline()
    
logFile.close()