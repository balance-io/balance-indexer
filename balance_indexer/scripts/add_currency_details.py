import json
import redis

ASSET_PREFIX='asset'

def asset_key(symbol):
  return '{}:{}'.format(ASSET_PREFIX, symbol)

with open('../resources/currency_details.json', 'r') as f:
  currency_details = f.read()
  all_currencies = json.loads(currency_details)
  redis_conn = redis.Redis(host='localhost', port=6379)
  for key, fields in all_currencies.items():
    redis_conn.hmset(asset_key(key), fields)


