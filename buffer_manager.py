import datetime
import time
import sys
import copy
from base_stage_service import BaseStageService

class BufferManager(BaseStageService):
    def __init__(self, **config):
        super().__init__(section="BufferManager", encryption=False)
        self.header = {'header': {'Source': None, 'SequanceNumber': 0, 'TimeStamp': ''}}

    def do_work(self):
        prev_packets_in_queue = 0
        last_queue_update_time = time.time()
        while True:
            if not self.ready_queue.empty():
                # print('ready queue is not empty')
                message = []
                size = sys.getsizeof(self.ready_queue)
                current_packets_in_queue = self.ready_queue.qsize()
                chunk_size = int(self.config_manager.get_config_by_key(self.section, 'packet_size')[1])
                if size >= chunk_size:
                    last_queue_update_time = time.time()
                    while sys.getsizeof(message) <= chunk_size:
                        # message.append(self.ready_queue.get())
                        if not self.ready_queue.empty():
                            pack = self.ready_queue.get()
                            self.header['header']['Source'] = 'Splunk'
                            self.header['header']['SequanceNumber'] += 1
                            self.header['header']['TimeStamp'] = datetime.datetime.now(datetime.timezone.utc)
                            self.header['header']['data'] = pack
                            message.append(copy.deepcopy(self.header))
                            self.packet_queue.put(message)
                elif prev_packets_in_queue == current_packets_in_queue:
                    timeout = int(self.config_manager.get_config_by_key(str(self.section), 'timeout')[1])
                    if (last_queue_update_time + timeout) <= time.time():
                        if not self.ready_queue.empty():
                            pack = self.ready_queue.get()
                            self.header['header']['Source'] = 'Splunk'
                            self.header['header']['SequanceNumber'] += 1
                            self.header['header']['TimeStamp'] = datetime.datetime.now(datetime.timezone.utc)
                            self.header['header']['data'] = pack
                            message.append(copy.deepcopy(self.header))
                            self.packet_queue.put(message)
                prev_packets_in_queue = current_packets_in_queue

if __name__ == '__main__':
    obj = BufferManager()
    obj.run()
