import socket
import sys
from cryptography.fernet import Fernet


def decryption(encrypted_message):
    """
    Decrypts an encrypted message
    """
    key = load_key()
    f = Fernet(key)
    decrypted_message = f.decrypt(encrypted_message)
    return decrypted_message


def load_key():
    """
    Load the previously generated key
    """
    return open("secret.key", "rb").read()


if __name__ == "__main__":
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    host = s.getsockname()[0]
    s.close()

    port = 4848
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((host, port))
    print("socket binded to port", port)

    # put the socket into listening mode
    s.listen(5)

    while True:
        print("socket is listening")
        c, addr = s.accept()
        print('Connected to :', addr[0], ':', addr[1])

        while True:
            # establish connection with client
            data = c.recv(10485760,socket.MSG_WAITALL)

            if not data:
                print('no data found')
                break
            # print('encrypted message: ', data)
            msg=decryption(data)
            # msg=eval(msg.decode('utf-8'))
            print(type(msg.decode('utf-8')))
            print('decrypted message: ', msg.decode('utf-8'))

            # print('Received on ingestion point: ', msg)

        c.close()

    s.close()
