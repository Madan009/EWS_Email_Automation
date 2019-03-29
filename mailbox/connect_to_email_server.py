from exchangelib import Account, DELEGATE, Configuration, ServiceAccount
from exchangelib.protocol import BaseProtocol, NoVerifyHTTPAdapter
import urllib3
urllib3.disable_warnings()
BaseProtocol.HTTP_ADAPTER_CLS = NoVerifyHTTPAdapter

def connect_to_server():

    credentials = ServiceAccount(username='1051058@tcsmfdm.com', password='India@2030')
    config = Configuration(server='win9595.tcsmfdm.com', credentials=credentials)
    account = Account(primary_smtp_address="1051058@tcsmfdm.com",
                      config=config,
                      autodiscover=False,
                      access_type=DELEGATE)
    return account