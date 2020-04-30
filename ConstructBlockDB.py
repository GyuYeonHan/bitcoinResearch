import json

import pymysql
from Research2.rpc import RPCHost


def DBselect(db, height):
    cursor = db.cursor()
    sql = "SELECT data FROM blocks WHERE TXID = %s;"
    cursor.execute(sql, height)
    return cursor.fetchall()


def DBinsert(db, height, data):
    try:
        cursor = db.cursor()
        sql = "INSERT INTO blocks VALUES (%s, %s);"
        cursor.execute(sql, (height, data))
        db.commit()
        return True

    except Exception as er:
        print(er)
        return False

rpcPort = 8332
rpcUser = 'gyuyeon'
rpcPassword = 'as7543df'
# Accessing the RPC local server
serverURL = 'http://' + rpcUser + ':' + rpcPassword + '@localhost:' + str(rpcPort)

host = RPCHost(serverURL)
print("Success to connect with RPCserver")

# Open database connection
db = pymysql.connect(host='localhost', port=3306, user='root', passwd='as998077df', db='bitcoin', charset='utf8', autocommit=True)
print("Success to connect with DB server")


try:
    with open("config.json", "r") as config_json:
        config = json.load(config_json)

    blockIndex = config["BlockNumber"]
    blockHash = host.call('getblockhash', blockIndex)
    block = host.call('getblock', blockHash)
    highest_block = host.call('getbestblockhash')

    while blockHash != highest_block:
        block_data = json.dumps(block)
        success = DBinsert(db, blockIndex, block_data)
        if success:
            print("Update block DB by", blockIndex)
            blockIndex = blockIndex + 1
            blockHash = block['nextblockhash']
            block = host.call('getblock', blockHash)

            config["BlockNumber"] = blockIndex
            with open("config.json", "w") as config_json:
                json.dump(config, config_json)
        else:
            print("Error occur when inserting blocks")
            break

except Exception as er:
    print(er)

finally:
    db.close()
