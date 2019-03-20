import sys
import multiprocessing
from time import time
from datetime import datetime

import aws
from aggregate import Aggregator
from blockchain.dash import Dash


def start_aggregator():
    bc = Dash()
    user, password = None, None
    with open("dash.txt", 'r') as f:
        for line in f:
            l = line.split("=")
            if len(l) > 1:
                if l[0] == 'rpcuser':
                    user = l[1].replace("\n", "")
                elif l[0] == 'rpcpassword':
                    password = l[1].replace("\n", "")
                    
    bc.rpc_connect(user, password)
    agg = Aggregator(bc, "dash_daily.csv", "dash_24h.csv", update_rate=600)
    agg.synchronize()


def start_uploader():               
    now = datetime.utcnow()
    aws.register_file("dash_daily.csv", 24*3600, ref=datetime(now.year, now.month, now.day, minute=10).timestamp())
    aws.register_file("dash_24h.csv", 1200)


if __name__ == "__main__":
    aws_option = True
    if len(sys.argv) > 1:
        if sys.argv[1] == "no_aws":
            aws_option = False
            
    aggregator_process = multiprocessing.Process(target=start_aggregator)
    aggregator_process.start()
    
    if aws_option:
        start_uploader()
    
    aggregator_process.join()
    
    
#    b = bc[15057]
#    t = list(b.transactions)
#    print(t[0])
#    print((b.transactions_count, b.transactions_value))
#    b = bc[1]
#    print(b.reward)

#    start = time()
#    for block in bc:
#        block.transactions_count, block.transactions_value
#        if block.height % 1000 == 0 and block.height > 0:
#            t = time() - start
#            print("Iterated up to {0} blocks. Elapsed: {1:.0f}. Per block: {2:.4f}.".format(block.height, t, t/block.height))
#        #print(block.hash)
#    print("Total time: {}".format(time() - start))