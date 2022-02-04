# playlist-not-bot

Discord bot (no libarary just api requests) that uses a secondary (real) discord account to queue songs up

# configuration

First, make a discord application and a discord account that you are will to get banned. Then, make a discord bot attached to the application.

You're going to need to enable the Oauth2 values `guilds.join` and `bot` in the url generator section. Set the redirect uri to https://www.google.com

Then, make a `config.json` file in the root folder and put your bot's information, your slave account's (real discord account) token and your desired bot prefix like this:

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
    "playlists": {
      "firstplaylist":["example song", "example song"],
      "secondplaylist":["example song", "example song"]
    }
  }
  {
    "id": "GUILDID2",
    "playlists":{
      "firstplaylist":["example song", "example song"],
      "secondplaylist":["example song","example song"]
    }
  }
]
```

DO NOT CHANGE THE NAME OF `config.json` OR USE THESE TOKENS IN PLAIN TEXT ANYWHERE IN YOUR PROJECT IF YOU PLAN ON COMMITING TO GITHUB AT ANY TIME, THIS WILL GIVE HACKERS THE ABILITY TO HACK THE DISCORD ACCOUNTS
