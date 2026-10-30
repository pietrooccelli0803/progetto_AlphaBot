import time
from libreria import AlphaBot

import socket
import threading

def gestisci_client(conn, addr):
    # Funzione eseguita dal thread isolato
    print(f"[THREAD] Avviato per {addr}")
    with conn:
        while True:
            data = conn.recv(1024)
            if not data:
                break
            # Echo dei dati
            print(f"Ho ricevuto {data.decode()} da {addr}")
            conn.sendall(data)
    print(f"[THREAD] Connessione chiusa: {addr}")

def main():
    HOST, PORT = '192.168.1.101', 65432
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        #s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT))
        s.listen()
        print("[SERVER] In ascolto multithread...")

        while True:
            # accept() blocca finché non arriva un client
            conn, addr = s.accept()
            # Istanzia un nuovo thread passando la funzione
            thread = threading.Thread(target=gestisci_client, args=(conn, addr))
            # Avvia l'esecuzione concorrente
            thread.start()

if __name__ == "__main__":
    main()