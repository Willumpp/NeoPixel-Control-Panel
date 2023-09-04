import socket
import pickle
import threading

class Sender:

    def __init__(self, host_address, port, debug_mode=False):
        self.host_address = host_address
        self.port = port
        self.debug_mode = debug_mode

        print(f"Searching for host {self.host_address} on port {self.port}")

        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((host_address, port))

        print(f"Connection made with host {self.host_address} on port {self.port}")

    #MAKE SURE TO USE THIS AT END OF CODE
    def close(self):
        self.client_socket.close()
    

    #Uses pickle to serialise the message and send it to the reciever
    def send_serialised_message(self, message):

        if self.debug_mode == True:
            print(f"Sending message: {message}")
        
        # Serialize the message using pickle before sending
        serialised_message = pickle.dumps(message)

        self.client_socket.send(serialised_message)

    #Send raw message without and sanitisation
    def send_message(self, message):
        if self.debug_mode == True:
            print(f"Sending message: {message}")

        self.client_socket.send(message)



class Server:
    def __init__(self, host_address, port, recieved_data_function, debug_mode=False):
        self.host_address = host_address
        self.port = port
        self._server_enabled = True
        self.debug_mode = debug_mode
        self._recieved_data_function = recieved_data_function


    def start_server(self):

        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host_address, self.port))
        self.server_socket.listen(2) #Limits the number of clients who can connect

        print(f"Server started on host {self.host_address} with port {self.port}")

        #Start this as a thread so the rest of the program can run while server listens
        _client_listener = threading.Thread(target=self._start_client_listener)
        _client_listener.start()


    #This listens for any new connecting clients
    #   when a client is found it creates a new thread for passing messages
    def _start_client_listener(self):
        print(f"Started client listener for host {self.host_address}")


        while self._server_enabled:

            client_socket, client_address = self.server_socket.accept()

            print(f"Accepted connection from {client_address}")
            client_handler = threading.Thread(target=self._handle_client, args=(client_socket, self.debug_mode))
            client_handler.start()


    #This listens for any messages the client has sent
    def _handle_client(self, client_socket, debug_messages=False):
        try:
            while self._server_enabled:
                if debug_messages:
                    print(f"Awaiting message from client {client_socket.getpeername()}")

                data = client_socket.recv(2048)

                if not data:
                    break

                # Deserialize the received data using pickle
                message = data #pickle.loads(data)

                if debug_messages:
                    print(f"Received message from {client_socket.getpeername()}: {message}")
                
                #Might be a bad idea:
                message_handler = threading.Thread(target=self._recieved_data_function, args=(message,))
                message_handler.start()
                #self._recieved_data_function(message)


        except Exception as e:
            print(f"Error: {e}")

        finally:
            if debug_messages:
                print(f"Closing connection with client {client_socket.getpeername()}")

            client_socket.close()


    def close(self):
        self._server_enabled = False
        self.server_socket.close()
