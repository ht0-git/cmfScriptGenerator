# Description
This script generates game scripts that can be used in the Total War: ROME REMASTERED modification, which allows you to control multiple game factions.

**Note:** Works correctly only if the modification does not have "Emerging Factions" (factions that have in the description "Events will be simulated leading up to the faction's appearance...").

# Usage
Place the faction list in the *factions.txt* file from the *descr_strat.txt* file with the required modification (from the "playable" and "unlockable" category).

**Note:** Everything will work correctly ONLY if the list of factions in *factions.txt* is in the order in which the factions take their turn if the player selects the very first faction in the list before the start of the campaign (for the original game this is romans_julii).

Run *cmfScriptGenerator.py* and it will create all the scripts that need to be placed in the folder next to *descr_strat.txt*.

If the required modification does not include its script in *descr_strat.txt*, then include the script *cmf_script__main.txt*. And if it does, then it is at your discretion - you either need to combine the scripts or execute at the end of the script (before ***end_script***):
```
include_script cmf_script__main.txt
```
A *text.txt* file will also be created, it will contain tags and text for localization, which will need to be added to the files (remember that all localization files must be saved in UTF-16 LE encoding):
```
data\text\expanded_bi.txt
data\text\expanded_bi_mac_de.txt
data\text\expanded_bi_mac_es.txt
data\text\expanded_bi_mac_fr.txt
data\text\expanded_bi_mac_it.txt
data\text\expanded_bi_mac_ru.txt
data\text\expanded_bi_mac_zh_cn.txt
```
If the mod uses these files, copy them to yours and add the contents of *text.txt* to the end of the file.

**Note:** Don't forget to change the faction names to the correct ones (don't touch the tags), as the default will be the name from *factions.txt* (for example, greek_cities and not Greek Cities).
