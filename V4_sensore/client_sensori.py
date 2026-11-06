import socket
from pynput import keyboard

SERVER_ADDRESS = ("192.168.0.183", 65432)

# Tabella tasto -> comando (gli stessi del server)
TASTI = {
    "w": "forward",
    "s": "backward",
    "a": "left",
    "d": "right",
}
FRECCE = {
    keyboard.Key.up: "faster",
    keyboard.Key.down: "slower",
}

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # socket ipv4 TCP
tasto_premuto = None  # evita di rimandare il comando mentre il tasto è tenuto premuto


def invia(comando):
    s.sendall((comando + "\n").encode())
    print("Inviato:", comando)


def leggi_tasto(key):
    # I tasti speciali non hanno 'char': in quel caso restituisce None
    carattere = getattr(key, "char", None)
    if carattere is None:
        return None
    return carattere.lower()


def on_press(key):
    global tasto_premuto
    if key == keyboard.Key.esc:
        invia("exit")
        return False  # ferma il listener

    # Freccette: cambio velocità (si può usare anche mentre il robot si muove)
    if key in FRECCE:
        invia(FRECCE[key])
        return

    tasto = leggi_tasto(key)

    # Il sistema ripete l'evento se il tasto resta premuto: invio solo la prima volta
    if tasto in TASTI and tasto_premuto is None:
        tasto_premuto = tasto
        invia(TASTI[tasto])


def on_release(key):
    global tasto_premuto
    tasto = leggi_tasto(key)

    if tasto is not None and tasto == tasto_premuto:
        tasto_premuto = None
        invia("stop")


def main():
    s.connect(SERVER_ADDRESS)
    print("Mi sono connesso. W/A/S/D per muoverti, ESC per uscire.")
    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()
    s.close()


if __name__ == "__main__":
    main()