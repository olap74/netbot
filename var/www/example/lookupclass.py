import urllib.request
import ssl
import certifi
import json
import re
from prettytable import PrettyTable, DOUBLE_BORDER

class LookupAddr:
    def __init__(self, addr):
        self.addr = addr

    @property
    def addr(self):
        return self.__addr

    @addr.setter
    def addr(self, value):
        match = re.match(r"[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}", value)
        if not bool(match):
            raise ValueError("IP Address is not valid")
        self.__addr = value

    def get_ip_info(self):
        req_url = 'https://geolocation-db.com/jsonp/' + self.addr
        json_data = {}
        with urllib.request.urlopen(req_url, context=ssl.create_default_context(cafile=certifi.where())) as url:
            data = url.read().decode()
            data = data.split("(")[1].strip(")")
            json_data = json.loads(data)

        return json_data

    def format_table(self):
        table = PrettyTable()
        table.field_names = ["Name", "Data"]
        table.align["Name"] = "l"
        table.align["Data"] = "r"
        table.set_style(DOUBLE_BORDER)
        table.header = False
        return table

    def return_ipinfo(self):
        host_data = self.get_ip_info()
        t = self.format_table()
        try:
            for k, v in host_data.items():
                t.add_row([k, v])
        except Exception as e:
            logging.error(str(e))
            return False
        return str(t)

