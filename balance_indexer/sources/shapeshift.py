import aiohttp
import json

from balance_indexer.errors import SourceError
from balance_indexer import kms, keystore
from balance_indexer.sources import coinwoke

BASE_URL='https://shapeshift.io'

async def index_currencies(session, redis_conn):
  get_coins_url = '{}/getcoins'.format(BASE_URL)
  resp = await session.get(get_coins_url)
  if resp.status != 200:
    raise SourceError('Shapeshift index currencies error')
  json_body = await resp.json()
  currencies = { k: {'symbol': k, 'name': v['name'], 'img': v['image'], 'img_small': v['imageSmall'], 'shapeshift': v['status']} for k, v in json_body.items() }
  erc20_only = await coinwoke.filter_erc20(redis_conn, currencies)
  await keystore.add_currency_details(redis_conn, erc20_only)


async def index_market_info(session, redis_conn):
  market_info_url = '{}/marketinfo'.format(BASE_URL)
  resp = await session.get(market_info_url)
  if resp.status != 200:
    raise SourceError('Shapeshift index market info error')
  json_body = await resp.json()
  all_pairs = {tuple(pair['pair'].split('_')): pair for pair in json_body}
  await keystore.add_pair_market_info(redis_conn, all_pairs)
