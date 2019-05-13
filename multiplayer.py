import threading
import socket

"""
"""
class Server(threading.Thread):
    PORT = 50000

    def __init__(self, game):
        super().__init__()
        self.text = ''
        self.client = None
        self.address = None
        self.game = game

        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(('localhost', self.PORT))
        self.server.listen(1)

    def send(self, message):
        try:
            self.server.sendall(bytes(str(message), 'ascii'))
        except Exception as err:
            print(err)
            exit(1)

    def read(self):
        if self.text == 'Close session':
            self.send('shutdown()\n exit 0')
            self.server.shutdown(socket.SHUT_RDWR)
            self.server.close()
    
    def get(self):
        return self.text

    def run(self):
        print('Listening on port' + str(self.PORT))
        self.client, self.address = self.server.accept()
        print('\nConnected to ', self.address + '\n')
        self.client.send(bytes("Connection estabilished with Shooter game Server\n", 'ascii'))
        while True:
            try:
                self.text = str(self.client.recv(4096), 'ascii')
                self.read()
            except Exception as err:
                print(err)


class Client(threading.Thread):
    pass
