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

![A screenshot of the problem tab with some values input.  It is annotated to display information about the different sections.](../readmeassets/problem-tab-annotated.jpg?raw=true)

The problem tab contains four sections to define the problem:
1) The target definition, where the target items and their weightings are specified.
2) The resource availability definition, where constraints on the availability of certain resources are specified.
3) The weightings definition, where miscellaneous weightings (currently just power usage) are specified.
4) The recipe selection, where the algorithm can be forbidden to use certain recipes in its solution.
Finally, there is the "Run Optimisation" button, the purpose of which should be self-explanatory.

To add a second target, the Add button next to "Target Weightings" can be clicked.  Note that adding multiple targets may result in the algorithm only producing one if weights and other constraints are not set carefully.

To add other available resources (other than the basic ores and fluids listed by default) as an input, the Add button next to "Resource Availability" can be clicked.  Here, care does not need to be taken in specifying which resources are available if multiple are to be made avaliable in the same way as multiple targets, *unless* using multiple targets (generally, this program is not good at handling multiple targets outside of specific scenarios).

As the user, you should be aware that the power usage weighting should be set quite low compared to the target weightings (by 3 orders of magnitude at minimum), since it is measured in megawatts (and most recipes consume quite a few megawatts).  If not, any recipe the algorithm chooses will decrease the objective variable by consuming power more than it will increase it by producing the target item, and the algorithm will fail.  If required, the weights of all the target items can be increased by one or more orders of magnitude (if the weight on the power usage cannot be set to a small enough value).  It should also be noted that setting a power usage weight tends to make the algorithm take a lot longer, for some reason.

The recipes used will be the ones that were selected at the time of running, not the ones listed in the selected profile on the disk.  However, to save to the selected profile on the disk, the user must click the save button.  To create a new profile, its name can be typed into the dropdown box and then save clicked.  Saving over the default profile is not possible, but if a profile named `user-default` is present then it will be loaded at startup instead of the built-in default profile.  The application will open a dialog to provide this info if saving over the default profile is attempted.

Profiles only save which recipes are active - they do not save the other inputs or any calculated solution.  The application settings are saved, loaded, and stored separately.

Profiles can be loaded on docs files from other versions of the game, with some caveats.  Recipes that did not exist when the profile was generated will be deselected.  Recipes that existed when the profile was created will be deselected if reloaded against a docs file that does contain them if the profile is saved over (if the profile is not saved over then this will not occur).  The built-in default profile is unaffected, since it is unwriteable and only enables any recipe that is in the normal category.

### Solution tab

![A screenshot of the solution tab before a solution has been calculated.  It is annotated to display information about what the different areas will contain.](../readmeassets/solution-tab-empty.jpg?raw=true)

![A screenshot of the solution tab after a solution has been calculated.  It is annotated to display information about what the different areas that were not annotated in the pre-calculation screenshot contain.](../readmeassets/solution-tab-with-solution.jpg?raw=true)
Note that the sum of the clock speeds is *represented as a decimal instead of a percentage* (such that if a whole number of machines was used it would equal the number of machines, not 100 times the number of machines).

<details><summary>Settings used that resulted in this solution</summary>
 + en-GB docs file from a release 1.0 game installation
 + All normal recipes enabled
 + Wet concrete alternate recipe enabled, all other alternate recipes disabled
 + Weight 1 for producing concrete, weight 0 for power usage, no other weights
 + 100 limestone and 10 cubic metres of water per minute, no other resources available
</details>
<details><summary>Some commentary on this problem, the kinds of problems that the program can currently handle, and the kinds of problems that the program could be modified to handle with relatively minimal programmer effort</summary>It is possible to see that the program created as much wet concrete as it could before it ran out of water, then used the regular recipe to make the rest of the concrete.  Although this is a rather simple example that could be done mentally (wet concrete makes more concrete per limestone than the regular recipe, so use that until no water is left over, then use the regular recipe for the rest is simple to do by hand), this was intentionally chosen to showcase the program UI.  The program is equipped to handle far more complex problems, such as being able to find the optimum ratio of multiple production chains that share the same set of inputs in different ratios, or doing similar calculations but avoiding high power usage (a similar problem to the example can be seen with the various "pure _ ingot" alternate recipes, which have a significantly lower increase in the number of items produced per ore when also adding water, so the extra power consumed by the refinery at a particular rate of production is significant).  Even though some scenarios are not supported (for example, adding a penalty for items transferred per minute for use if high-tier belts/pipes have not been unlocked, handling power generation using byproducts and subtracting it from the power consumption or planning a power plant instead of a factory by setting power production as a target, setting a hard limit on power consumption by treating it as an item for the purposes of the recipes, setting weights for usage of any of the input items, and other such use cases) the core of the program is already powerful enough to handle these scenarios and could be modified to support them in the future with fairly little effort.</details>

The solution tab contains two sections:
1) At the top there is a scrollable area which will list all the recipes used in the solution, including data required to construct them, such as the sum of the clock speeds and the total item flow rates (useful for planning item routing e.g. representing the flows as a graph or determining which tier of belt/pipe is required for a manifold).
2) At the bottom there is a region that provides a quick overview of the solution, with data such as the total power consumed and the total production output of each of the requested items.  The value of the objective variable is also present (this is the value that the algorithm is trying to maximise).

A splitter handle is present between the two sections, which allows the space to be reallocated between them.  It is also possible to use this to hide the quick overview (e.g. if the solution is deemed suitable by the user, they can collapse the quick overview so that more space is available for them to read the list of recipes used).

The contents of this tab are *cleared immediately when re-running the optimisation*, to avoid confusion if the progress dialog becomes hidden before the algorithm completes.  If one desires to retain a record of a solution, I would suggest screenshotting it, scrolling through the production overview and details as required.

Multiple recipes may appear on one line of the list of all recipes used if sufficient horizontal space is available.

### Settings tab

![A screenshot of the settings tab, showing all the notification backends to be available, with the D-Bus backend selected](../readmeassets/2025-03-16T13:00:40,923934561+00:00.png?raw=true)

Currently, the only setting available is the notification backend.  If the module required by a notification backend fails to import, the corresponding backend will be unavailable for selection.  If the saved settings specify a backend that would be unavailable in this way, a dialog will be displayed when the program starts offering to reset the settings to their defaults or terminate the program to allow for manual troubleshooting and rectification.

Settings are **not applied** unless the "Apply" button is clicked.  Once this is done, the settings will then be saved to disk and take effect on the program.

To reload the stored settings from disk, the "Cancel" button can be clicked.  This will revert what is displayed in the settings tab to match what is in use by the program (and is saved on disk).