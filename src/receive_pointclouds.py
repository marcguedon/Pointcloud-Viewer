import socket
import numpy as np


def receive_data(conn, size):
    data = b""
    while len(data) < size:
        packet = conn.recv(size - len(data))

        if not packet:
            raise ConnectionError("Connection closed")
            # break

        data += packet

    return data


def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("localhost", 8080))
    server.listen(1)

    print("Waiting for a connection...")
    conn, addr = server.accept()
    print(f"Connected to {addr}")

    try:
        while True:
            data_size = receive_data(conn, 4)
            expected_size = int.from_bytes(data_size, byteorder="big")

            data = receive_data(conn, expected_size)

            _ = np.frombuffer(data, dtype=np.float32).reshape((-1, 3))
            print("Data received")

    except KeyboardInterrupt:
        print("Program interrupted")

    finally:
        conn.close()


if __name__ == "__main__":
    main()
