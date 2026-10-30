import socket
import time
from libreria import AlphaBot

HOST, PORT = '192.168.1.111', 65432

bot = AlphaBot()

# Tabella comando -> funzione (senza parametri)
COMANDI = {
    "forward":  bot.forward,
    "backward": bot.backward,
    "left":     bot.left,
    "right":    bot.right,
    "stop":     bot.stop,
    "faster":   bot.increase_speed,
    "slower":   bot.decrease_speed,
}


def esegui_comando(riga):
    parti = riga.strip().lower().split()
    if not parti:
        return

    nome = parti[0]
    args = parti[1:]

    # speed <0-100>
    if nome == "speed":
        if len(args) == 1 and args[0].lstrip("-").isdigit():
            bot.speed = int(args[0])
        else:
            print("[SERVER] uso: speed <0-100>")
        return

    # Movimento con durata opzionale: forward 2 -> avanti per 2 secondi
    if nome in ("forward", "backward", "left", "right"):
        COMANDI[nome]()
        if args:
            durata = float(args[0]) if args[0].replace(".", "", 1).isdigit() else 0
            time.sleep(min(durata, 10))  # limite di sicurezza
            bot.stop()
        return

    if nome in COMANDI:
        print("eseguo")
        COMANDI[nome]()
        return

    print(f"[SERVER] comando sconosciuto: '{nome}'")


def gestisci_client(conn, addr):
    print(f"[SERVER] Client connesso: {addr}")
    buffer = ""
    with conn:
        while True:
            data = conn.recv(1024)
            if not data:
                break
            buffer += data.decode()
            print(f"ho ricevuto: {data.decode()}")

            # Elabora una riga alla volta (i comandi finiscono con \n)
            while "\n" in buffer:
                riga, buffer = buffer.split("\n", 1)
                if riga.strip().lower() in ("quit", "exit"):
                    bot.stop()
                    print(f"[SERVER] Connessione chiusa: {addr}")
                    return
                print(f"[SERVER] {addr}: '{riga.strip()}'")
                esegui_comando(riga)

    # Il client si è disconnesso: ferma il robot per sicurezza
    bot.stop()
    print(f"[SERVER] Connessione chiusa: {addr}")


def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT))
        s.listen()
        print("[SERVER] In ascolto...")

        while True:
            conn, addr = s.accept()
            gestisci_client(conn, addr)


if __name__ == '__main__':
    main()