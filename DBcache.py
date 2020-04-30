import signal
import os
import sys
import time

sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from Research2.rpc import RPCHost

rpcPort = 8332
rpcUser = 'gyuyeon'
rpcPassword = 'as7543df'
# Accessing the RPC local server
serverURL = 'http://' + rpcUser + ':' + rpcPassword + '@localhost:' + str(rpcPort)

host = RPCHost(serverURL)
print("Success to connect with RPCserver")

interrupt = False


def handler(signum, f):
    global interrupt
    interrupt = True


signal.signal(signal.SIGINT, handler)

try:
    Bestblockhash = host.call('getbestblockhash')
    BestBlock = host.call('getblock', Bestblockhash)

    txcache = {}

    start = time.time()
    BlockIndex = 1
    while (BlockIndex < 10000) and not interrupt:
        blockHash = host.call('getblockhash', BlockIndex)
        block = host.call('getblock', blockHash)
        blockTransactionList = block['tx']

        for tx, index in txcache.items():
            if index < BlockIndex - 1000:
                del txcache[tx]

        for blockTransactionID in blockTransactionList:
            tx = host.call('getrawtransaction', blockTransactionID, True)
            txcache[tx] = BlockIndex
            Vins = tx['vin']

            for Vin in Vins:
                if 'coinbase' in Vin:
                    continue
                else:
                    VinTx = host.call('getrawtransaction', Vin['txid'], True)
                    VinBlockHash = VinTx['blockhash']
                    VinBlock = host.call('getblock', VinBlockHash)
                    InputIndex = VinBlock['height']

        print("update block ", BlockIndex)
        BlockIndex = BlockIndex + 1

    print("Elasped time :", time.time() - start)

except Exception as er:
    print(er)
