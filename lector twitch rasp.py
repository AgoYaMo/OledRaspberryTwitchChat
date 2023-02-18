from board import SCL, SDA
import busio
from oled_text import OledText

import time
import socket
import re
import textwrap

i2c = busio.I2C(SCL, SDA)

# Create the display, pass its pixel dimensions
oled = OledText(i2c, 128, 64)
oled.auto_show = False

# Write to the oled
s = socket.socket()
s.connect(("irc.chat.twitch.tv", 6667))
s.send("PASS {}\r\n".format("oauth:key").encode("utf-8")) # Ouath key
s.send("NICK {}\r\n".format("username").encode("utf-8")) # Your username
s.send("JOIN #{}\r\n".format("channel").encode("utf-8")) # Twitch channel to join

connected = False
run = True
messages = []

while run:
    response = s.recv(2048).decode("utf-8")
    print(response)
    if response == "PING :tmi.twitch.tv\r\n":
        s.send("PONG :tmi.twitch.tv\r\n".encode("utf-8"))
    else:
        username = re.search(r"\w+", response).group(0)
        CHAT_MSG = re.compile(r"^:\w+!\w+@\w+\.tmi\.twitch\.tv PRIVMSG #\w+ :")
        message = CHAT_MSG.sub("", response).rstrip('\n')
        if 'End of /NAMES list' in message:
            connected = True
            oled.text('Conectado')
            oled.show()
        if connected == True:
            if 'End of /NAMES list' in message:
                pass
            else:
                messages.append(username.title() + ': ' + message)
                pantallaActual = []
                indexLineas = 0
                for i in reversed(messages[-5:]):
                    if indexLineas < 5:
                        lines = textwrap.wrap(i, width=18)
                        for l in reversed(lines[-5:]):
                            indexLineas = indexLineas + 1
                            if indexLineas < 6:
                                pantallaActual.append(l)
                indexPantalla = 1
                for p in reversed(pantallaActual):
                    oled.text(p, indexPantalla)
                    indexPantalla = indexPantalla + 1
                oled.show()
                messages = messages[-5:]
                time.sleep(1)