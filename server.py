import socket


class Server:
    def __init__(self, **config):
        self.config_manager = config.get('config_manager')
        self.port = config.get('receiving_port')
        self.ready_queue = config.get('ready_queue')
        self.host = self.get_host()
        self.initialize_socket()

    def get_host(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        myip=s.getsockname()[0]
        s.close()
        return myip

    def initialize_socket(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.bind((self.host, self.port))
        print("socket binded to port", self.port)
        self.s.listen(1)
        print('Socket is listening')
        self.connect_socket()

    def connect_socket(self):
        try:
            self.c, self.addr = self.s.accept()
            print('Connected to :', self.addr[0], ':', self.addr[1])
        except Exception as e:
            print(e)

    def start_server(self):
        while True:
            try:
                buffer_size = int(self.config_manager.get_config_by_key('Default', 'buffer_size')[1])
                self.data = self.c.recv(buffer_size, socket.MSG_WAITALL)
                if self.data:
                    self.ready_queue.put(self.data)
            except Exception as e:
                print(e)

    def __del__(self):
        self.shutdown()

    def shutdown(self):
        self.c.close()
        self.s.close()
