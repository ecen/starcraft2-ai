# sc2reaper modification
This is a modification/extension of sc2reaper that allows for automatic extraction of data from multiple replays sequentially. The data is also converted to the same format used in PySC2 making it easy to use it for supervised learning with PySC2.

# Prerequisites
* MongoDB
* PySC2
* Copy of sc2reaper: https://github.com/miguelgondu/sc2reaper
* Starcraft 2
* SC2 Replay files
* Windows?

# How to
* Copy all Python files from this branch into your copy of sc2reaper's sc2reaper folder, replacing the default files.
* Edit reapAllinDir.py's directory variable to point to the folder containing your replays.
* Make sure MongoDB is running
* Run reapAllinDir.py

# Customize
You can change what information is stored by changing for example state_extraction.py. The pysc2Observation inside of get_state is the same data type as the one used by PySC2 so the simple API found in other branches can be applied to it. Copies of all get functions for the image data that should be relevant for TvT matchups from the simple API should exist near the top of state_extraction.py.

# Known Issues
* So far we've only managed to make sc2reaper work on Windows. It might be possible to get it working on Linux but we haven't succeeded at it. 
* Currently there is no way to assign data to training/validation sets.
* It appears that replays have to be of the same version that SC2 is, if SC2 updates then all replays are rendered obsolete. There might be a way to run it on older replays but we haven't succeeded at it.
* sc2reaper doesn't like filenames with strange characters like spaces and will crash failing to find the replay if given one.

# Troubleshooting
* `Connection already closed. SC2 probably crashed.` make sure that the replay is running the same version is the game.
* An error like `Possible corruption - Failed to open the map archive: C:\...` appears if this is the first time that the map has been run on the machine, it can be solved by starting the replay manually with SC2, by double clicking on it.
* Some replays will crash partway through parsing due to `Unknown ability_id: %s, type: %s. Likely a bug.`, this can be circumvented by editing pysc2's features.py: Add `return FUNCTIONS.no_op()` just before the line raising the error `raise ValueError("Unknown ability_id: %s, type: %s. Likely a bug."`. This might cause some missing data if one were to save the actions taken to the database, but since it appears the action wouldn't have been supported by pysc2 anyway it shouldn't matter.
