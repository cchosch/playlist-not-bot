# playlist-not-bot

This project is a discord bot that stores playlists of songs in a directory (no db) and uses a secondary discord account to queue songs on other music bots.

# WARNING

Do not commit your config file to github unless you want anyone to be able to login to your discord account.

# Configuration and config.json

First, make a discord application and a discord account that you are willing to get banned.
Then, make a discord application attached to that account at https://www.discord.com/developers/applications.
After that, go to the oath2 general section and click "add redirect". If you have a domain, put it in this field. However, if you dont own a domain put `https://www.google.com` in this field.
After you have that application created and redirect URI set, go to the "Bot" section and click "add bot".

Then, run `pip install websockets` & `pip install bs4`. Also make a `config.json` file in the root folder and put your bot's information, along with the token for the read account and your desired bot prefix like this:

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

The bot stores the playlists in their respective dirs following this rule: `./.playlists/{guild_id}/md5hash(playlistname)`. Here's an example of what that might look like:

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
