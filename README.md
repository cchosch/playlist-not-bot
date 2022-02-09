# playlist-not-bot

Discord bot (no libarary just api requests) that stores playlists of songs and uses a secondary (real) discord account to queue songs on other music bots.

# configuration

First, make a discord application and a discord account that you are willing to get banned. Then, make a discord bot attached to that account at www.discord.com/developers/applications.

You're going to need to enable the Oauth2 values `guilds.join` and `bot` in the url generator section. Set the redirect uri to https://www.google.com

Then, run `pip install requests` and `pip install websockets`. Also make a `config.json` file in the root folder and put your bot's information, along with the token for the read account and your desired bot prefix like this:

```json
{
  "master_auth": "BOT TOKEN HERE",
  "master_client_secret": "BOT SECRET HERE",
  "master_redirect_uri": "BOT REDIRECT URI HERE",
  "slave_auth": "SLAVE ACCOUNT TOKEN HERE",
  "prefix": ";"
}
```

That's it, your bot is ready to go! The bot stores all of the playlists in a json file in the root folder called `playlists.json`. The formatting of `playlists.json` is as follows:

```json
[
  {
    "id": "GUILDID1",
    "uid": "USERID",
    "":[""]
    "playlists": {
      "firstplaylist":["example song", "example song"],
      "secondplaylist":["example song", "example song"]
    }
  }
  {
    "id": "GUILDID2",
    "uid":"USERID2",
    "playlists":{
      "firstplaylist":["example song", "example song"],
      "secondplaylist":["example song","example song"]
    }
  }
]
```

DO NOT CHANGE THE NAME OF `config.json` OR USE THESE TOKENS IN PLAIN TEXT ANYWHERE IN YOUR PROJECT IF YOU PLAN ON COMMITING TO GITHUB AT ANY TIME, THIS WILL GIVE HACKERS THE ABILITY TO HACK THE DISCORD ACCOUNTS
