import time
import socket
import numpy as np
from generate_pointcloud import generate_random_pointcloud


def main():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(("localhost", 12345))

    try:
        while True:
            pointcloud, _ = generate_random_pointcloud(50, False)

            bytes_pointcloud = pointcloud.astype(np.float32).tobytes()

            client.sendall(len(bytes_pointcloud).to_bytes(4, byteorder="big"))
            client.sendall(bytes_pointcloud)
            print("Data sent")
            time.sleep(1)

    except KeyboardInterrupt:
        print("Program interrupted")

    finally:
        client.close()


if __name__ == "__main__":
    main()
