# starcraft2-ai
Repository for bachelor-degree project with the goal of developing a StarCraft 2 AI using machine learning.



# Agents

* CNN = Convolutional Network Agent
* DQN = Deep Q network agent
* MarineAgent = Marine Agent
* WinLoss = Win Loss Agent


# Testing

> 
1. Build MongoDB in the sc2reaper branch
2. Run WinLoss.py with the database running, saves \*.h5 files every 5th epoch
3. Run MarineAgent.py, put one of the \*.h5 files in the same folder and change line 512 så that it can be fed into the program
