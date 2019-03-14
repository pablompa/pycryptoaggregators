from blockchain.dash import Dash

if __name__ == "__main__":
    bc = Dash()
    bc.rpc_connect('X', 'Y')
    print(bc.block(height=1500))