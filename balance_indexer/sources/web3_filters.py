import aiohttp
import json

TOKEN_TRANSFER='0xa9059cbb'
FROM='from'
TO='to'
INPUT='input'

addresses = ['0x9b7b2B4f7a391b6F14A81221AE0920A9735B67Fb', '0x5c15BC39d5bb0a1Fce406285271aCF73658f4659', '0xbbd13ca6aace2a8eccbde88bc7849c3c6e4e172e']

def check_address(txn, address):
  if txn[FROM] == address or txn[TO] == address or (txn[INPUT].lower().startswith(TOKEN_TRANSFER) and address[2:].lower() in txn[INPUT].lower()):
    # TODO: async send to web sockets
    print('>>>>>>>>>>>>> txn matched: {} for address: {}'.format(txn, address))


async def filter_pending_transactions(w3, txn_filter, redis_conn):
  print('filter pending transactions')
  for txn_hash in txn_filter.get_new_entries():
    transaction = w3.eth.getTransaction(w3.toHex(txn_hash))
    if transaction:
      for address in addresses:
        check_address(transaction, address)


async def filter_new_blocks(w3, block_filter, redis_conn):
  for block in block_filter.get_new_entries():
    print('block: {}'.format(block))
    # TODO: Get transactions list and if pending pool is now in this, send over a websocket notification
