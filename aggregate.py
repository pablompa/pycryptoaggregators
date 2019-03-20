import time
import os
import sys
import threading
from datetime import datetime, timedelta

from blockchain import Blockchain, Block

class Aggregator:
    
    max_back_seek_bytes = 128
    
    def __init__(self, blockchain: Blockchain, csv_file_daily: str, csv_file_last_24: str, update_rate: int = 60):
        self._blockchain = blockchain
        self._csv_file_daily = csv_file_daily
        self._csv_file_last_24 = csv_file_last_24
        self._update_rate = update_rate
        self._columns = ["date", "block_height", "transactions", "amounts", "reward", "supply"]
        self._date_format = "%Y-%m-%d"
        self._last_daily_supply = 0
        
    def synchronize(self):
        daily_thread = threading.Thread(target=self._synchronize_daily, daemon=True)
        last_24h_thread = threading.Thread(target=self._synchronize_last_24h, daemon=True)
        daily_thread.start()
        last_24h_thread.start()
        daily_thread.join()
        last_24h_thread.join()
        
    def _synchronize_last_24h(self):
        while True:
            block_height = self._blockchain.getblockcount() - 1
            bc = self._blockchain[block_height:-1:-1]
            now = datetime.utcnow()
            new_data = self._new_data(now)
            for block in bc:
                block_time = datetime.utcfromtimestamp(block.mediantime)
                if block_time + timedelta(days=1) < now:
                    # We have completed the aggregation of the last 24h
                    print("Last 24h aggregated: {}".format(new_data))
                    sys.stdout.flush()
                    with open(self._csv_file_last_24, 'w') as f:
                        header_line = ""
                        for column in self._columns:
                            header_line += column + ","
                        f.write(header_line[:-1] + self._data_to_line(new_data))
                    break
                else:
                    new_data["transactions"] += block.transactions_count
                    new_data["amounts"] += block.transactions_value
                    new_data["reward"] += block.reward
                    new_data["supply"] = self._last_daily_supply + new_data["reward"]
                    new_data["block_height"] = block.height
                    
            time.sleep(self._update_rate)
            
    def _synchronize_daily(self):
        while True:
            # Open daily csv file
            last_block = -1
            last_line_data = None
            with open(self._csv_file_daily, 'a+') as f:
                f.seek(0, os.SEEK_END)
                f.seek(f.tell() - min(f.tell(), 512), os.SEEK_SET)
                tail = f.read().split('\n')[-1]
                if tail != "":
                    try:
                        last_line_data = self._line_data(tail)
                        last_block = int(last_line_data["block_height"])
                    except Exception:
                        # Corrupted file.
                        last_block = -1
                        last_line_data = None

            # Slice blockchain from last block in the csv file
            bc = self._blockchain[last_block+1:]
            # Aggregate each day and write to file
            if last_block == -1:
                # The cause could be a corrupted file
                with open(self._csv_file_daily, 'w') as f:
                    header_line = ""
                    for column in self._columns:
                        header_line += column + ","
                    f.write(header_line[:-1])
                date = self._block_date(bc[0])
                self._last_daily_supply  = 0
            else:
                date = datetime.strptime(last_line_data["date"], self._date_format) + timedelta(days=1)
                self._last_daily_supply  = float(last_line_data["supply"])
                
            new_data = self._new_data(date)
            for block in bc:
                block_date = self._block_date(block)
                if block_date > date:
                    # We have completed the aggregation of one day
                    print("New day aggregated: {}".format(new_data))
                    sys.stdout.flush()
                    with open(self._csv_file_daily, 'a') as f:
                        f.write(self._data_to_line(new_data))
                    self._last_daily_supply  = new_data["supply"]
                    date = block_date
                    new_data = self._new_data(date)
                else:
                    new_data["transactions"] += block.transactions_count
                    new_data["amounts"] += block.transactions_value
                    new_data["reward"] += block.reward
                    new_data["supply"] = self._last_daily_supply  + new_data["reward"]
                    new_data["block_height"] = block.height
                    
            while date + timedelta(days=1) > datetime.utcnow():
                time.sleep(self._update_rate)
            
    @staticmethod
    def _block_date(block: Block):
        block_timestamp = datetime.utcfromtimestamp(block.mediantime)
        return datetime(block_timestamp.year, block_timestamp.month, block_timestamp.day)
            
    def _line_data(self, line: str):
        return {column: value for column, value in zip(self._columns, line.split(','))}
    
    def _new_data(self, date: datetime):
        data = {column: 0 for column in self._columns}
        data["date"] = date.strftime(self._date_format)
        return data
    
    def _data_to_line(self, data):
        line = "\n"
        for i, column in enumerate(self._columns):
            if column in ("block_height", "transactions"):
                line += "{:.0f}".format(data[column])
            elif column == "date":
                line += data[column]
            else:
                line += "{:.8f}".format(data[column])
            if i < len(self._columns) - 1:
                line += ","
        return line
