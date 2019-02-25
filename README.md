# starcraft2-ai
Repository for bachelor-degree project with the goal of developing a StarCraft 2 AI using machine learning.

## PYSC2 and replays
Some help for running PYSC2 agents and watching replays in the game client.

### Running PYSC2 agents
__Running built-in agents__, example:
`python3 -m pysc2.bin.agent --map MoveToBeacon --agent_race terran --agent pysc2.agents.scripted_agent.MoveToBeacon`.

__Running custom agents__. If you have a python file named `my-agent.py` which contains a class `MyAgent` that extends the base agent, you can run this by going to the folder where `my-agent.py` is located and running `python3 -m pysc2.bin.agent --map MoveToBeacon --agent_race terran --agent my-agent.MyAgent`.

### View replays
To view replays in the SC2 game client (not the PYSC2 one), place the replay files in `drive_c/users/[your username]/My Documents/StarCraft II/Accounts/[account id, ex: 123456789]/[another id, ex: 1-S2-3-4567890]/Replays/Multiplayer/AI/`). This also works when SC2 is installed under Wine on Linux.

To view the replay you may also need to add the map to your SC2 folder. Put the map in `drive_c/ProgramData/Blizzard Entertainment/StarCraft II/Maps/Cache/`.

## Status
Information and status of things.

### ecen -> agent-swann.SwannCraft
A scripted agent designed after following [a tutorial](https://chatbotslife.com/building-a-basic-pysc2-agent-b109cde1477c). Currently works and can win, but does not always. Run with `python3 -m pysc2.bin.agent --map Simple64 --agent_race terran --agent agent-swann.SwannCraft`.

Swann is named after the chief engineer aboard Raynor's ship in the Wings of Liberty SC2 campaign.

### ecen -> supervised-mk1.Mk1
An agent currently taking random actions. Designed from the beginning of [this tutorial](https://chatbotslife.com/building-a-smart-pysc2-agent-cdc269cb095d).
