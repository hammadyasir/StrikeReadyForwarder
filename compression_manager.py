import datetime

from base_stage_service import BaseStageService
import sys
import time
import bz2
# import snappy
import zlib
import lzma
import datetime
import copy


class CompressionManager(BaseStageService):
    def __init__(self, **config):
        super().__init__(section='CompressionManager')
        compression_methods = {'bzip': self.bzip, 'zlib': self.zlib, 'lzma': self.lzma}
        header = {'header': {'method': None, 'TimeStamp': None, 'PacketSequance':0}, 'data': None}
        self.header = header
        self.compression_methods = compression_methods

    def lzma(self, msg, level=9):
        msg = bytes(str(msg), 'utf-8')
        msg = lzma.LZMACompressor(msg,level=level)
        return msg

    # def snappy(self, msg, level=9):
    #     pack = []
    #     msg = snappy.compress(msg)
    #     self.header['header']['method'] = 'snappy'
    #     self.header['data'] = msg
    #     pack.append(self.header)
    #     return pack

    def bzip(self, msg, compresslevel=9):
        msg = bytes(str(msg), 'utf-8')
        msg = bz2.compress(msg, compresslevel=compresslevel)
        return msg

    def zlib(self, msg, level=9):
        msg = bytes(str(msg), 'utf-8')
        msg = zlib.compress(msg, level=level)
        return msg

    def do_work(self):
        prev_packets_in_queue = 0
        last_queue_update_time = time.time()
        while True:
            if not self.ready_queue.empty():
                try:

                    message = []
                    size = sys.getsizeof(self.ready_queue)
                    current_packets_in_queue = self.ready_queue.qsize()
                    # print('size is: ',size)
                    chunk_size = int(self.config_manager.get_config_by_key(self.section, 'chunk_size')[1])
                    level = int(self.config_manager.get_config_by_key(self.section, 'level')[1])
                    compression_type = str(self.config_manager.get_config_by_key(self.section, 'method')[1])
                    chunk_size = chunk_size * 1048
                    if size >= chunk_size:
                        last_queue_update_time = time.time()
                        while sys.getsizeof(message) < chunk_size:
                            message.append(self.ready_queue.get())
                    elif prev_packets_in_queue == current_packets_in_queue:
                        # print('size is not updating')
                        timeout = int(self.config_manager.get_config_by_key(str(self.section), 'timeout')[1])
                        if (last_queue_update_time + timeout) <= time.time():
                            for i in range(0, current_packets_in_queue):
                                message.append(self.ready_queue.get())
                    prev_packets_in_queue = current_packets_in_queue
                    if not message == []:
                        func = self.compression_methods.get(compression_type)
                        pack=[]
                        compressed_message = func(message, level)
                        self.header['header']['method'] = compression_type
                        self.header['header']['TimeStamp'] = datetime.datetime.utcnow()
                        self.header['header']['PacketSequance']+= 1
                        self.header['data'] = compressed_message
                        pack.append(copy.deepcopy(self.header))
                        self.packet_queue.put(pack)
                except ValueError:
                    print('Oops! Ready Queue is Empty')


if __name__ == '__main__':
    obj = CompressionManager()
    obj.run()