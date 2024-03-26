import socket
import sys
import time
import signal

def handle_exit_signal(signal, frame):
    global conn
    print("\nexiting...")
    conn.send("EXIT\n".encode())
    time.sleep(1)  # Wait for a short duration
    print("Connection closed.")
    conn.close()
    sys.exit(0)

def connect(ip, port):
    global conn
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((ip, port))
    conn = s
    print('Connected to ', ip, "on port", port)

    signal.signal(signal.SIGINT, handle_exit_signal)

    try:
        while True:
            # Receive data from the target and get user input
            ans = conn.recv(1024).decode()
            sys.stdout.write(ans)
            command = input()

            # Send command
            command += "\n"
            conn.send(command.encode())
            time.sleep(1)

            # Remove the output of the "input()" function
            sys.stdout.write("\033[A" + ans.split("\n")[-1])
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    ip = input("Enter the IP address: ")
    port = int(input("Enter the port: "))
    connect(ip, port)
