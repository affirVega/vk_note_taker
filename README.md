# VK Note taker

This is a simple bot for vk group. It uses `vk` python module to get user information and get vk longpoll server, and `requests` to make
longpoll requests.

As for the database, at first I went with `MongoEngine` for `MongoDB`, which was fairly easy and straightforward to work with.
I decided to move it to SQL, since my server has no space left :(

I did not want to experience the hassle of learning SQL, knowing the differences of dialects, and I've heard `SQLAlchemy` can do wonders
with sql stuff, so I went for it. So far it went smooth and I loved it! I admit, there are places that can be optimized, but I'm not
sure for now how to.

Could use some translation options in the future, as well as reminder feature which tells you your notes at your local time (i feel like it'll be a lot of pain to deal with...)


## What works
Current help (translated from RU):

```
ℹ Bot help:
!notes - show all notes
!note <text>... - create new note
!delete <int> - delete the note
!delete all - delete all notes
!edit <int> <text>... - edit note
!help - shows this message

Max notes per user - 50 (default)
```

