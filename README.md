# Satisfactory Optimiser

A program for planning optimised factories in the videogame "Satisfactory", using linear programming.

## Dependencies
 + Python3 installed
   + This must be on the system PATH if running the script directly on Un\*x or Un\*x-like systems
   + `pythonw.exe` from Python3 must be on the system PATH if using the batch script on Windows
   + If running manually, the script can be passed to python directly instead (e.g. to use a different Python interpreter)
   + The program has been tested with Python 3.11.8 and Python 3.13.2, and works on both.  It should work on any version above 3.11.8 with no issues, and possibly on older versions (some older versions of my program were broken on 3.11.8 due to format string parsing differences, and it is possible that other differences in older versions of Python break the code in other ways, but I do not have any of these versions installed to test against).
 + `PySide6` installed for your python interpreter
 + A `Docs.json` file from Satisfactory
   + If Satisfactory 1.0 is installed from Steam on Linux or Windows, and is installed to the default location, then the British English localised version will be autodetected.
     + To use a different path (installed in non-default location, using update 8 file that is called `Docs.json` due to lack of localised versions being available, using Satisfactory installed from Epic Games, using a file copied from the game install to a different device without the game, or running on an OS where I have not been able to test where the game is installed and thus no autodetection is set up), the script can be launched with the `-p <path>` argument.
   + The program has been tested with `Docs.json` files from an Update 8 game, as well as a Release 1.0 game.
 + (Optional, Un\*x-like only) GNU Coreutils 8.30 or above
   + This is required if running the script as an executable directly, due to the shebang making use of the `-S` argument to `/usr/bin/env`
   + If passing the script as an argument to python instead, this is not required (the shebang is ignored)
 + (Optional, Un\*x-like only) `dbus-python` installed for your python interpreter
   + This is used for (optional) notification support on Linux.
   + This backend is able to specify the urgency of the notification, and the dependency size is smaller than the plyer backend.  If your system supports it, I would suggest using it over the plyer backend.
   + The notification backend used can be selected from the application settings, with notifications being disabled by default.
 + (Optional) `plyer` installed for your python interpreter, and appropriate dependencies for its notification support.
   + This is used for (optional) notification support on multiple platforms.
   + My code does not implement setting the urgency of the notification when this is used on Linux.  Other platforms lack a concept of notification urgency.
   + The notification backend used can be selected from the application settings, with notifications being disabled by default.
 + Some time to wait
   + The optimisation algorithm can take a long time to run.  A CPU with decent single-thread performance is recommended, as well as enabling one of the notification backends if you decide to do something else on your computer while you wait.
   + I would suggest taking some time to explore any unexplored areas of your game world if the program is given a complicated input.  You could also work on building a factory you have planned previously, or expanding an existing one.

## Launching
On Microsoft Windows, execute the file named `WINDOWS USERS CLICK HERE.bat` to start as a GUI.

On Un\*x-like systems, mark `main.py` as executable (`chmod +x main.py`) if it is not already, then run it directly.  Alternatively, you can launch it via the python interpreter directly: `/path/to/your/python3 main.py`.

On any system, it is suggested to set the `PYTHONHASHSEED` environment variable to `0` if launching manually via a python interpreter.  The script will attempt to do this automatically if you do not do it yourself (the batch file and shebang in the script will explicitly do this, and the script itself has logic to relaunch itself with the environment variable set).  This is because hash randomisation of strings performed by Python has a nasty habit of frequently making some problems take around five times as long to run most of the time (I have a vague idea why, but no idea of how to properly fix it).  Hash randomisation provides no effective security benefit to this program (there are other ways to crash it with access to its input data, it can be closed via normal means with access to the UI, and it does not use the network).  Also ensure that python is not invoked with the `-R` command-line argument, since this overrides the environment variable.  While the script has logic to detect this and avoid entering an infinite restart loop (or creating a forkbomb on Windows, where process substitution isn't available), it will refuse to start.
### Command-line arguments
`-h` or `--help` will display the available arguments specific to the program.  `--help-all` will additionally display generic arguments provided by Qt.

`-v` or `--version` will display the program version

`-p <path>` can be used to manually specify the path to the Docs.json file (if it has not been autodetected, or if you wish to use a path different to the one that was autodetected).  The default path depends on the platform the program is run on.

`-l <verbosity>` sets the log level.  Logs from the current program run are output to a file named `last.log`, which is overwritten if the program is restarted.  The verbosity can be one of `debug`, `info`, `warn`, `error`, `crit` (with `debug` being the most verbose and `crit` being the least).  The default is `warn`.

## Usage

The program is divided up into three tabs (problem, solution, settings), with the program selecting the problem tab when first started.  The problem tab is used to define the linear programming problem, the solution tab is used to view the solution that is calculated, and the settings tab is used to specify miscellaneous program settings.

### Problem tab

(todo)

### Solution tab

(todo)

### Settings tab

![A screenshot of the settings tab, showing all the notification backends to be available, with the D-Bus backend selected](../readmeassets/2025-03-16T13:00:40,923934561+00:00.png?raw=true)

Currently, the only setting available is the notification backend.  If the module required by a notification backend fails to import, the corresponding backend will be unavailable for selection.  If the saved settings specify a backend that would be unavailable in this way, a dialog will be displayed when the program starts offering to reset the settings to their defaults or terminate the program to allow for manual troubleshooting and rectification.

Settings are **not applied** unless the "Apply" button is clicked.  Once this is done, the settings will then be saved to disk and take effect on the program.

To reload the stored settings from disk, the "Cancel" button can be clicked.  This will revert what is displayed in the settings tab to match what is in use by the program (and is saved on disk).