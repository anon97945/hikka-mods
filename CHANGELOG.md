# 📝 Apodiktum Modules Changelog:

## 🆕 Version 2.0.62
### ℹ️ General:
- updated addons copyright and media link

### 📃 module updates:
- save_message | fixed for channels

## 🆕 Version 2.0.61
### 📃 module updates:
- linked_chat | added new module
- quotes | added new module

## 🆕 Version 2.0.60
### 📃 module updates:
- admintools | fixed missing await

## 🆕 Version 2.0.59
### 📃 module updates:
- general | replaced get_entity with get_chat and get_sender

## 🆕 Version 2.0.58
### 📃 module updates:
- pmlog | mark log as read (opt-out)

## 🆕 Version 2.0.57
### 📃 module updates:
- mark_read | updated for forums

## 🆕 Version 2.0.56
### 📃 module updates:
- mark_read | wrong cfg string

## 🆕 Version 2.0.55
### 📃 module updates:
- mark_read | typo

## 🆕 Version 2.0.54
### 📃 module updates:
- _skeleton | rework q_watcher
- mark_read | new module
- msg_merger | changed default whitelist to false

## 🆕 Version 2.0.53
### 📃 module updates:
- apo_python | removed, library is adding itself to eval now
- auto_delerror | changed validators

## 🆕 Version 2.0.52
### 📃 module updates:
- _skeleton | added q_watcher example
- admintools | fix bnc, removed try except
- msg_merger | removed try except
- pmlog | removed try except

## 🆕 Version 2.0.51
### 📃 module updates:
- pmlog | create new topic if deleted

## 🆕 Version 2.0.50
### 📃 module updates:
- admintools | changed crash handler
- msg_merger | changed crash handler
- pmlog | added realtime_names for topics

## 🆕 Version 2.0.49
### 📃 module updates:
- pmlog | users are now logged now in seperate topics, fixed whielist

## 🆕 Version 2.0.48
### 📃 module updates:
- admintools | added some debug msgs and fixed restricted logger

## 🆕 Version 2.0.47
### 📃 module updates:
- all modules | removed stats collect

## 🆕 Version 2.0.46
### 📃 module updates:
- apolib_controller | changed apodiktum_library url to master

## 🆕 Version 2.0.45
### 📃 module updates:
- auto_delerror | fix module

## 🆕 Version 2.0.44
### 📃 module updates:
- apolib_controller | typo

## 🆕 Version 2.0.43
### 📃 module updates:
- auto_delerror | added new module

## 🆕 Version 2.0.42
### 📃 module updates:
- apolib_controller | added unloadapocontroller

## 🆕 Version 2.0.41
### 📃 module updates:
- msg_merger | added try except q_watcher
- pmlog | added try except q_watcher

## 🆕 Version 2.0.40
### 📃 module updates:
- autoreact | Added all emoji reactions to the regex

## 🆕 Version 2.0.39
### 📃 module updates:
- admintools | removed get_entity(x.sender_id)

## 🆕 Version 2.0.38
### 📃 module updates:
- admintools | fix bnd for non-creators

## 🆕 Version 2.0.37
### 📃 module updates:
- admintools | fix admin tags whitelist

## 🆕 Version 2.0.36
### 📃 module updates:
- dnd | fixed afk reply

## 🆕 Version 2.0.35
### 📃 module updates:
- admintools | fixed logger message

## 🆕 Version 2.0.35
### 📃 module updates:
- apolib_controller | code improvement
- msg_merger | fix for reply merge bug

## 🆕 Version 2.0.34
### 📃 module updates:
- admintools | fixed crash of queue
- dnd | fixed afk reply
- msg_merger | fix attempt for threads

## 🆕 Version 2.0.33
### 📕 new modules:
- auto_delerror | Remove inline bot error messages in log channel including defined phrases

### 📃 module updates:
- admintools | added `.bnc` -> BlockNonComment will block all "non comment" messages.
- dnd | fixed `.denypm <id>`
- langreplier | fixed watcher
- msg_merger | fix attempt for threads
- pypng | fixed reply to file
- voicetools | fixed watcher


## 🆕 Version 2.0.32
### 📃 module updates:
- msg_merger | new config var `skip_reactions`

## 🆕 Version 2.0.31
### 📃 module updates:
- dnd | fix `custom emoji bio`

## 🆕 Version 2.0.30
### 📃 module updates:
- dnd | now supports `custom emojis`

## 🆕 Version 2.0.29
### 📃 module updates:
- dnd | fix `duration` display

## 🆕 Version 2.0.28
### 📃 module updates:
- msg_merger | added `.merge` to merge manual
- msg_merger | reduced `get_messages` requests

## 🆕 Version 2.0.27
### 📃 module updates:
- dnd | added multitime string support e.g. `7h30m`
- dnd | changed command `report` to `reportpm`

## 🆕 Version 2.0.26
### 📃 module updates:
- apolib_controller | added `qapolib` to see the current q_watcher queue and tasks

## 🆕 Version 2.0.25
### 📃 module updates:
- admintools | using `apo_lib.watcher_q`
- apo_python | updated to upstream
- pmlog | using `apo_lib.watcher_q`

## 🆕 Version 2.0.24
### 📃 module updates:
- msg_merger | using `q_watcher`

## 🆕 Version 2.0.23
### 📃 module updates:
- admintools | fix `whitelist` doc and `behavior`
- dnd | fix `whitelist` doc and `behavior`

## 🆕 Version 2.0.22
### 📃 module updates:
- admintools | fixed `BlockDoubleLink`
- admintools | fixed `TypeError: '<' not supported between instances of 'list' and 'float'`
- msg_merger | `skip_prefix` work in messages with links
- msg_merger | ignore messages with `prefix`

## 🆕 Version 2.0.21
### 📃 module updates:
- admintools | added `BlockCustomEmojis`
- admintools | rework of `punish handler`, now also supports notify for each
- dnd | now can black/whitelist chats for afk response. check `config`
- dnd | now supports `custom emojis`
- dnd | now supports `premium` further `bio length`
- dnd | removed config `afk_no_group` use `afk_group_list` and `afk_tag_whitelist`

## 🆕 Version 2.0.20
### 📃 module updates:
- auto_update | fix watcher

## 🆕 Version 2.0.19
### 📃 module updates:
- dnd | now also supports further in `bio`

## 🆕 Version 2.0.18
### 📃 module updates:
- apolib_controller | added `.vapolib` to get the version of the last loaded apodiktum_library
- dnd | added `use_bio` config (`Default: True`). This will set the afk message also as bio and will replace it with the old bio after `unstatus`

## 🆕 Version 2.0.17
### 📃 module updates:
- admintools | added `.bf` (blockflood) which will count messages of a user until limit (this is still `beta`)
- admintools | anonymous chat admin will be ignored
- admintools | changed `int` in db to `str`. json cant use `int keys`
- admintools | next update may have a command rework, also punishment rework

## 🆕 Version 2.0.16
### 📃 module updates:
- admintools | added `GetFullChannelRequest` cache
- admintools | added `BlockGifSpam` which will only accept one sticker per x seconds per user

## 🆕 Version 2.0.15
### 📃 module updates:
- admintools | added `BlockDoubleLinks` which will block each duplicated link for x seconds
- admintools | added `BlockStickerSpam` which will only accept one sticker per x seconds per user
- admintools | added `get_permissions` cache
- admintools | added ratelimit to notify messages
- admintools | reduced api requests

## 🆕 Version 2.0.14
### 📃 module updates:
- admintools | send msg as reply if possible

## 🆕 Version 2.0.13
#### General:
- scope: hikka_min 1.3.3
- refactored code for 1.3.0
- renamed modules to `Apo-Modulename`

### 📃 module updates:
- admintools | can now be deactivated in a chat even without admin perms
- purge | fixed apurge, spurge for private chats

## 🆕 Version 2.0.12
### 📃 module updates:
- dnd | reduced api requests

## 🆕 Version 2.0.11
### 📃 module updates:
- admintools | delete messages via bot

## 🆕 Version 2.0.10
### 📃 module updates:
- admintools | send messages via bot

## 🆕 Version 2.0.9
### 📃 module updates:
- auto_update | added skip message
- auto_update | multilang support

## 🆕 Version 2.0.8
### 📃 module updates:
- admintools | added debug message for global_queue_handler

## 🆕 Version 2.0.7
#### General:
- changed copyright banner

## 🆕 Version 2.0.6
### 📃 module updates:
- dnd | added optional further informations

## 🆕 Version 2.0.5
#### General:
- black formatting

### 📃 module updates:
- admintools | `admin_tags` is not case insensetive
- admintools | added message link to bot message
- admintools | added `whitelist` config for admin_tag
- admintools | added `ignore_admins` config to ignore `admin tags` of admins
- dnd | hopefully fixed entity error

## 🆕 Version 2.0.4
### 📃 module updates:
- admintools | added ability to add custom admin tags in config such as `/report`, `.report`, etc.

## 🆕 Version 2.0.3
### 📃 module updates:
- admintools | added `@admin` tag for chats (check config)
- autoreact | added `ignore_self` config
- dnd | automatically removes status after given time, improved bot message

## 🆕 Version 2.0.2
### 📃 module updates:
- apoinfo | fixed apoinfo `{upd}`

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
- scope: hikka_min 1.2.11
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