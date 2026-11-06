import socket

SERVER_ADDRESS = ("192.168.1.111", 65432)
#BUFFER_SIZE = 4096

def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # socket ipv4 TCP
    s.connect(SERVER_ADDRESS)
    print("Mi sono connesso.")
    while True:
        dati = input("Inserisci il comando -> ")
        print(dati.encode())
        s.sendall((dati+"\n").encode())
        if dati.upper() == "EXIT":
            break
    s.close()

if __name__ == "__main__":
    main()