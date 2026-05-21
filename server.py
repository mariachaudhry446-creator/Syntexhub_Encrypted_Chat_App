import socket
import threading
from cryptography.fernet import Fernet

HOST = '127.0.0.1'
PORT = 55555
KEY_FILE = "secret.key"

# Generate or load encryption key
def get_key():
    try:
        with open(KEY_FILE, "rb") as f:
            return f.read()
    except:
        key = Fernet.generate_key()
        with open(KEY_FILE, "wb") as f:
            f.write(key)
        return key

KEY = get_key()
cipher = Fernet(KEY)
print(f"Encryption Key: {KEY.decode()}")

clients = []
usernames = []

def broadcast(encrypted_message, sender_client=None):
    for client in clients:
        if client != sender_client:
            try:
                client.send(encrypted_message)
            except:
                remove_client(client)

def remove_client(client):
    if client in clients:
        index = clients.index(client)
        clients.remove(client)
        username = usernames[index]
        usernames.remove(username)
        client.close()
        encrypted_leave = cipher.encrypt(f"🔴 {username} left the chat!".encode())
        broadcast(encrypted_leave)

def handle_client(client):
    # Get username for this client
    index = clients.index(client)
    username = usernames[index]
    
    while True:
        try:
            encrypted_msg = client.recv(1024)
            if encrypted_msg:
                # Decrypt for logging only
                decrypted = cipher.decrypt(encrypted_msg).decode()
                print(f"Message from {username}: {decrypted}")
                
                # Forward encrypted message with username included
                full_message = f"{username}: {decrypted}"
                encrypted_full = cipher.encrypt(full_message.encode())
                broadcast(encrypted_full, client)
            else:
                remove_client(client)
                break
        except:
            remove_client(client)
            break

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()
    print(f"Server running on {HOST}:{PORT}")
    print("Waiting for connections...")
    
    while True:
        client, address = server.accept()
        print(f"Connected: {address}")
        
        # Send encryption key to client
        client.send(KEY)
        
        # Get encrypted username
        encrypted_username = client.recv(1024)
        username = cipher.decrypt(encrypted_username).decode()
        
        usernames.append(username)
        clients.append(client)
        
        print(f"Username: {username}")
        encrypted_join = cipher.encrypt(f"🟢 {username} joined the chat!".encode())
        broadcast(encrypted_join)
        
        thread = threading.Thread(target=handle_client, args=(client,))
        thread.start()

if __name__ == "__main__":
    start_server()