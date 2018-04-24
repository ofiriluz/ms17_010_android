import socket
import sys
host = ''        # Symbolic name meaning all available interfaces


port = int(sys.argv[1])     # Arbitrary non-privileged port
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((host, port))
print host, port
s.listen(1)
conn, addr = s.accept()
print('Connected by', addr)
while True:
    try:
        data = conn.recv(1024)
        if not data:
            break
        print data,
        if str(data).endswith(">"):
            command = raw_input()
            conn.sendall(command + '\n')

    except socket.error:
        print "Error Occured."
        break
conn.close()


