import socket

SERVER_ADDRESS = ("127.0.0.1", 65432)
BUFFER_SIZE = 4096

def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # socket ipv4 TCP
    s.connect(SERVER_ADDRESS)
    print("Mi sono connesso.")
    while True:
        dati = input("Inserisci il messaggio -> ").upper()
        s.send(dati.encode())
        data = s.recv(BUFFER_SIZE)
        print(data.decode())
        if data.decode() == "EXIT":
            break

    s.close()

if __name__ == "__main__":
    main()