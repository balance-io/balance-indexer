import hashlib
import hmac
import json

from balance_indexer.errors import SourceError
from balance_indexer import kms, keystore

class ChangellyApiDetails(object):
  def __init__(self, api_key, signature):
    self.api_key = kms.get_parameter('changelly-api-key') if not api_key else api_key
    self.signature = kms.get_parameter('changelly-sign') if not signature else signature
    self.base_url = 'https://api.changelly.com'
    self.signature = signature


def request_headers(api_key, signature):
  return {
    'api-key': api_key,
    'sign': signature,
    'Content-Type': 'application/json'
  }


async def index_currencies(session, redis_conn, api_details):
  message = {
    'jsonrpc': '2.0',
    'id': 1,
    'method': 'getCurrenciesFull',
    'params': {}
  }
  serialized_data = json.dumps(message)
  sign = hmac.new(api_details.signature.encode('utf-8'), serialized_data.encode('utf-8'),
                  hashlib.sha512).hexdigest()
  headers = request_headers(api_details.api_key, sign)
  resp = await session.post(api_details.base_url, data=serialized_data, headers=headers)
  if resp.status != 200:
    raise SourceError('Changelly error')
  json_body = await resp.json()
  if 'result' not in json_body:
    raise SourceError('Result not in JSON response')
  result_body = json_body['result']
  currencies = { x['name'].upper(): {'symbol': x['name'].upper(), 'name': x['fullName'], 'changelly': ('available' if x['enabled'] else 'unavailable')} for x in result_body}
  await keystore.add_currency_details(redis_conn, currencies)
