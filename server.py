import socket
import threading
from protocol import SERVER_ADDRESS, receive_data, send_data


clients = []


def broadcast(message, client_except=None):
    for client in clients:
        if client != client_except:
            try:
                send_data(client, message)
            except Exception as e:
                print("[EXCEPTION]", e)


def recieve(client):
    while True:
        try:
            recieved = receive_data(client)

            if recieved is not None:
                points = recieved['points']
                print(points)

                broadcast(recieved, client)
            else:
                break
        except Exception as e:
            print("[EXCEPTION]", e)
            break

    clients.remove(client)
    client.close()


def wait_for_connection(server):
    while True:

        try:
            client, address = server.accept()
            print(f'Connected with {address}')
            clients.append(client)
            print("[CLIENTS]", len(clients))
            thread = threading.Thread(target=recieve, args=(client,), daemon=True)
            thread.start()
        except Exception as e:
            print("[EXCEPTION]", e)
            break

    print("SERVER CRASHED!")


def main():
    server = socket.socket()
    server.bind(SERVER_ADDRESS)

    server.listen(5)
    print("[STARTED] Waiting for connections...")
    accept_thread = threading.Thread(target=wait_for_connection, args=(server,))
    accept_thread.start()
    accept_thread.join()
    server.close()

if __name__ == '__main__':
    main()
