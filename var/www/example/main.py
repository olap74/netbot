#!/usr/bin/env python3

from flask import Flask, request, render_template
from ssl_checker import SSLChecker
from netclass import WhoisDNS, WhoisIP
from lookupclass import LookupAddr
from textwrap import wrap

import requests
import telegram
import json
import logging
import dns.resolver
import bleach
import socket

from time import gmtime, time

FORMAT = '%(asctime)s %(levelname)s %(message)s'
logging.basicConfig(level=logging.INFO,format=FORMAT)
logging.Formatter.converter = gmtime
logger = logging.getLogger(__name__)

# Config
TOKEN = "1234567890:ABCDefgHijklmNoPQRSTuVWxyz123456789"
TELEGRAM_URL = "https://api.telegram.org/bot{token}".format(token=TOKEN)
HOSTNAME = "your-host-name.tld"
WEBHOOK_URL  = "https://" + HOSTNAME

# To retrieve unique user chat ID and group ID, use @IDBot
WHITELISTED_USERS = ["132242620"]
bot = telegram.Bot(token=TOKEN)

# Bot
app = Flask(__name__, template_folder='templates')

def get_whois(chat_id, inputs):
    input = ""
    output = []
    try:
        host = inputs[1]
    except:
        logging.error("Specify an IP address or hostname as command-line parameter")
        sendmarkdown(chat_id,"*ERROR: DNS name or IP should be specified!*\n\nType `/help` for extended information")
        return False

    logging.info(f'Looking up whois information for {host}')
    try:
        WhoisIP(host).validate()
        try:
           output = WhoisIP(host).show()
        except Exception as e:
            output.append('ERROR: ' + str(e))
    except:
        logging.info('Looking up for hostname')
        try:
            output = WhoisDNS(host).show()
        except Exception as e:
            output.append('ERROR: ' + str(e))

    sendmarkdown(chat_id,f'Whois information for {host}\n\n')
    for part in output:
        sendmarkdown(chat_id,f'{part}')

def lookup(chat_id, inputs):
    input = ""
    output = ""
    try:
        host = inputs[1]
    except:
        logging.error("Specify an IP address as command-line parameter")
        sendmarkdown(chat_id,"*ERROR: DNS name or IP should be specified!*\n\nType `/help` for extended information")
        return False

    logging.info(inputs)

    try: 
        WhoisIP(host).validate()
        output = LookupAddr(host).return_ipinfo()
    except:
        try:
            ips = WhoisDNS(host).resolve()
            for ip in ips:
                output = output + str(LookupAddr(ip).return_ipinfo()) + '\n'
        except Exception as e:
            output = "ERROR: " + str(e)

    output = 'Requested DNS lookup for host: *' + host + '*\n```Response\n' + output + '```'

    sendmarkdown(chat_id,output)

def get_sslinfo(chat_id, req):
    output = ""
    cert_data = ""
    host = req[1]
    validate = []
    try:
        validate = WhoisDNS(host).resolve()
    except Exception as e:
        logging.error(str(e))
        sendcustom(chat_id,str(e))

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(10)
    check = sock.connect_ex((host,443))
    print(f'Check: {check}')
    if check != 0:
        output = f'ERROR: There is no https port opened for {host}\n\n'
        sock.close()
    else:
        if len(validate) > 0:
            SSLCheck = SSLChecker()
            args = {
                'hosts': [ host ]
            }
            result = SSLCheck.show_result(SSLCheck.get_args(json_args=args))
            try:
                for k,v in json.loads(result)[host].items():
                    cert_data = cert_data + f'{k}: {v}\n'
            except Exception as e:
                cert_data = f'ERROR: {e}'

            output = f'Host {host} exists\n\n```SSL\n{cert_data}```'
        else:
            output = ""
            # output = f'ERROR: Host {host} does not exists'

    return output

def sendmarkdown(chat_id,message):
    url = "{telegram_url}/sendMessage".format(telegram_url=TELEGRAM_URL)
    payload = {
        "text": message,
        "chat_id": chat_id,
        "parse_mode": "markdown"
        }

    resp = requests.get(url,params=payload)

def sendcustom(chat_id,message):
    url = "{telegram_url}/sendMessage".format(telegram_url=TELEGRAM_URL)
    payload = {
        "text": message,
        "chat_id": chat_id
        }

    resp = requests.get(url,params=payload)


def sendmessage(chat_id,resp):
    # As the bot is searchable and visble by public.
    # Limit the response of bot to only specific chat IDs.
    # print(f'Chat ID: {chat_id}')
    # authorised = True if str(chat_id) in WHITELISTED_USERS else False

    if resp["from"]["is_bot"]:
        message = "<b>Bots are not authorized to use this bot</b>"
    else:
        try:
            username = resp["chat"]["first_name"] + " " + resp["chat"]["last_name"]
        except:
            username = ''

        nickname = resp["from"]["username"]
        is_premium = resp["from"]["is_premium"]
        allowed_tags = ['b','i']
        allowed_attrs = {}
        resp_text = ""
        try:
            resp_text = resp["text"]
        except:
            resp_text = "There is no sense to send me something except regular text!"

        resp_text_sanitized = bleach.clean(resp_text,tags=allowed_tags,attributes=allowed_attrs)

        if username != "":
            message = f'<b>Hello, {username}</b>\n\n'
        else:
            message = f'<b>Hello, {nickname}</b>\n\n'

        message = message + f'<i>Your Telegram ID: {chat_id}</i>\n'
        if is_premium:
            message = message + f'<i>Your Username: @{nickname} (premium account)</i>\n\n'
        else:
            message = message + f'<i>Your Username: @{nickname}</i>\n\n'
        message = message + f'You just typed:\n\n'
        message = message + f'<tg-spoiler>{resp_text_sanitized}</tg-spoiler>\n\n'

    #if not authorised:
    #    message = "You're not authorised."

    url = "{telegram_url}/sendMessage".format(telegram_url=TELEGRAM_URL)
    payload = {
        "text": message,
        "chat_id": chat_id,
        "parse_mode": "html"
        }

    resp = requests.get(url,params=payload)


@app.route("/", methods=["POST","GET"])
def index():
    if(request.method == "POST"):
        response = request.get_json()

        # To Debug
        # print(response)
        ts = time()
        print(ts)

        # To run only if 'message' exist in response.
        if 'message' in response:

            chat_id = response["message"]["chat"]["id"]
            username = response["message"]["from"]["username"]
            try:
                userdata = response["message"]["chat"]["first_name"] + " " + response["message"]["chat"]["last_name"]
            except:
                userdata = username

            # To not response to other bots in the same group chat
            if 'entities' not in response['message']:
                message_text = response["message"]["text"]
                logmessage = f'User: {userdata} ({username}, {chat_id}) {message_text}'
                logging.info(logmessage)
                sendmessage(chat_id,response["message"])
            else:
                if response["message"]["entities"][0]["type"] == "bot_command":
                    command = response["message"]["text"]
                    logmessage = f'User: {userdata} ({username}, {chat_id}) {command}'
                    logging.info(logmessage)
                    if command.startswith('/help'):
                        message = f'*Commands*:\n\n'
                        message = message + '`/start` - Show welcome message\n'
                        message = message + '`/help` - Show this message\n'
                        message = message + '`/geo HOST_OR_IP` - GeoIP lookup for hostname or IP\n'
                        message = message + '`/ssl HOSTNAME` - Check SSL Certificate on HOST\n'
                        message = message + '`/whois HOST_OR_IP` -  Whois data of HOST or IP\n\n'
                        message = message + 'Any other command returns error message\n\n'
                        message = message + 'Any other command text returns answer with your personal data and hidden text you entered\n\n'
                        message = message + '_It\'s better to use this bot from PC client_\n\n'
                        sendmarkdown(chat_id,message)
                    elif command.startswith('/geo'):
                        inputs = command.split(" ")
                        lookup(chat_id,inputs)
                    elif command.startswith('/start'):
                        message = f'*GeoIP Lookup Bot*\n\nThis bot allows you to find a geographic location of a given IP or hostname.\n\n'
                        message = message + 'Please, keep in mind that a site you are checking may be pointed to some service that hides the real hosting server location (DDoS protection, Load balancer, CDN, etc)\n\n'
                        message = message + 'Type `/help` to get information how to use this bot'
                        sendmarkdown(chat_id,message)
                    elif command.startswith('/ssl'):
                        req = command.split(" ")
                        resp = get_sslinfo(chat_id, req)
                        sendmarkdown(chat_id,resp)
                    elif command.startswith('/whois'):
                        req = command.split(" ")
                        resp = get_whois(chat_id,req)
                        sendmarkdown(chat_id, resp)
                    else:
                        sendcustom(chat_id,"Unrecognized command!")

    elif(request.method == "GET"):
        logging.info(request.user_agent)
        title = HOSTNAME
        title_large = f'If you have nothing to do, don\'t do it here!'
        return render_template('default.html', title=title, title_large=title_large)

    return "Success"


@app.route("/setwebhook/")
def setwebhook():
    s = requests.get("{telegram_url}/setWebhook?url={webhook_url}".format(telegram_url=TELEGRAM_URL,webhook_url=WEBHOOK_URL))
  
    if s:
        return "Success"
    else:
        return "Fail"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

