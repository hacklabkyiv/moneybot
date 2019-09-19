**moneybot** is a Slack bot that grabs donation stats and posts reminders to DM to pay monthly donation.


## Now implemented

### Pullers

- ✅ **Privat**
- 🔜 **Monobank**

### Pushers 

- ✅ **CSV**
- ✅ **Slack**
- 🔜 **GDrive**


## Configuration

Make sure you added a bot as a user goind through [Slack Bot Users Guide](https://api.slack.com/bot-users).

### General

⏱️ update_interval - how often should bot pull and push updates  
🗄️ db_prefix - what folder will DB be in  
🧻 log_level - maximal level of log records  
💵 monthly_donate - how much money users should donate monthly  

### Slack

📆 general_date - a day when to post to `#general`  
⏱️ general_time - a time when to post to `#general`
📆 private_date - a day when to post to DM  
⏱️ private_time - a time when to post to DM  

📖 general_text - a text for `#general`  
📖 private_text - a text for DM  

📋 members - a dictionary of **Slack** usernames and tokens (usually real names) which bot will be searching in descriptions of payments. Tokens should be space separated.


## Installation

### 🐳 Docker

Install `docker` and then:

```sh
$ git clone https://github.com/dethoter/moneybot && cd moneybot
$ cp config.yml.template config.yml
$ docker build -t moneybot .
$ docker run -d --name moneybot --restart=unless-stopped -it -v $PWD:/app -v $PWD/data:/app/data moneybot
```

This `Dockerfile` from repo contains setup for RaspberryPi.
You can modify **FROM** field in order to target your distro.

### 💻 Locally

```sh
$ pip3 install -Ur requirements.txt
$ python3 ./app.py
```


## License

see [./LICENSE](/LICENSE)
