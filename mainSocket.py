import socket
import threading
from libreria import AlphaBot

HOST, PORT = '0.0.0.0', 65432

# Un solo robot condiviso da tutti i thread: serve un lock
bot = AlphaBot()
lock_bot = threading.Lock()

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
    """Interpreta una riga tipo 'forward' o 'speed 70' ed esegue la funzione."""
    parti = riga.strip().lower().split()
    if not parti:
        return "ERRORE: comando vuoto"

    nome = parti[0]
    args = parti[1:]

    with lock_bot:
        # Comando con parametro: speed <0-100>
        if nome == "speed":
            if len(args) != 1 or not args[0].lstrip("-").isdigit():
                return "ERRORE: uso 'speed <0-100>'"
            bot.speed = int(args[0])
            return f"OK speed={bot.speed}"

        # Comando con durata opzionale: forward 2 -> avanti per 2 secondi
        if nome in ("forward", "backward", "left", "right"):
            COMANDI[nome]()
            if args:
                try:
                    durata = float(args[0])
                except ValueError:
                    bot.stop()
                    return "ERRORE: durata non valida"
                import time
                time.sleep(min(durata, 10))  # limite di sicurezza
                bot.stop()
            return "OK"

        if nome in COMANDI:
            COMANDI[nome]()
            return "OK"

    return f"ERRORE: comando sconosciuto '{nome}'"


def gestisci_client(conn, addr):
    print(f"[THREAD] Avviato per {addr}")
    buffer = ""
    with conn:
        while True:
            data = conn.recv(1024)
            if not data:
                break
            buffer += data.decode(errors="ignore")

            # Elabora una riga alla volta (i comandi finiscono con \n)
            while "\n" in buffer:
                riga, buffer = buffer.split("\n", 1)
                if riga.strip().lower() in ("quit", "exit"):
                    conn.sendall(b"BYE\n")
                    print(f"[THREAD] Connessione chiusa: {addr}")
                    return
                risposta = esegui_comando(riga)
                print(f"[THREAD] {addr}: '{riga.strip()}' -> {risposta}")
                conn.sendall((risposta + "\n").encode())

    # Il client si è disconnesso: ferma il robot per sicurezza
    with lock_bot:
        bot.stop()
    print(f"[THREAD] Connessione chiusa: {addr}")


def main():
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((HOST, PORT))
            s.listen()
            print("[SERVER] In ascolto multithread...")

            while True:
                conn, addr = s.accept()
                t = threading.Thread(target=gestisci_client,
                                     args=(conn, addr), daemon=True)
                t.start()
    except KeyboardInterrupt:
        print("\n[SERVER] Chiusura...")
    finally:
        bot.cleanup()


if __name__ == '__main__':
    main()