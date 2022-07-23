# 📝 Apodiktum Modules Changelog:

## 🆕 Version 2.0.1
### 📃 module updates:
- dnd | fixed is_linkedchannel

## 🆕 Version 2.0.0
### 📦 apodiktum_library:
#### General:
- Switched Library to his own repo -> https://github.com/anon97945/hikka-libs
- Library now supports scope for requirements, not need to add unnecessary imports into the module

### 📃 module updates:
- all | dropped imports and req scope of emoji

## 🆕 Version 1.0.6
### ℹ️ General:
- reformatted modules with black

### 📦 apodiktum_library:
#### Utils:
- added get_buttons

### 📃 module updates:
- dnd | fixed .status without optional time

## 🆕 Version 1.0.5
### ℹ️ General:
- added # meta banner and # meta pic

### 📦 apodiktum_library:
#### Utils:
- renamed get_buttons_as_dict to get_buttons

### 📃 module updates:
- all | removed migrator log configs from modules, they are now in the lib config
- apo_migrator_class | removed, is now implemented in library
- dnd | .status now remove reply messages if it was already .status
- msg_merger | fixed multiple errors, fixed unmerge command

## 🆕 Version 1.0.4
### 📦 apodiktum_library:
#### Utils:
- library utils beta | added get_buttons_as_dict

## 🆕 Version 1.0.3
### 📦 apodiktum_library:
#### Utils:
- added get_user_id
- added validate_bool
- added validate_datetime
- added validate_dict
- added validate_email
- added validate_float
- added validate_integer
- added validate_list
- added validate_none
- added validate_regex
- added validate_string
- added validate_tgid
- added validate_tuple
- removed get_attrs
- removed get_sub

## 🆕 Version 1.0.2
### 📦 apodiktum_library:
#### General:
- deepsource fix
- fixed logger

#### Utils:
- fixed keyerror in get_str() when db has no `hikka.translations`
- added get_all_urls

### 📃 module updates:
- autoreact | fixed `local variable 'emoji_list' referenced before assignment`

## 🆕 Version 1.0.2
### 📦 apodiktum_library:
#### Utils:
- added get_uptime
- added tdstring_to_seconds
- added time_formatter(short=True)

### 📃 module updates:
- all | added emoji requirement scope to ensure lib can load
- admintools | fixed get_tag not awaited
- apoinfo | changed get_uptime to apo_lib instead of hikka native

## 🆕 Version 1.0.1
### 📦 apodiktum_library:
#### General:
- ControllerLoader Log set as debug_msg
- fixed config
- reworked hikka anonymous stats
- reworked logger

#### Utils:
- added humanbytes
- added time_formatter

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
- added convert_time
- added distinct_emoji_list
- added emoji_list
- added escape_html
- added get_attrs
- added get_entityurls
- added get_href_urls
- added get_ids_from_tglink
- added get_invite_link
- added get_str
- added get_sub
- added get_tag
- added get_tag_link
- added get_urls
- added is_emoji
- added is_linkedchannel
- added is_member 
- added log
- added rem_duplicates_list
- added rem_emoji
- added unescape_html

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