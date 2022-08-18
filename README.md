# playlist-not-bot

Discord bot (no libarary just api requests) that stores playlists of songs and uses a secondary (real) discord account to queue songs on other music bots.

# WARNING

THE CONFIGURATION FOR THIS PROJECT IS STORED IN A FILE CALLED `config.json`. DO NOT RENAME THIS FILE AT ANY POINT AS IT CONTAINS API TOKENS THAT COULD BE USED TO HACK THESE ACCOUNTS.

# Configuration and config.json

First, make a discord application and a discord account that you are willing to get banned.
Then, make a discord application attached to that account at https://www.discord.com/developers/applications.
After that, go to the oath2 general section and click "add redirect". If you have a domain, put it in this field. However, if you dont own a domain put `https://www.google.com` in this field.
After you have that application created and redirect URI set, go to the "Bot" section and click "add bot".

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

# /.playlists

The bot stores the playlists in their respective dirs following this rule: `cwd/.playlists/guilid/md5hash(playlistname)`. Here's an example of what that might look like

```json
{
"users":{
  "USER1ID":3,
  "USER2ID":2
  },
  "pulbic":0,
  "songs":["example song", "example song"]
}
```

## Playlist Object

| Field    | Description                                                                                                                                          | Type      |
| -------- | ---------------------------------------------------------------------------------------------------------------------------------------------------- | --------- |
| "users"  | json object with user ids mapped to their corrosponding [authorization level](#authorization-level)                                                  | dict      |
| "public" | sets default [authorization level](#authorization-level) for everyone in the given server (on creating playlist this value is set to 0)              | int       |
| "songs"  | list of song names in playlist                                                                                                                       | list[str] |

### Authorization Level

| Level | Description                                                        |
| ----- | ------------------------------------------------------------------ |
|   0   | cannot play playlist                                               |
|   1   | can play playlist                                                  |
|   2   | play and edit playlist                                             |
|   3   | everything in 2 and add/remove level 1 and 2 users to the playlist |
|   4   | owner, can edit any property of the playlist                       |
