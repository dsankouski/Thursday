# Thursday bot

Hi, I'm Thursday, a Telegram bot to organize group's regular social events.

Suppose you and your mates have a group in Telegram, and a tradition to hang up
in bar on a regular basis. I will create a poll to find out who's going, then
assign a random going person to handle organization questions.

## Installation

- Create a telegram bot using @botfather and get your api token
- Add bot to your group
- Get your telegram group id
- Create venv: `python3 -m venv ~/.venv`
- Activate venv: `. ~/.venv/bin/activate`
- Install requirements: `pip install -r requirements.txt`

## Running

- Run bot:
```sh
token=<Your telegram bot token>
quota=<Minimum amount of persons willing to participate>
chat_id=<Chat id to serve>
python3 main.py --token "$token" --quota "$quota" --chat_id "$chat_id" --locale 'en' >>
/var/log/Thursday/Thursday.log 2>&1
```

Now you can send SIGUSR1 and SIGUSR2 to trigger bot create poll, and trigger
poll result processing respectively. For example: `pkill -SIGUSR1 -f
"\.*$chat_id"`

Cron job may be used to automate poll creation and poll processing.
For example:
```
0 11 * * 3 pkill -SIGUSR1 -f "\.*$chat_id"
0 12 * * 4 pkill -SIGUSR2 -f "\.*$chat_id"
```

This job will create a poll on each Wednesday at 11:00, and process results each
Thursday at 12:00

