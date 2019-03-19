from misc import bound
from rpc import RPCHost, RPCException


class Blockchain:
    
    def __init__(self, host=None, start=None, stop=None, step=None):
        assert (start is None) or (start >= 0), "Negative block heights not allowed"
        assert (stop is None) or (stop >= 0), "Negative block heights not allowed"
        
        self._host = host
        self._start = 0 if start is None else start
        self._stop = stop
        self._step = step
        
    def __getitem__(self, value):
        if isinstance(value, slice):
            start = 0 if value.start is not None and value.start < 0 else value.start
            stop = 0 if value.stop is not None and value.stop < 0 else value.stop
            return self.__class__(host=self._host, start=start, stop=stop, step=value.step)
        else:
            if value >= self._start and (self._stop is None or value < self._stop):
                try:
                    return self.block(height=value)
                except RPCException:
                    raise IndexError("Block height out of range")
            else:
                raise IndexError("Block height out of range")
            
    def __iter__(self):
        i = self._start
        step = 1 if self._step is None else self._step
        while True:
            if self._stop is not None:
                if step > 0 and i >= self._stop or step < 0 and i <= self._stop:
                    break
            else:
                if i < 0:
                    break
            try:
                yield self.block(height=i)
            except RPCException:
                break
            i += step
                
    def __str__(self):
        string = self.__repr__()
        if self._start is not None:
            string += " from block {}".format(self._start)
        if self._stop is not None:
            string += " from block {}".format(self._stop)
        if self._step is not None:
            string += " in steps of {}".format(self._step)
        return string
        
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
    
    def __init__(self, blockchain: Blockchain, hash_: str = None, height: int = None, data: dict = None):
        self._blockchain = blockchain
        self._hash = hash_
        self._height = height
        self._data = data
        self._load_data()
        
    def __str__(self):
        return self._data.__str__()
    
    def transaction(self, index):
        data = self._data["tx"][index]
        return Transaction(self, id_=data["txid"], index=index, data=data) 
    
    @property
    def height(self):
        return self._height
    
    @property
    def hash(self):
        return self._hash
    
    @property
    def time(self):
        return self._data["time"]
    
    @property
    def mediantime(self):
        return self._data["mediantime"]
    
    @property
    def data(self):
        return self._data
    
    @property
    def transactions(self):
        for i, data in enumerate(self._data["tx"]):
            yield Transaction(self, id_=data["txid"], index=i, data=data)
            
    @property
    def transactions_count(self):
        return len(self._data["tx"])
    
    @property
    def transactions_value(self):
        value = 0
        for transaction in self.transactions:
            value += transaction.value
        return value
    
    @property
    def reward(self):
        return self.transaction(0).value
        
    def _load_data(self):
        if self._hash is None:
            if self._height is not None:
                self._hash = self._blockchain.getblockhash(self._height)
            elif self._data is not None:
                self._hash = self._data["hash"]
            else:
                raise AssertionError("Not enough data to create a block")
                
        if self._data is None:
            self._data = self._blockchain.getblock(self._hash, verbosity=2)
        
        if self._height is None:
            self._height = self._data["height"]
            
        assert self._height == self._data["height"] and self._hash == self._data["hash"], "Incoherent data"
        

class Transaction:
    
    def __init__(self, block: Block, id_: str, index: int = None, data: dict = None):
        self._block = block
        self._id = id_
        self._index = index
        self._data = data
        self._load_data()
        
    def __str__(self):
        return self._data.__str__()
    
    @property
    def value(self):
        value = 0
        for vout in self._data["vout"]:
            value += vout["value"]
        return value
        
    def _load_data(self):
        if self._id is None:
            if self._index is not None:
                self._data = self._block.data["tx"][self._index]
                self._id = self._data["txid"]
            else:
                raise AssertionError("Not enough data to create a transaction")
            
        if self._index is None:
            for i, tx in enumerate(self._block.data["tx"]):
                if tx["txid"] == self._id:
                    self._index = i
                    break
                
        if self._data is None:
            self._data = self._block.data["tx"][self._index]
            
        assert self._id == self._data["txid"], "Incoherent data"
        