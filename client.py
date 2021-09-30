import socket
import time
import configparser
from cryptography.fernet import Fernet


class Client:
    def __init__(self, **config):
        self.encryption = config.get("encryption")
        self.host = config.get('host')
        self.port = config.get('sending_port')
        self.packet_queue = config.get('packet_queue')
        self.initialize_socket()

    def load_key(self):
        """
        Load the previously generated key
        """
        return open("secret.key", "rb").read()

    def decryption(self,encrypted_message):
        """
        Decrypts an encrypted message
        """
        key = self.load_key()
        f = Fernet(key)
        decrypted_message = f.decrypt(encrypted_message)
        return decrypted_message

    def encrypt_message(self, message):
        """
        Encrypts a message
        """
        key = self.load_key()
        # encoded_message = message.encode()
        f = Fernet(key)
        encrypted_message = f.encrypt(message)
        return encrypted_message+('\n').encode()

    def initialize_socket(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect_socket()

    def connect_socket(self):
        try:
            self.s.connect((self.host, self.port))
        except Exception as e:
            print(e)

    def start_client(self):
        while True:
            if not self.packet_queue.empty():
                message = self.packet_queue.get()
                if self.encryption:
                    message = (str(message)).encode()
                    # print('before encryption: ',message)
                    message = self.encrypt_message(message)
                    print(type(message))
                    print('After encryption: ',message)
                else:
                    message = (str(message)+'\n').encode()
                try:
                    print(message)
                    self.s.send(message,True)
                    print('message sent')
                except Exception as e:
                    print(e)

    def __del__(self):
        self.shutdown()

    def shutdown(self):
        self.s.close()
