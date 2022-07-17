# 📝 Apodiktum Changelog:

## 🆕 Version 1.0.0

### ℹ️ General:
- deepsource fixes

### 📦 apodiktum_library:
- edited library for 1.2.10 native support
- scope to 1.2.11
- library sideload apolib_controller.py
- logger rework
- get_str rework. forcelang > setlang > basestring
- added migrator, not testet and not working!
- using different classes
- changed to self.apo_lib.utils
- new beta utils
- new internal class
- added utils_beta for testing
- added beta_id list
- added translation strings
- implementing migrator class

### 📕 new modules:
- apo_python.py
- apolib_controller.py

### 📁 new files:
- apodiktum_library.py

### 📃 module updates:
- all         | use my apodiktum_library.py
- all         | changed self.strings to support new library
- all         | removed migrator class, will be build into library
- all         | dropped fast_download
- dnd         | added self expiring afk messages
- dnd         | changed reason banned to blocked.
- msg_merger  | try / except get_messages
- msg_merger  | added new is_emoji skip
- msg_merger  | force link_preview `True`/`False` or decide automatically if set to `None` (config bool)
- msg_merger  | merge urls `True`/`False` (config bool))
- msg_merger  | fix ignores time on merge_own_reply `false`
- msg_merger  | some bug fixes in msg_merger#
- msg_merger  | added reverse_merge to msg_merger to merge into newest
- msg_merger  | delete reply message if its from self
- apoinfo     | changed default msg time to `code`
- lcr         | check for digit count instead of message content to support different languages.
- msg_merger  | add ignore prefix to ignore the message fully
- apoinfo     | update for uptime
- langreplier | added auto translation
- langreplier | ignore mathematical as alphabet
- langreplier | replace `cyrillic` with `vodka` in respond message of alphabet (optional)
- langreplier | fix requirements of langreplier
- show_viewer | fix .sv args
- show_viewer | fix send as reply

