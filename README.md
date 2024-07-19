# Network Tools Bot

## Description

This Telegram bot has been created to simplify getting network-related information such as GeoIP lookup, SSL certificate check and Hostname Whois database search.

The bot has been created using Python and it uses Nginx and UWSGI for running. Also, this bot uses Telegram API [webhooks](https://core.telegram.org/bots/api#setwebhook)

## Required Libraries
```
Flask>=3.0.2
pyopenssl>=23.2.0
dnspython>=2.6.1
certifi>=2023.11.17
bleach>=6.1.0
python-whois>=0.9.4
python-telegram-bot>=21.3
prettytable>=3.10.0
ipwhois>=1.1.0
urllib3>=2.0.7
json2html>=1.3.0
```

## Installation

Install [Nginx](https://www.f5.com/go/product/welcome-to-nginx) and [UWSGI](https://github.com/unbit/uwsgi). Also, you can use [Certbot](https://certbot.eff.org/) for hadling SSL certificates
Then using config files in the `/etc` directory of the repo, configure your Nginx, UWSGI and systemctl services. Copy these files to your server and review its content. 

After it's done, get to the Telegram and call a user named [`@BotFather`](https://t.me/BotFather). This bot allows you to [create a new Telegram bot and get it's Token](https://core.telegram.org/bots/tutorial).

Then place all files from `/var/www/example` directory to the same directory on your server and update value of `TOKEN` variable with your token you got from `@BotFather` and `HOSTNAME` variable with your host name. 

Install required Python packages using `requirements.txt` file. 
```
pip3 install -r requirements.txt
```   

Then you can start a bot using previously created systemctl service:
```
sudo systemctl daemon-reload
sudo systemctl enable netbot.uwsgi
sudo systemctl start netbot.uwsgi
```

Then call a webhook creation that is required for a new bot: 
```
curl https://your-host-name.tld/setwebhook/
```

Your new bot is ready to use

## How to use this bot

The bot supports the next commands:

- `/start` - Starts the bot and returns a "Welcome message":

```
GeoIP Lookup Bot

This bot allows you to find a geographic location of a given IP or hostname.

Please, keep in mind that a site you are checking may be pointed to some service that hides the real hosting server location (DDoS protection, Load balancer, CDN, etc)

Type /help to get information how to use this bot
```

- `/help` - Bot functionality description: 

```
Commands:

/start - Show welcome message
/help - Show this message
/geo HOST_OR_IP - GeoIP lookup for hostname or IP
/ssl HOSTNAME - Check SSL Certificate on HOST
/whois HOST_OR_IP -  Whois data of HOST or IP

Any other command returns error message

Any other command text returns answer with your personal data and hidden text you entered

It's better to use this bot from PC client
```

- `/geo` - Hostname or IP should be specified here. For example, `/geo 8.8.8.8` returns:

```
Requested DNS lookup for host: 8.8.8.8
╔══════════════╦═══════════════╗
║ country_code ║            US ║
║ country_name ║ United States ║
║ city         ║          None ║
║ postal       ║          None ║
║ latitude     ║        37.751 ║
║ longitude    ║       -97.822 ║
║ IPv4         ║       8.8.8.8 ║
║ state        ║          None ║
╚══════════════╩═══════════════╝
```

- `/ssl` - SSL certificate check. For example, `/ssl tiktok.com`
```
Host tiktok.com exists

host: tiktok.com
issued_to: *.tiktok.com
issued_o: None
issuer_c: US
issuer_o: DigiCert, Inc.
issuer_ou: None
issuer_cn: RapidSSL Global TLS RSA4096 SHA256 2022 CA1
cert_sn: 5738620536151431447615280448550238740
cert_sha1: 06:94:45:2C:AF:AA:12:6F:54:6B:2A:09:6C:34:A8:1E:9E:46:99:97
cert_alg: sha256WithRSAEncryption
cert_ver: 2
cert_sans: DNS:*.tiktok.com; DNS:tiktok.com
cert_exp: False
cert_valid: True
valid_from: 2023-08-25
valid_till: 2024-09-24
validity_days: 396
days_left: 67
valid_days_to_expire: 66
tcp_port: 443
```

- `/whois` - Looks up for IP Whois data. IP or Hostname can be used. For example, `/whois tiktok.com`:
```
GeoIP Lookup, [19/07/2024 13:55]
Whois information for tiktok.com

GeoIP Lookup, [19/07/2024 13:55]
Domain tiktok.com data:

GeoIP Lookup, [19/07/2024 13:55]
┌─────────────────┬────────────────────────────────────────────────────────────────────────────┐
│ domain_name     │ TIKTOK.COM                                                                 │
│                 │ tiktok.com                                                                 │
│                 │                                                                            │
│ registrar       │ GANDI SAS                                                                  │
│ whois_server    │ whois.gandi.net                                                            │
│ referral_url    │ None                                                                       │
│ updated_date    │ 2024-06-19 01:01:46                                                        │
│ creation_date   │ 1996-07-21 04:00:00                                                        │
│                 │ 1996-07-21 02:00:00                                                        │
│                 │                                                                            │
│ expiration_date │ 2025-07-20 04:00:00                                                        │
│ name_servers    │ NS-1475.AWSDNS-56.ORG                                                      │
│                 │ NS-1574.AWSDNS-04.CO.UK                                                    │
│                 │ NS-440.AWSDNS-55.COM                                                       │
│                 │ NS-722.AWSDNS-26.NET                                                       │
│                 │                                                                            │
│ status          │ clientTransferProhibited https://icann.org/epp#clientTransferProhibited    │
│                 │ clientTransferProhibited http://www.icann.org/epp#clientTransferProhibited │
│                 │                                                                            │
└─────────────────┴────────────────────────────────────────────────────────────────────────────┘

GeoIP Lookup, [19/07/2024 13:55]
┌────────────────────────┬─────────────────────────────────────────────────────────────┐
│ emails                 │ abuse@support.gandi.net                                     │
│                        │ f19c697400249b00ba26da776aeaa3b0-20984370@contact.gandi.net │
│                        │                                                             │
│ dnssec                 │ unsigned                                                    │
│                        │ Unsigned                                                    │
│                        │                                                             │
│ name                   │ REDACTED FOR PRIVACY                                        │
│ org                    │ TIKTOK LTD                                                  │
│ address                │ REDACTED FOR PRIVACY                                        │
│ city                   │ REDACTED FOR PRIVACY                                        │
│ state                  │ None                                                        │
│ registrant_postal_code │ REDACTED FOR PRIVACY                                        │
│ country                │ KY                                                          │
└────────────────────────┴─────────────────────────────────────────────────────────────┘
```
- Any other text returns the next message, with your text hidden:

```
Hello, USERNAME

Your Telegram ID: 123456789
Your Username: @username (premium account)

You just typed:

#######
```