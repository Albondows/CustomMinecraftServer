import datetime
import logging
import os
import requests
import socket
import string
import threading
import time
import tomllib

import block
import packet
import player
import world
import world_generator

class MinecraftServer:
    def __init__(self, logs_folder, config_folder, players_folder, worlds_folder, plugins_folder):
        self.logs_folder          = logs_folder
        self.config_folder        = config_folder
        self.players_folder       = players_folder
        self.worlds_folder        = worlds_folder
        self.plugins_folder       = plugins_folder

        self.running              = False
        self.server_software_name = "Rainb0wSkeppy's minecraft classic server software"

        self.commands             = {}
        self.command_help         = {}
        self.loaded_plugins       = {}

        self.online_players       = {}
        self.used_player_ids      = []

        self.blocks = dict(block.blocks)
    
    def start(self):
        
        self.running = True
        if not os.path.isdir(self.logs_folder   ): os.mkdir(self.logs_folder)
        if not os.path.isdir(self.config_folder ): os.mkdir(self.config_folder)
        if not os.path.isdir(self.players_folder): os.mkdir(self.players_folder)
        if not os.path.isdir(self.worlds_folder ): os.mkdir(self.worlds_folder)
        if not os.path.isdir(self.plugins_folder): os.mkdir(self.plugins_folder)
        
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.DEBUG)
        self.formatter = logging.Formatter("[%(levelname)-8s @ %(asctime)s] %(message)s", 
                                           "%H:%M:%S")
        
        file_handler = logging.FileHandler(f"{self.logs_folder}/log_{datetime.datetime.now():%Y-%m-%d_%H-%M-%S}.log")
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(self.formatter)

        self.logger.addHandler(file_handler)

        with open(f"{self.config_folder}/server.toml", "rb") as f:
            self.server_config = tomllib.load(f)
        
        match self.server_config:
            case {
                "server": {"port": int(), "name": str(), "max_players": int(), "main_world": str(), "heartbeat_url": str()},
                "ranks": {"banned": int(), "default": int(), "operator": int()}
            }:
                pass
            case _:
                raise ValueError(f"invalid configuration: {self.server_config}")
        
        self.world = world.World(128, 128, 128, name="main", motd="welcome!", generator=world_generator.flat_world_generator)
        
        error = self.load_plugin("core")
        if error != "":
            logging.fatal("@@@@@@@@ FAILED TO LOAD CORE PLUGIN @@@@@@@@")
            logging.fatal(error)
            logging.fatal("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")

        ping_thread = threading.Thread(target=self.ping)
        ping_thread.start()

        heartbeat_thread = threading.Thread(target=self.heartbeat_do)
        heartbeat_thread.start()

        listen_thread = threading.Thread(target=self.listen)
        listen_thread.start()

    def ping(self):
        while self.running:            
            for k,v in dict(self.online_players).items():
                v.send_packet(packet.PingPacket())
            
            time.sleep(1)
    
    def heartbeat_do(self):
        url = self.server_config["server"]["heartbeat_url"]
        if url.startswith('http://'):
            url = url[7:]

        url, _, page = url.partition('/')

        logging.debug(f"{url=}, {page=}")


        while self.running:
            name     = self.server_config["server"]["name"]
            port     = self.server_config["server"]["port"]
            users    = len(self.online_players)
            max      = self.server_config["server"]["max_players"]
            public   = True
            salt     = "X" * 16
            software = self.server_software_name
            web      = False
            version  = 7
            
            heartbeat_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            heartbeat_socket.connect((url, 80))
            heartbeat_socket.send(f"GET /{page} port={port}&max={max}&name={self.http_escape(name)}&public={'True' if public else 'False'}&version={version}&salt={self.http_escape(salt)}&users={users}&software={self.http_escape(software)}&web={'True' if web else 'False'}".encode("utf-8"))

            response = heartbeat_socket.recv(1024).decode("utf-8")

            if response.startswith("http"):
                if self.url is None:
                    self.logger.info(f"You can join the server at {response}")

                self.url = response
            else:
                self.logger.error(response)

            heartbeat_socket.close()
            time.sleep(45)

    def http_escape(self, string):
        safe_characters = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_.-~"
        hex = "0123456789ABCDEF"

        output = ""

        for i in string:
            if i in safe_characters:
                output += i
            else:
                char = ord(i)
                output += "%" + hex[char//16] + hex[char%16]

        return output

    def stop(self):
        self.running = False

    def get_free_player_id(self):
        return min([i for i in range(128) if i not in self.used_player_ids])

    def listen(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind(("", self.server_config["server"]["port"]))
        self.socket.listen()

        while self.running:
            connection, address = self.socket.accept()

            thread = threading.Thread(target=self.accept, args=(connection, address))
            thread.start()
        
        self.socket.close()

    def accept(self, connection, address):
        this_player = None

        self.logger.info(f"{address} connected to the server")

        try:
            data = connection.recv(packet.PlayerIdentificationPacket.size) # All complient clients should first send a player identification packet
            first_packet = packet.PlayerIdentificationPacket.from_bytes(data)
            this_player = player.Player(first_packet.username, connection)

            if first_packet.username in self.online_players:
                this_player.send_packet(packet.DisconnectPacket("&3There is already a player with your username on this server"))
                this_player = None
                raise ValueError()

            self.logger.info(f"{first_packet.username} connected to the server")

            self.online_players[this_player.username] = this_player
            this_player.player_id = self.get_free_player_id()
            self.used_player_ids.append(this_player.player_id)

            self.world.send(this_player)

            for k, v in dict(self.online_players).items():
                if v.player_id != this_player.player_id:
                    v.send_packet(packet.SpawnPlayerPacket(this_player.player_id, this_player.username, this_player.x, this_player.y, this_player.z, 0, 0))
                    v.send_packet(packet.MessagePacket(0, f"&2{this_player.username} connected"))

            for k, v in dict(self.online_players).items():
                this_player.send_packet(packet.SpawnPlayerPacket(v.player_id, v.username, v.x, v.y, v.z, 0, 0))
            
            
            this_player.send_packet(packet.MessagePacket(0, f"&2{this_player.username} connected"))

            while self.running:
                this_packet = this_player.read_packet()

                if isinstance(this_packet, packet.ClientSetBlockPacket):
                    if this_packet.block in self.blocks:
                        this_block = self.blocks[this_packet.block]

                        self.world.set_block(this_packet.x, this_packet.y, this_packet.z, block.AirBlock() if this_packet.mode == 0 else this_block())

                        
                        for k,v in dict(self.online_players).items():
                            if v.player_id != this_player.player_id:
                                v.send_packet(packet.ServerSetBlockPacket(this_packet.x, this_packet.y, this_packet.z, 0 if this_packet.mode == 0 else this_packet.block))
                        
                    else:
                        this_player.send_packet(packet.MessagePacket(0, f"&cInvalid block type &d{this_packet.block}"))

                elif isinstance(this_packet, packet.PositionOrientationPacket):
                    this_player.x = this_packet.x
                    this_player.y = this_packet.y
                    this_player.z = this_packet.z

                    for k,v in dict(self.online_players).items():
                        if v.player_id != this_player.player_id:
                            v.send_packet(packet.PositionOrientationPacket(this_player.player_id, this_packet.x, this_packet.y, this_packet.z, this_packet.pitch, this_packet.yaw))
                    
                
                elif isinstance(this_packet, packet.MessagePacket):
                    
                    if this_packet.message[0] == '/':
                        self.logger.info(f"{this_player.username} Used command \"{this_packet.message}\"")

                        cmdname, _, cmdargs = this_packet.message[1:].partition(" ")

                        if cmdname in self.commands:
                            self.commands[cmdname](this_player, cmdargs)
                        else:
                            this_player.message(f"&cInvalid command &d{cmdname}")
                    else:
                        self.logger.info(f"{this_player.username} said \"{this_packet.message}\"")

                        for k,v in dict(self.online_players).items():
                            v.send_packet(packet.MessagePacket(0, f"{this_player.username}: {this_packet.message}"))
                    
                elif this_packet is None:
                    break

        except (OSError, ValueError) as e:
            pass
        
        if this_player is not None:
            for k,v in dict(self.online_players).items():
                if v.player_id != this_player.player_id:
                    v.send_packet(packet.DespawnPlayerPacket(this_player.player_id))
                    v.send_packet(packet.MessagePacket(0, f"&c{this_player.username} disconnected"))
                
            self.logger.info(f"{this_player.username} disconnected")

            
            self.used_player_ids = [i for i in self.used_player_ids if i != this_player.player_id]
            del self.online_players[this_player.username]
        else:
            self.logger.info(f"{address} disconnected")
        
        connection.close()
            
    def load_plugin(self, name) -> str:
        if not os.path.exists(f"{self.plugins_folder}/{name}.py"):
            return f"File \"{self.plugins_folder}/{name}.py\" not found"

        with open(f"{self.plugins_folder}/{name}.py") as f:
            code = f.read(-1)

        try:
            globals = {"server": self}
            locals = {}

            exec(code, globals, locals)

            self.loaded_plugins[name] = locals["Plugin"]
            locals["Plugin"].load()

        except Exception as e:
            return repr(e)
        
        return ""

    def unload_plugin(self, name):
        self.loaded_plugins[name].unload()
        del self.loaded_plugins[name]
    
    def add_command(self, name, onuse, help):
        self.commands[name] = onuse
        self.command_help[name] = help
    
    def remove_command(self, name):
        del self.commands[name]
        del self.command_help[name]
