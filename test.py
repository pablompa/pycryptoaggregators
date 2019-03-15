from time import time

from blockchain.dash import Dash

if __name__ == "__main__":
    bc = Dash()
    bc.rpc_connect('X', 'Y')
#    b = bc[15057]
#    t = list(b.transactions)
#    print(t[0])
#    print((b.transactions_count, b.transactions_value))
    start = time()
    for block in bc:
        block.transactions_count, block.transactions_value
        if block.height % 1000 == 0 and block.height > 0:
            t = time() - start
            print("Iterated up to {0} blocks. Elapsed: {1:.0f}. Per block: {2:.4f}.".format(block.height, t, t/block.height))
        #print(block.hash)
    print("Total time: {}".format(time() - start))