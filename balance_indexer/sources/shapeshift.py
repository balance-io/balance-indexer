import aiohttp
import json

from balance_indexer.errors import SourceError
from balance_indexer import kms, keystore

class ShapeshiftApiDetails(object):
  def __init__(self, api_key):
    self.api_key = kms.get_parameter('shapeshift-api-key') if not api_key else api_key
    self.base_url = 'https://shapeshift.io'


async def index_currencies(session, redis_conn, api_details):
  get_coins_url = '{}/getcoins'.format(api_details.base_url)
  resp = await session.get(get_coins_url)
  if resp.status != 200:
    raise SourceError('Shapeshift error')
  json_body = await resp.json()
  currencies = { k: {'symbol': k, 'name': v['name'], 'img': v['image'], 'img_small': v['imageSmall'], 'shapeshift': v['status']} for k, v in json_body.items() }
  await keystore.add_currency_details(redis_conn, currencies)


async def get_market_info(session, api_details, redis_conn, pair=None):
  market_info_url = '{}/marketinfo'.format(api_details.base_url)
  if not pair:
    market_info_url = '{}/{}'.format(market_info_url, pair)
  resp = await session.get(market_info_url)
  market_info_resp = json.loads(resp)
