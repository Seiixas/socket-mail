from socket import socket, AF_INET, SOCK_STREAM
from typing import Optional

from rich import print

from enums import RequestType, ResponseCode
from models import LoginRequestDto, Request, Response, User, Message


class Client:

    def __init__(self):
        self.socket = socket(AF_INET, SOCK_STREAM)
        self.user: Optional[User] = None

    # Connects to a server
    def connect(self, ip, port) -> bool:
        try:
            self.socket.connect((ip, port))
            return True
        except Exception as e:
            print("Connection failed: " + str(e))
            return False

    # Registers to a server
    def register(self):
        name = input("Enter your name: ").strip()
        username = input("Enter your username: ").strip()
        password = input("Enter your password: ").strip()

        body = User(name, username, password)
        response: Response = Request(RequestType.REGISTER, body).send(self.socket)

        if response.code == ResponseCode.SUCCESS:
            print("Successfully registered")
        else:
            print("Failed to register: " + str(response.content))

    # Login to a server
    def login(self):
        username = input("Enter your username: ").strip()
        password = input("Enter your password: ").strip()

        body = LoginRequestDto(username, password)
        response: Response = Request(RequestType.LOGIN, body).send(self.socket)

        if response.code == ResponseCode.SUCCESS:
            print(response.content)
            self.user = body
        else:
            print("Failed to log in: " + str(response.content))

    def disconnect(self):
        self.user = None

    def send(self):
        recipient = input("Recipient: ").strip()
        subject = input("Subject: ").strip()
        body = input("Body: ").strip()

        body = Message(self.user.username, recipient, subject, body)
        response = Request(RequestType.MESSAGE, body).send(self.socket)

        print(response.content)

    def receive(self):
        response = Request(RequestType.DOWNLOAD_MESSAGE, self.user.username).send(self.socket)

        if response.code == ResponseCode.SUCCESS:
            messages = response.content

            sel = 1

            if len(messages) > 0:
                while sel >= 0:
                    for y, message in enumerate(messages):
                        print(f'[{y + 1}] {message.sender}: {message.subject}')

                    print('')

                    sel = int(input('Message to read (0 or negative to leave): ').strip()) - 1
                    print(messages[sel])
        else:
            print("Failed to receive messages: " + str(response.content))


if __name__ == "__main__":
    client = Client()


    def configure_server():
        host = input("Enter host address: ").strip()
        port = int(input("Enter port number: ").strip())

        connected = client.connect(host, port)

        if connected:
            print('Successfully connected to the server')
            menu.extend([('Register', client.register), ('Login', client.login)])


    menu = [('Configure Server', configure_server)]

    while True:
        for i, item in enumerate(menu):
            print(f'{i + 1}) {item[0]}')

        try:
            selected = int(input('Select an option: ').strip()) - 1
            menu[selected][1]()

            if client.user:
                menu = [('Send', client.send), ('Receive', client.receive), ('Disconnect', client.disconnect)]
            else:
                menu = [('Configure Server', configure_server), ('Register', client.register), ('Login', client.login)]

        except Exception as exception:
            print('Invalid input: ' + str(exception))
