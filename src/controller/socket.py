from threading import Thread
import socket
import numpy as np
import pyvista as pv
from controller.controller import Controller
from utils.log import Log


class Socket:
    _instance = None

    def __new__(cls):
        if not cls._instance:
            cls._instance = super(Socket, cls).__new__(cls)
            cls._instance._initialized = False

        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        super().__init__()
        self._initialized = True

        self.controller: Controller = Controller()
        self.controller.start_socket_signal.connect(self.start_socket)
        self.controller.stop_socket_signal.connect(self.stop_socket)

        self.port: int = None
        self.conn: socket = None
        self.server: socket = None
        self.connected: bool = False

        self.socket_thread: Thread = None
        self.is_running: bool = False

    def start_socket(self, port: int):
        self.port = port
        self.open_connection()
        self.is_running = True
        self.socket_thread = Thread(target=self.run_socket, daemon=True)
        self.socket_thread.start()

    def open_connection(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(("localhost", self.port))
        self.server.listen(1)

    def run_socket(self):
        while self.is_running:
            self.conn, _ = self.server.accept()  # conn, addr
            self.connected = True
            self.controller.notify(Log.INFO, "Client connected")

            while self.connected:
                data_size = self.receive_data(4)

                if len(data_size) != 4:
                    break

                expected_size = int.from_bytes(data_size, byteorder="big")

                data = self.receive_data(expected_size)

                if len(data) != expected_size:
                    break

                pointcloud_data = np.frombuffer(data, dtype=np.float32).reshape((-1, 3))
                pointcloud_object = pv.PolyData(pointcloud_data)
                self.controller.update_socket_pointcloud_signal.emit(pointcloud_object)

    def receive_data(self, size):
        data = b""

        while len(data) < size:
            try:
                packet = self.conn.recv(size - len(data))

                if not packet:
                    self.connected = False
                    self.conn.close()

                data += packet
            except socket.error:
                self.connected = False
                self.conn.close()
                self.controller.client_disconnected()
                break

        return data

    def stop_socket(self):
        self.is_running = False
        self.conn.close()
