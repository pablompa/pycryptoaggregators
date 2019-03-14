from misc import bound
from rpc import RPCHost


class Blockchain:
    
    def __init__(self):
        self._host = None
        
    def block(self, hash_: str = None, height: int = None):
        return Block(self, hash_, height)
    
    # RPC
    def rpc_connect(self, usr, pwd, ip='localhost', port=9998):
        """
        Default port for the dash mainnet is 9998.
        The port number depends on the one written in dash.conf file.
        The RPC username and RPC password MUST match the one in dash.conf file.
        """
        serverURL = 'http://{0}:{1}@localhost:{2}'.format(usr, pwd, port)
        self._host = RPCHost(serverURL)
    
    def getinfo(self):
        return self._rpc('getinfo')
    
    def getblock(self, block_hash: str, verbosity: int = 0):
        return self._rpc('getblock', block_hash, bound(verbosity, (0, 2)))
    
    def getblockchaininfo(self):
        return self._rpc('getblockchaininfo')
    
    def getblockcount(self):
        return self._rpc('getblockcount')
    
    def getblockhash(self, height: int):
        return self._rpc('getblockhash', height)
    
    
    def _rpc(self, method: str, *args):
        return self._host.call(method, *args)
    

class Block:
    
    def __init__(self, blockchain: Blockchain, hash_: str = None, height: int = None):
        super().__init__()
        self._blockchain = blockchain
        self._hash = hash_
        self._height = height
        self._data = None
        self._load_block_data()
        
    def __str__(self):
        return self._data.__str__()
        
    def _load_block_data(self):
        assert self._hash is not None or self._height is not None, "Cannot load data."
        
        if self._hash is None:
            self._hash = self._blockchain.getblockhash(self._height)
            
        self._data = self._blockchain.getblock(self._hash, verbosity=2)