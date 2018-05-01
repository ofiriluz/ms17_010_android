import socket
import sys
import threading
from collections import deque


class MS1710Listener:
    def __init__(self, host='', port=3000, data_callback=None):
        self.host = host
        self.port = port
        self.is_listener_running = False
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.listener_thread = threading.Thread(target=self.__listener_thread)
        self.data_callback = data_callback
        self.commands_queue = deque()

    def __has_commands_to_execute(self):
        return len(self.commands_queue) > 0

    def __get_next_command(self):
        return self.commands_queue.popleft()

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
                if str(data).endswith(">") and self.__has_commands_to_execute():
                    command = self.__get_next_command()
                    conn.sendall(command + '\n')
            except socket.error:
                print "Error Occured."
                break
        conn.close()
        self.is_listener_running = False

    def add_command_to_queue(self, command):
        self.commands_queue.append(command)

    def clear_commands_queue(self):
        self.commands_queue.clear()

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

    def is_listening(self):
        return self.is_listener_running

