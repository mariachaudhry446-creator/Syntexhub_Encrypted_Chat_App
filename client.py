import socket
import threading
from cryptography.fernet import Fernet

HOST = '127.0.0.1'
PORT = 55555

def main():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((HOST, PORT))
    
    # Receive encryption key from server
    key = client.recv(1024)
    cipher = Fernet(key)
    print("Connected to SECURE chat server!")
    
    username = input("Enter your username: ")
    # Send encrypted username
    encrypted_username = cipher.encrypt(username.encode())
    client.send(encrypted_username)
    
    def receive_messages():
        while True:
            try:
                encrypted_msg = client.recv(1024)
                if encrypted_msg:
                    # Decrypt the message
                    decrypted = cipher.decrypt(encrypted_msg).decode()
                    print(f"\r{decrypted}")  # \r clears the "You: " line
                    print("You: ", end="", flush=True)
            except:
                print("\nDisconnected from server!")
                client.close()
                break
    
    def send_messages():
        while True:
            message = input("You: ")
            if message.lower() == '/quit':
                client.close()
                break
            try:
                # Encrypt before sending
                encrypted = cipher.encrypt(message.encode())
                client.send(encrypted)
            except:
                break
    
    print("\n✅ All messages are ENCRYPTED with AES!")
    print("Type /quit to exit\n")
    
    threading.Thread(target=receive_messages, daemon=True).start()
    threading.Thread(target=send_messages, daemon=True).start()
    
    while True:
        pass

if __name__ == "__main__":
    main()