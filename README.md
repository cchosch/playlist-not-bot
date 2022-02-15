# playlist-not-bot

Discord bot (no libarary just api requests) that stores playlists of songs and uses a secondary (real) discord account to queue songs on other music bots.

# WARNING

THE CONFIGURATION FOR THIS PROJECT IS STORED IN A FILE CALLED `config.json`. DO NOT RENAME THIS FILE AT ANY POINT AS IT CONTAINS API TOKENS THAT COULD BE USED TO HACK THESE ACCOUNTS.

# Configuration and config.json

First, make a discord application and a discord account that you are willing to get banned.
Then, make a discord application attached to that account at https://www.discord.com/developers/applications.
After that, go to the oath2 general section and click "add redirect". If you have a domain, put it in this field. However, if you dont own a domain put `https://www.google.com` in this field.
Whence you have that application created and redirect URI set, go to the "Bot" section and click "add bot".

Then, run `pip install websockets`. Also make a `config.json` file in the root folder and put your bot's information, along with the token for the read account and your desired bot prefix like this:

```json
{
  "master_auth": "BOT TOKEN HERE",
  "master_client_secret": "BOT SECRET HERE",
  "master_redirect_uri": "BOT REDIRECT URI HERE",
  "slave_auth": "SLAVE ACCOUNT TOKEN HERE",
  "prefix": ";"
}
```

That's it, your bot is ready to go!

# playlist.json

The bot stores all of the playlists in a json file in the root folder called `playlists.json`. The formatting of `playlists.json` is as follows:

```json
[
  {
    "id": "GUILDID1",
    "playlists": {
      "firstplaylist":{
        "users":{
          "USER1ID":3,
          "USER2ID":2
        },
        "pulbic":0,
        "songs":["example song", "example song"]
      },
      "secondplaylist":{
        "users":{
          "USER1ID":3,
          "USER2ID":2
        },
        "public": 2,
        "songs":["example song", "example song"]
      }
    }
  }
  {
    "id": "GUILDID2",
    "playlists": {
      "firstplaylist":{
        "users":{
          "USER1ID":3,
          "USER2ID":2
        },
        "pulbic":0,
        "songs":["example song", "example song"]
      },
      "secondplaylist":{
        "users":{
          "USER1ID":3,
          "USER2ID":2
        },
        "public": 2,
        "songs":["example song", "example song"]
      }
    }
  }
]
```

## Guild Object

| Field       | Description                                                                                                                       | Type        |
| ----------- | --------------------------------------------------------------------------------------------------------------------------------- | ----------- |
| "id"        | id of guild this object belongs to                                                                                                | string      |
| "playlists" | json object with the names of all the playlists in the guild as the field and [playlist object's](#playlist-object) as the items | json object |

## Playlist Object

| Field    | Description                                                                                                                                            | Type             |
| -------- | ------------------------------------------------------------------------------------------------------------------------------------------------------ | ---------------- |
| "users"  | json object with fields as user ids and [authorization level](#authorization-level) as item                                                          | json object      |
| "public" | sets default [authorization level](#authorization-level) for everyone in the given server with 0 representing a private playlist. default value of 0 | integer          |
| "songs"  | array of song names in playlist                                                                                                                        | array of strings |

### Authorization Level

| Level | Description                                                                              |
| ----- | ---------------------------------------------------------------------------------------- |
| 1     | can play given playlist                                                                  |
| 2     | do everything in 1 and edit given playlist                                               |
| 3     | do everything in 1-2 and add and remove level 1 and level 2 authorized users to playlist |
| 4     | edit playlist and add and remove level 1, 2, and 3 users to the playlist                 |
| 5     | owner, can edit any properties of the playlist                                           |
