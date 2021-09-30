from base_stage_service import BaseStageService
import sys
import time
import datetime
import copy


class DataForwarder(BaseStageService):
    def __init__(self, **config):
        super().__init__(section="DataForwarder", encryption=True)
        self.header = {'header': {'Source': None, 'SequanceNumber': 0, 'TimeStamp': None, 'NumberOfMessages': None}}

    def do_work(self):
        prev_packets_in_queue = 0
        last_queue_update_time = time.time()
        packets_collected = 0
        while True:
            if not self.ready_queue.empty():
                message = []
                current_packets_in_queue = self.ready_queue.qsize()
                # print('size is: ',size)
                max_packets = int(self.config_manager.get_config_by_key(self.section, 'max_packets')[1])
                # print('max packets are : ', max_packets)
                if current_packets_in_queue >= max_packets:
                    packets_collected = max_packets
                    last_queue_update_time = time.time()
                    for i in range(0, max_packets):
                        message.append(self.ready_queue.get())
                elif prev_packets_in_queue == current_packets_in_queue:
                    # print('size is not updating')
                    timeout = int(self.config_manager.get_config_by_key(str(self.section), 'timeout')[1])
                    if (last_queue_update_time + timeout) <= time.time():
                        packets_collected = current_packets_in_queue
                        for i in range(0, current_packets_in_queue):
                            message.append(self.ready_queue.get())
                prev_packets_in_queue = current_packets_in_queue
                if not message == []:
                    # print(sys.getsizeof(message))
                    self.header['header']['Source'] = 'DataForwarder'
                    self.header['header']['SequanceNumber'] += 1
                    self.header['header']['TimeStamp'] = datetime.datetime.now(datetime.timezone.utc)
                    self.header['header']['NumberOfMessages'] = packets_collected
                    self.header['header']['data'] = message
                    self.packet_queue.put(copy.deepcopy(self.header))
                    break


if __name__ == '__main__':
    obj = DataForwarder()
    obj.run()
