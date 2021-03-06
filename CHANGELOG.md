# đ Apodiktum Modules Changelog:

## đ Version 2.0.10
### đ module updates:
- admintools | send messages as bot

## đ Version 2.0.9
### đ module updates:
- auto_update | added skip message
- auto_update | multilang support

## đ Version 2.0.8
### đ module updates:
- admintools | added debug message for global_queue_handler

## đ Version 2.0.7
#### General:
- changed copyright banner

## đ Version 2.0.6
### đ module updates:
- dnd | added optional further informations

## đ Version 2.0.5
#### General:
- black formatting

### đ module updates:
- admintools | `admin_tags` is not case insensetive
- admintools | added message link to bot message
- admintools | added `whitelist` config for admin_tag
- admintools | added `ignore_admins` config to ignore `admin tags` of admins
- dnd | hopefully fixed entity error

## đ Version 2.0.4
### đ module updates:
- admintools | added ability to add custom admin tags in config such as `/report`, `.report`, etc.

## đ Version 2.0.3
### đ module updates:
- admintools | added `@admin` tag for chats (check config)
- autoreact | added `ignore_self` config
- dnd | automatically removes status after given time, improved bot message

## đ Version 2.0.2
### đ module updates:
- apoinfo | fixed apoinfo `{upd}`

## đ Version 2.0.1
### đ module updates:
- dnd | fixed is_linkedchannel

## đ Version 2.0.0
### đĻ apodiktum_library:
#### General:
- Switched Library to his own repo -> https://github.com/anon97945/hikka-libs
- Library now supports scope for requirements, not need to add unnecessary imports into the module

### đ module updates:
- all | dropped imports and req scope of emoji

## đ Version 1.0.6
### âšī¸ General:
- reformatted modules with black

### đĻ apodiktum_library:
#### Utils:
- added get_buttons

### đ module updates:
- dnd | fixed .status without optional time

## đ Version 1.0.5
### âšī¸ General:
- added # meta banner and # meta pic

### đĻ apodiktum_library:
#### Utils:
- renamed get_buttons_as_dict to get_buttons

### đ module updates:
- all | removed migrator log configs from modules, they are now in the lib config
- apo_migrator_class | removed, is now implemented in library
- dnd | .status now remove reply messages if it was already .status
- msg_merger | fixed multiple errors, fixed unmerge command

## đ Version 1.0.4
### đĻ apodiktum_library:
#### Utils:
- library utils beta | added get_buttons_as_dict

## đ Version 1.0.3
### đĻ apodiktum_library:
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

## đ Version 1.0.2
### đĻ apodiktum_library:
#### General:
- deepsource fix
- fixed logger

#### Utils:
- fixed keyerror in get_str() when db has no `hikka.translations`
- added get_all_urls

### đ module updates:
- autoreact | fixed `local variable 'emoji_list' referenced before assignment`

## đ Version 1.0.2
### đĻ apodiktum_library:
#### Utils:
- added get_uptime
- added tdstring_to_seconds
- added time_formatter(short=True)

### đ module updates:
- all | added emoji requirement scope to ensure lib can load
- admintools | fixed get_tag not awaited
- apoinfo | changed get_uptime to apo_lib instead of hikka native

## đ Version 1.0.1
### đĻ apodiktum_library:
#### General:
- ControllerLoader Log set as debug_msg
- fixed config
- reworked hikka anonymous stats
- reworked logger

#### Utils:
- added humanbytes
- added time_formatter

## đ Version 1.0.0
### âšī¸ General:
- scoped to hikka_min 1.2.11
- deepsource fixes

### đĻ apodiktum_library:
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

### đ new modules:
- apo_python.py
- apolib_controller.py

### đ new files:
- apodiktum_library.py

### đ module updates:
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