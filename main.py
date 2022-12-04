import sys
import threading
import logging

import minecraft_server
import player
import packet

class ColorHandler(logging.StreamHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def emit(self, msg):
        print(colorize(self.format(msg)))

def colorize(text):
    text = text.replace("&0", "\u001b[30m")
    text = text.replace("&1", "\u001b[34m")
    text = text.replace("&2", "\u001b[32m")
    text = text.replace("&3", "\u001b[36m")
    text = text.replace("&4", "\u001b[31m")
    text = text.replace("&5", "\u001b[35m")
    text = text.replace("&6", "\u001b[33m")
    text = text.replace("&7", "\u001b[97m")
    text = text.replace("&8", "\u001b[90m")
    text = text.replace("&9", "\u001b[94m")
    text = text.replace("&a", "\u001b[92m")
    text = text.replace("&b", "\u001b[96m")
    text = text.replace("&c", "\u001b[91m")
    text = text.replace("&d", "\u001b[95m")
    text = text.replace("&e", "\u001b[93m")
    text = text.replace("&f", "\u001b[97m")

    return text + "\u001b[0m"

def main():
    server = minecraft_server.MinecraftServer(logs_folder     ="logs",
                                              config_folder   ="config",
                                              players_folder  ="players",
                                              worlds_folder   ="worlds",
                                              plugins_folder  ="plugins")

    server.start()

    my_handler = ColorHandler()
    my_handler.setLevel(logging.DEBUG)
    my_handler.setFormatter(server.formatter)

    server.logger.addHandler(my_handler)

    console_player = player.Player("(console)", None, 1 << 31)

    console_player.message = server.logger.info
    
    server.used_player_ids.append(0)

    while server.running:
        msg = input()

        if len(msg) == 0:
            pass

        elif msg[0] == '/':
            cmdname, _, cmdargs = msg[1:].partition(" ")

            if cmdname in server.commands:
                server.commands[cmdname](console_player, cmdargs)
            else:
                console_player.message(f"&cInvalid command &d{cmdname}")
        else:
            for k,v in dict(server.online_players).items():
                v.send_packet(packet.MessagePacket(0, f"{console_player.username}: {msg}"))
                    

    sys.exit(0)

if __name__ == "__main__":
    main()
