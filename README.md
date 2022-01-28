# playlist-not-bot

Discord bot (no libarary just api requests) that uses a secondary (real) discord account to queue songs up

# configuration

First, make a discord application and a discord account that you are will to get banned. Then make a discord bot attached to the application.

You're going to need to enable the Oauth2 values `guilds.join` and `bot` in the url generator section. Set the redirect uri to https://www.google.com

Then, make a `config.json` file in the root folder and put your bot's information, your slave account's (real discord account) token and your desired bot prefix like this:

```json
{
  "master_auth": "BOT TOKEN HERE",
  "master_client_id": "BOT CLIENT ID HERE",
  "master_client_secret":"BOT SECRET HERE",
  "master_redirect_uri": "BOT REDIRECT URI HERE"
  "slave_auth": "SLAVE ACCOUNT TOKEN HERE",
  "prefix": ";"
}
```

DO NOT CHANGE THE NAME OF THIS FILE OR USE THESE TOKENS IN PLAIN TEXT ANYWHERE IN YOUR PROJECT IF YOU PLAN ON COMMITING TO GITHUB AT ANY TIME, THIS WILL GIVE HACKERS THE ABILITY TO HACK THE DISCORD ACCOUNTS
