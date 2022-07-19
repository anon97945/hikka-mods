# 📝 Apodiktum Changelog:

## 🆕 Version 1.0.0

### ℹ️ General:
- scoped to hikka_min 1.2.11
- deepsource fixes

### 📦 apodiktum_library:
#### General:
- added beta_id list
- added full docstring to library
- added hikka anonymous stats
- added hikka min version scope to library
- added translation strings
- added utils_beta for testing
- changed to self.apo_lib.utils
- edited library to use hikka native libs
- get_str rework. forcelang > setlang > basestring
- implemented migrator class
- library sideloads apolib_controller.py
- logger rework
- new beta utils
- new internal class
- using different classes

#### Utils:
- library utils | added convert_time
- library utils | added distinct_emoji_list
- library utils | added emoji_list
- library utils | added escape_html
- library utils | added get_attrs
- library utils | added get_entityurls
- library utils | added get_href_urls
- library utils | added get_ids_from_tglink
- library utils | added get_invite_link
- library utils | added get_str
- library utils | added get_sub
- library utils | added get_tag
- library utils | added get_tag_link
- library utils | added get_urls
- library utils | added is_emoji
- library utils | added is_linkedchannel
- library utils | added is_member 
- library utils | added log
- library utils | added rem_duplicates_list
- library utils | added rem_emoji
- library utils | added unescape_html

### 📕 new modules:
- apo_python.py
- apolib_controller.py

### 📁 new files:
- apodiktum_library.py

### 📃 module updates:
- all | changed self.strings to support new library
- all | dropped fast_download
- all | removed migrator class, will be build into library
- all | use my apodiktum_library.py
- apoinfo | changed default msg time to `code`
- apoinfo | update for uptime
- dnd | added self expiring afk messages
- dnd | changed reason banned to blocked.
- langreplier | added auto translation
- langreplier | fix requirements of langreplier
- langreplier | ignore mathematical as alphabet
- langreplier | replace `cyrillic` with `vodka` in respond message of alphabet (optional)
- lcr | check for digit count instead of message content to support different languages.
- msg_merger | add ignore prefix to ignore the message fully
- msg_merger | added new is_emoji skip
- msg_merger | added reverse_merge to msg_merger to merge into newest
- msg_merger | added unmerge cmd
- msg_merger | delete reply message if its from self
- msg_merger | dont merge into ignored prefix
- msg_merger | fix ignores time on merge_own_reply `false`
- msg_merger | force link_preview `True`/`False` or decide automatically if set to `None` (config bool)
- msg_merger | merge urls `True`/`False` (config bool))
- msg_merger | some bug fixes in msg_merger#
- msg_merger | try / except get_messages
- show_viewer | fix .sv args
- show_viewer | fix send as reply