# This is a simple Azure OAuth2 client that could be used to retrieve the different
# AAD tokens for a service principal identity, assuming its credentials and tenant_id
# are set in the OS environment.

import os
import requests
import ssl

from requests.adapters import HTTPAdapter

try:
    from requests.packages.urllib3.poolmanager import PoolManager
    from requests.packages.urllib3 import exceptions
except ImportError:
    from urllib3.poolmanager import PoolManager
    from urllib3 import exceptions

class TlsV1HttpAdapter(HTTPAdapter):
    """
    A HTTP adapter implementation that specifies the ssl version to be TLS1.
    This avoids problems with openssl versions that
    use SSL3 as a default (which is not supported by the server side).
    """

    def init_poolmanager(self, connections, maxsize, block=False):
        self.poolmanager = PoolManager(num_pools=connections, maxsize=maxsize, block=block, ssl_version=ssl.PROTOCOL_TLSv1_2)

class AzureOAuth2Client(object):

    def __init__(self):
        self.session = requests.Session()
        self.session.mount('https://', TlsV1HttpAdapter())
        self.headers = {'Content-Type':'application/x-www-form-urlencoded'}

        # Get the service principal credentials and tenant id
        self.client_id = os.environ['AZURE_CLIENT_ID']
        self.client_secret = os.environ['AZURE_CLIENT_SECRET']
        self.tenant_id = os.environ['AZURE_TENANT_ID']
        self.url = "https://login.microsoftonline.com/" + self.tenant_id + "/oauth2/token"

    # Get the AAD access token for the service principal
    def get_aad_access_token(self):
        payload = {
            'grant_type': 'client_credentials',
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'resource': '2ff814a6-3304-4ab8-85cb-cd0e6f879c1d'
        }
        resp = self.session.request('GET', self.url, data=payload, verify = True, headers = self.headers)
        resp_json = resp.json()
        return resp_json['access_token']

    # Get the Azure management resource endpoint token for the service principal 
    def get_aad_mgmt_token(self):
        payload = {
            'grant_type': 'client_credentials',
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'resource': 'https://management.core.windows.net/'
        }
        resp = self.session.request('GET', self.url, data=payload, verify = True, headers = self.headers)
        resp_json = resp.json()
        return resp_json['access_token']
