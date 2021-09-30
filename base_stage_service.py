import multiprocessing
import server
import client
from config_manager import ConfigManager
import sys
import socket
from abc import ABC, abstractmethod


class BaseStageService(ABC):
    def __init__(self, **config):
        self.config_manager = ConfigManager()
        self.section = config.get("section")
        self.encryption = config.get("encryption")

        # print(type(self.config_manager.get_config_by_key(self.section, 'listening_port')))
        self.l_port = int(self.config_manager.get_config_by_key(self.section, 'listening_port')[1])
        self.host_to_send = str(self.config_manager.get_config_by_key('Default', 'ip_address')[1])
        self.next_stage = str(self.config_manager.get_config_by_key(self.section, 'next_stage')[1])
        self.s_port = int(self.config_manager.get_config_by_key(self.next_stage, 'listening_port')[1])

        self.ready_queue = multiprocessing.Queue()
        self.packet_queue = multiprocessing.Queue()
        self.server = self.get_server()
        self.client = self.get_client()

    def get_server(self):
        return server.Server(receiving_port=self.l_port, ready_queue=self.ready_queue,
                             config_manager=self.config_manager)

    def get_client(self):
        return client.Client(encryption=self.encryption, host=self.host_to_send, sending_port=self.s_port,
                             packet_queue=self.packet_queue)

    def run(self):
        p1 = multiprocessing.Process(target=self.server.start_server, args=())
        p2 = multiprocessing.Process(target=self.do_work, args=())
        p3 = multiprocessing.Process(target=self.client.start_client, args=())

        p1.start()
        p2.start()
        p3.start()

        p1.join()
        p2.join()
        p3.join()

    @abstractmethod
    def do_work(self):
        pass
