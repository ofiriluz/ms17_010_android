import socket
import sys
import threading


class MS1710Listener:
    def __init__(self, host='', port=3000, command_request_callback=None, data_callback=None):
        self.host = host
        self.port = port
        self.is_listener_running = False
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.listener_thread = threading.Thread(target=self.__listener_thread)
        self.command_request_callback = command_request_callback
        self.data_callback = data_callback

    def __listener_thread(self):
        self.socket.listen(1)
        conn, addr = s.accept()

        while self.is_listener_running:
            try:
                data = conn.recv(1024)
                if not data:
                    break
                if self.data_callback:
                    self.data_callback(data)
                if str(data).endswith(">") and self.command_request_callback:
                    command = self.command_request_callback()
                    conn.sendall(command + '\n')

            except socket.error:
                print "Error Occured."
                break
        conn.close()
        self.is_listener_running = False

    def start_listen(self):
        if self.is_listener_running:
            return

        self.is_listener_running = True
        self.listener_thread.start()

    def stop_listen(self):
        if not self.is_listener_running:
            return

        self.is_listener_running = False
        self.listener_thread.join()
