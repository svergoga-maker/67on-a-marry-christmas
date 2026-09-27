import socket
import threading

HOST = '0.0.0.0'
PORT = 8080

clients = []


def broadcast(data, sender_socket=None):
    for client in list(clients):
        if client == sender_socket:
            continue
        try:
            client.sendall(data)
        except OSError:
            try:
                clients.remove(client)
            except ValueError:
                pass
            client.close()


def handle_client(client_socket):
    buffer = ""
    while True:
        try:
            chunk = client_socket.recv(4096)
            if not chunk:
                break
            buffer += chunk.decode("utf-8", errors="replace")
            while "\n" in buffer:
                line, buffer = buffer.split("\n", 1)
                if line.strip():
                    broadcast((line + "\n").encode("utf-8"), sender_socket=client_socket)
        except OSError:
            break

    if client_socket in clients:
        clients.remove(client_socket)
    client_socket.close()


def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    server_socket.bind((HOST, PORT))
    server_socket.listen(100)
    print(f"Server listening on {HOST}:{PORT}")

    while True:
        client_socket, addr = server_socket.accept()
        print(f"Connection from {addr}")
        clients.append(client_socket)

        thread = threading.Thread(target=handle_client, args=(client_socket,), daemon=True)
        thread.start()


if __name__ == "__main__":
    main()