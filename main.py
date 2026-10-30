import time
from libreria import AlphaBot

def main():
    bot = AlphaBot()

    bot.forward()
    time.sleep(2)
    bot.stop()

if __name__ == "__main__":
    main()