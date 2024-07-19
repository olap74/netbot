from prettytable import PrettyTable, DOUBLE_BORDER, MARKDOWN, PLAIN_COLUMNS, SINGLE_BORDER
from ipwhois import IPWhois
import re
import dns.resolver
import whois

resolver = dns.resolver.Resolver(configure=False)
resolver.nameservers = ['8.8.8.8','8.8.4.4']
resolver.timeout = 5
resolver.lifetime = 5

class WhoisIP:
    def __init__(self, addr):
        self.addr = addr

    def __repr__(self):
        return self.show()

    def get_data(self):
        obj = IPWhois(self.addr)
        res=obj.lookup_whois()
        
        return res

    @property
    def addr(self):
        return self.__addr

    @addr.setter
    def addr(self, value):
        match = re.match(r"[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}", value)
        if not bool(match):
            raise ValueError("IP Address is not valid")
        
        self.__addr = value

    def validate(self):
        match = re.match(r"[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}", self.addr)
        if not bool(match):
            return False
        else:
            return True
    
    def format_table(self):
        table = PrettyTable()
        table.field_names = ["Name", "Data"]
        table.align["Name"] = "l"
        table.align["Data"] = "r"
        table.set_style(SINGLE_BORDER)
        table.header = False

        return table

    def show(self):
        output = []
        data = self.get_data()
        t = self.format_table()
        nets = []
        for k,v in data.items():
            if k == 'nets':
                nets = v
            else:
                t.add_row([k, v])

        net_tables = []
        for net in nets:
            net_table = self.format_table()
            for k,v in net.items():
                if k == 'emails' and isinstance(v, (list, tuple)):
                    email_list = ""
                    for mail in v:
                        if mail:
                            email_list = email_list + mail + "\n"

                    net_table.add_row([k, email_list])
                else:
                    net_table.add_row([k, v])

            net_tables.append(str(net_table))

        output.append(f'Address Whois data:\n')
        output.append('```Domain\n' + str(t) + '```\n')
        output.append('Networks:\n')
        for tbl in net_tables:
            output.append('```Networks\n' + tbl + '```\n')
        return output

class WhoisDNS:
    def __init__(self, host):
        self.host = host

    def __repr__(self):
        return self.show()
    
    @property
    def host(self):
        return self.__host
    
    @host.setter
    def host(self, value):
        ips = []
        try:
            answers = resolver.resolve(value, 'A')
            for server in answers:
                ips.append(server.to_text())
        except Exception as e:
            raise ValueError(e)
        
        if len(ips) == 0:
            raise ValueError("Host not found")

        self.__host = value
        
    def resolve(self):
        ips = []
        try:
            answers = resolver.resolve(self.host, 'A')
            for server in answers:
                ips.append(server.to_text())
        except Exception as e:
            raise ValueError(e)

        return ips

    def get_data(self):
        dm_info =  whois.whois(self.host)

        return dm_info

    def format_table(self):
        table = PrettyTable()
        table.field_names = ["Name", "Data"]
        table.align["Name"] = "l"
        table.align["Data"] = "l"
        table.set_style(SINGLE_BORDER)
        table.header = False

        return table

    def show(self):
        data = self.get_data()
        output = []

        t = self.format_table()
        t1 = self.format_table()

        t1_flag = False

        for k,v in data.items():
            if isinstance(v, (list, tuple)):
                datatext = ""
                for d in v:
                    datatext = datatext + str(d) + '\n'
                if len(str(t)) < 1000:
                    t.add_row([k, datatext])
                else:
                    t1.add_row([k, datatext])
                    t1_flag = True
            else:
                if len(str(t)) < 1000:
                    t.add_row([k, v])
                else:
                    t1.add_row([k, v])
                    t1_flag = True

        output.append(f'Domain {self.host} data:\n')
        output.append('```WHOIS\n' + str(t) + '```\n')
        if t1_flag:
            output.append('```WHOIS\n' + str(t1) + '```\n')

        return output
