import aiohttp
import json

from balance_indexer.errors import SourceError
from balance_indexer import keystore

BASE_URL='https://api.coinwoke.com/v1/tokens'

async def index_erc20_tokens(session, redis_conn):
  total_resp = await session.get(BASE_URL)
  if total_resp.status != 200:
    raise SourceError('Coinwoke ERC20 tokens error')
  total_json_body = await total_resp.json()
  total = total_json_body['total']

  resp = await session.get('{}?limit={}'.format(BASE_URL, total))
  if resp.status != 200:
    raise SourceError('Coinwoke ERC20 tokens error')
  json_body = await resp.json()
  items = json_body['items']
  tokens = [x['symbol'] for x in filter(lambda x: x['coin']['name'] == 'Ethereum', items)]

  # must manually add ETH as an ERC20 token
  tokens.append('ETH')
  await keystore.add_erc20_tokens(redis_conn, tokens)


async def filter_erc20(redis_conn, tokens):
  erc20_tokens = await keystore.get_erc20_tokens(redis_conn)
  erc20_only = [k for k in tokens.items() if k in erc20_tokens]
  return erc20_only
