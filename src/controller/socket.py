from threading import Thread, Event
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
        self.controller.start_socket_signal.connect(
            lambda port, persistence: self.start_socket(port)
        )
        self.controller.pause_socket_signal.connect(self.pause_socket)
        self.controller.stop_socket_signal.connect(self.stop_socket)

        self.port: int = None
        self.conn: socket = None
        self.server: socket = None
        self.connected: bool = False

        self.pause_event: Event = Event()
        self.pause_event.set()
        self.socket_thread: Thread = None
        self.is_running: bool = False

    def start_socket(self, port: int):
        if self.is_running:
            self.pause_event.set()
            self.controller.notify(Log.INFO, "Socket resumed")
            return

        self.port = port
        self.open_connection()
        self.is_running = True
        self.pause_event.set()
        self.controller.notify(Log.SUCCESS, f"Starting socket on port: {port}")
        self.socket_thread = Thread(target=self.run_socket, daemon=True)
        self.socket_thread.start()

    def open_connection(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind(("0.0.0.0", self.port))
        self.server.listen(1)

    def run_socket(self):
        while self.is_running:
            try:
                self.conn, _ = self.server.accept()  # conn, addr
                
            except OSError:
                break

            if not self.is_running:
                break

            self.connected = True
            self.controller.notify(Log.INFO, "Client connected on socket")

            while self.connected:
                self.pause_event.wait()
                data_size = self.receive_data(4)

                if len(data_size) != 4:
                    break

                expected_size = int.from_bytes(data_size, byteorder="big")
                data = self.receive_data(expected_size)

                try:
                    pointcloud_data = np.frombuffer(data, dtype=np.float32).reshape(
                        (-1, 3)
                    )
                    
                except ValueError:
                    self.controller.notify(
                        Log.DEBUG, "Data socket received, but wrong data format"
                    )
                    continue

                pointcloud_object = pv.PolyData(pointcloud_data)
                self.controller.update_socket_pointcloud(pointcloud_object)

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

    def pause_socket(self):
        self.pause_event.clear()

    def stop_socket(self):
        self.is_running = False
        self.pause_event.set()

        if self.conn:
            try:
                self.conn.shutdown(socket.SHUT_RDWR)
                
            except OSError:
                pass
            
            self.conn.close()
            self.conn = None

        if self.server:
            try:
                self.server.shutdown(socket.SHUT_RDWR)
                
            except OSError:
                pass
            
            self.server.close()
            self.server = None
