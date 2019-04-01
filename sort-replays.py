import sc2reader
from shutil import copy, move
import re
import argparse
import sys
import os

# This script requires [sc2reader](https://github.com/GraylinKim/sc2reader)
# Install with `pip install sc2reader`.

# Parse arguments
parser = argparse.ArgumentParser(
    description='Test replays in a given folder. Those that pass the test are placed in one folder and those that fail in another. Folders must be created beforehand. Script requires sc2reader, install with `pip install sc2reader`.')
parser.add_argument(
    'src', help='Path to replay directory. If relative, has to start with ./ or ../.')
parser.add_argument(
    'acceptDest', help='Path to directory where accepted replays go. If relative, has to start with ./ or ../.')
parser.add_argument(
    'declineDest', help='Path to directory where accepted replays go. If relative, has to start with ./ or ../.')
args = parser.parse_args()

# Globals
replaysChecked = 0
replaysAccepted = 0
errors = 0


def lockAndLoad():
   global replaysChecked
   global replaysAccepted
   global errors

   # Load all replays
   replays = sc2reader.load_replays(args.src)
   print("All replays loaded from {}".format(args.src))

   for replay in replays:
      path = replay.filename
      name = re.search(r"[^/]+$", path).group(0)
      lineup = [team.lineup for team in replay.teams]
      # print("%-20s | %s" % (replay.map_name, name))
      # if (replay.release_string.startswith("4.7.1")):
      #   print(replay.release_string)

      # Test the current replay
      if (len(replay.players) == 2 and lineup[0] == 'T' and lineup[1] == 'T' and
              replay.release_string.startswith("4.")):
         replaysAccepted += 1
         try:
            os.mkdir(args.acceptDest + "/" + replay.release_string)
         except:
            #print("There already is a directory for " + replay.release_string)
            pass
         move(path, args.acceptDest + "/" + replay.release_string)  # If accepted
      else:
         move(path, args.declineDest)  # If failed
         pass

         # One replay sorted. Print status every now and then.
      replaysChecked += 1
      if (replaysChecked % 10 == 0):
         print("%d/%d replays accepted. %d error(s)." %
               (replaysAccepted, replaysChecked, errors))


# Start the script. Due to unpack errors, retrying requires reloading entirely.
while errors < 1:
   try:
      lockAndLoad()
      break
   except:
      e = sys.exc_info()[0]
      print("There was an error: " + e)
      errors += 1
