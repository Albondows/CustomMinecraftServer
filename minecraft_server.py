from __future__ import annotations
import datetime
import logging
import os
import socket
import threading
import time
import tomllib

import block
import command
import constants
import packet
import player
import world
import rank
import world_generator
import world

class MinecraftServer:
    def __init__(self, logs_folder, config_folder, players_folder, worlds_folder, plugins_folder):
        self.logs_folder          = logs_folder
        self.config_folder        = config_folder
        self.players_folder       = players_folder
        self.worlds_folder        = worlds_folder
        self.plugins_folder       = plugins_folder

        self.logger               = logging.getLogger()
        self.running              = False
        self.server_software_name = "Rainb0wSkeppy's minecraft classic server software"

        self.formatter            = logging.Formatter("[%(levelname)-8s @ %(asctime)s] %(message)s", 
                                                      "%H:%M:%S")
        self.commands             = {}
        self.loaded_plugins       = {}
        self.loaded_worlds        = {}
        self.ranks                = {}

        self.online_players       = {}
        self.used_player_ids      = []

        self.version              = (0, 0, 1)
  
        self.blocks               = dict(block.blocks)
    
    def start(self):
        
        self.running = True
        if not os.path.isdir(self.logs_folder   ): os.mkdir(self.logs_folder)
        if not os.path.isdir(self.config_folder ): os.mkdir(self.config_folder)
        if not os.path.isdir(self.players_folder): os.mkdir(self.players_folder)
        if not os.path.isdir(self.worlds_folder ): os.mkdir(self.worlds_folder)
        if not os.path.isdir(self.plugins_folder): os.mkdir(self.plugins_folder)
        
        self.logger.setLevel(logging.DEBUG)
        
        file_handler = logging.FileHandler(f"{self.logs_folder}/log_{datetime.datetime.now():%Y-%m-%d_%H-%M-%S}.log")
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(self.formatter)

        self.logger.addHandler(file_handler)

        with open(f"{self.config_folder}/server.toml", "rb") as f:
            self.server_config = tomllib.load(f)
        
        self.ranks = rank.load(f"{self.config_folder}/ranks.toml")
        
        #match self.server_config:
        #    case {
        #        "server": {"port": int(), "name": str(), "max_players": int(), "main_world": str(), "heartbeat_url": str()},
        #        "ranks": {"banned": int(), "default": int(), "operator": int()}
        #    }:
        #        pass
        #    case _:
        #        raise ValueError(f"invalid configuration: {self.server_config}")
        
        if not self.world_exists(self.server_config["server"]["main_world"]):
            self.logger.info("Main world does not exist, creating it.")
            self.make_world(self.server_config["server"]["main_world"], 128, 128, 128)
        self.load_world(self.server_config["server"]["main_world"])

        error = self.load_plugin("core")
        if error != "":
            logging.fatal("@@@@@@@@ FAILED TO LOAD CORE PLUGIN @@@@@@@@")
            logging.fatal(error)
            logging.fatal("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")

        print(self.commands, self.ranks)

        ping_thread = threading.Thread(target=self.ping)
        ping_thread.start()

        #heartbeat_thread = threading.Thread(target=self.heartbeat_do)
        #heartbeat_thread.start()

        listen_thread = threading.Thread(target=self.listen)
        listen_thread.start()

    def ping(self):
        while self.running:            
            for k,v in dict(self.online_players).items():
                v.send_bytes(packet.ping_packet.to_bytes())
            
            time.sleep(1)
    
    def heartbeat_do(self, url: str):
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
            heartbeat_socket.send(f"GET /{page} port={port}&max={max}&name={self.http_escape(name)}&public={'True' if public else 'False'}&version={version}&salt={self.http_escape(salt)}&users={users}&software={self.http_escape(software)}&web={'True' if web else 'False'}\r\n".encode("utf-8"))

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
            data = b""
            while len(data) < 131:
                data += connection.recv(131-len(data))
            
            first_packet = packet.player_identification_packet.from_bytes(data)  # All complient clients should first send a player identification packet
            
            if first_packet[2] in self.online_players:
                connection.send(packet.disconnect_packet.to_bytes("&3There is already a player with your username on this server"))
                raise ValueError()
                
            if self.player_saved(first_packet[2]):
                this_player = self.load_player(first_packet[2])
                this_player.connection = connection
            else:
                this_player = player.Player(first_packet[2], connection)
                this_player.rank = self.ranks[max(i for i in self.ranks if i in self.ranks and i <= self.server_config["ranks"]["default"])]

            this_player.logins += 1
            this_player.world = self.server_config["server"]["main_world"]

            def message(msg):
                this_player._message(this_player.format_r(self.format_message(msg)))
            
            this_player.message = message

            self.logger.info(f"{first_packet[2]} connected to the server")

            self.online_players[this_player.username] = this_player
            this_player.player_id = self.get_free_player_id()
            self.used_player_ids.append(this_player.player_id)

            self.loaded_worlds[self.server_config["server"]["main_world"]].send(this_player)

            for k, v in dict(self.online_players).items():
                if v.player_id != this_player.player_id and v.world == this_player.world:
                    v.send_bytes(packet.spawn_player_packet.to_bytes(this_player.player_id, this_player.username, int(this_player.x * 32), int(this_player.y * 32), int(this_player.z * 32), 0, 0))
                    this_player.send_bytes(packet.spawn_player_packet.to_bytes(v.player_id, v.username, int(v.x * 32), int(v.y * 32), int(v.z * 32), 0, 0))
                v.message(this_player.format_s(self.server_config["player"]["connect_message"]))

            while self.running:
                this_packet = this_player.read_packet()

                if this_packet[0] == packet.client_set_block_packet.packet_id:
                    x = this_packet[1]
                    y = this_packet[2]
                    z = this_packet[3]

                    if this_packet[5] in self.blocks:
                        self.loaded_worlds[this_player.world].set_block(x, y, z, 0 if this_packet[4] == 0 else this_packet[5])

                        for k,v in dict(self.online_players).items():
                            if v.player_id != this_player.player_id and v.world == this_player.world:
                                v.send_bytes(packet.server_set_block_packet.to_bytes(x, y, z, 0 if this_packet[4] == 0 else this_packet[5]))
                        
                    else:
                        this_player.message(f"&cInvalid block type &d{this_packet[5]}")

                        this_player.send_bytes(packet.server_set_block_packet.to_bytes(x, y, z, self.loaded_worlds[this_player.world].get_block(this_packet[1], this_packet[2], this_packet[3])))

                elif this_packet[0] == packet.position_orientation_packet.packet_id:
                    this_player.x = this_packet[2] / 32
                    this_player.y = this_packet[3] / 32
                    this_player.z = this_packet[4] / 32

                    for k,v in dict(self.online_players).items():
                        if v.player_id != this_player.player_id and v.world == this_player.world:
                            v.send_bytes(packet.position_orientation_packet.to_bytes(this_player.player_id, int(this_player.x * 32), int(this_player.y * 32), int(this_player.z * 32), this_packet[5], this_packet[6]))
                    
                
                elif this_packet[0] == packet.message_packet.packet_id:
                    message = this_packet[2]

                    if message[0] == '/':
                        self.logger.info(f"{this_player.username} Used command \"{message}\"")
                        cmdname, _, cmdargs = message[1:].partition(" ")

                        if cmdname in self.commands:
                            if this_player.rank.num >= self.commands[cmdname].minrank:
                                self.commands[cmdname].onuse(this_player, cmdargs)
                            else:
                                min_rank = self.ranks[min(i for i in self.ranks if i in self.ranks and i >= self.commands[cmdname].minrank)]
                                this_player.message(f"§errOnly {min_rank.color}{min_rank.name}§err+ can use §cmd/{cmdname}")
                        else:
                            this_player.message(f"§errInvalid command §nms{cmdname}")
                    else:
                        message = this_player.format_s(self.server_config["player"]["message_format"]).replace("%msg%", message)
                        self.logger.info(message)

                        for k,v in dict(self.online_players).items():
                            v.message(message)
                    
                elif this_packet is None:
                    break

        except (OSError, ValueError) as e:
            pass
        
        if this_player is not None:
            for k,v in dict(self.online_players).items():
                if v.player_id != this_player.player_id:
                    v.send_bytes(packet.despawn_player_packet.to_bytes(this_player.player_id))
                    v.message(this_player.format_s(self.server_config["player"]["disconnect_message"]))
                
            self.logger.info(this_player.format_s(self.server_config["player"]["disconnect_message"]))

            self.used_player_ids = [i for i in self.used_player_ids if i != this_player.player_id]

            self.save_player(this_player)

            del self.online_players[this_player.username]
        
        connection.close()
            
    def load_plugin(self, name) -> str:
        if not os.path.exists(f"{self.plugins_folder}/{name}.py"):
            return f"File \"{self.plugins_folder}/{name}.py\" not found"

        with open(f"{self.plugins_folder}/{name}.py") as f:
            code = f.read(-1)

        try:
            local_vars  = locals()
            global_vars = globals()

            exec(code, global_vars, local_vars)
            self.loaded_plugins[name] = local_vars["Plugin"](server=self)#, block=block, command=command, constants=constants, packet=packet, player=player, world=world, rank=rank, world_generator=world_generator, world=world)

        except Exception as e:
            return repr(e)
        
        return ""

    def unload_plugin(self, name):
        self.loaded_plugins[name].unload()
        del self.loaded_plugins[name]
    
    def add_command(self, cmd):
        if not isinstance(cmd, command.Command):
            raise TypeError("command must be a Command")

        self.commands[cmd.name] = cmd
    
    def remove_command(self, name):
        del self.commands[name]

    def get_world(self, name):
        if name in self.loaded_worlds:
            return self.loaded_worlds[name]

        self.load_world(name)

        return self.loaded_worlds[name]
    
    def load_world(self, name):
        with open(f"{self.worlds_folder}/{name}", "rb") as f:
            data = f.read()
        
        self.loaded_worlds[name] = world.World.from_bytes(data)
    
    def make_world(self, name, width, height, length, motd="Welcome!", generator=world_generator.flat_world_generator):
        this_world = world.World(name=name, width=width, height=height, length=length, motd=motd, generator=generator)
        
        with open(f"{self.worlds_folder}/{name}", "wb") as f:
            f.write(this_world.to_bytes())
    
    def save_world(self, name):
        with open(f"{self.worlds_folder}/{name}", "wb") as f:
            print(f.write(self.loaded_worlds[name].to_bytes()))

    def world_exists(self, name):
        return name in os.listdir(self.worlds_folder)
    
    def load_player(self, name):
        with open(f"{self.players_folder}/{name}", "rb") as f:
            data = f.read()
        
        return player.Player.from_bytes(data, self.ranks)
    
    def save_player(self, p):
        with open(f"{self.players_folder}/{p.username}", "wb") as f:
            print(f.write(p.to_bytes()))

    def player_saved(self, name):
        return name in os.listdir(self.players_folder)

    def unload_world(self, name):
        self.save_world(name)
        
        del self.loaded_worlds[name]
    
    def format_message(self, message):
        message = message.replace("§msg", self.server_config["colors"]["message"])
        message = message.replace("§dft", self.server_config["colors"]["default"])
        message = message.replace("§cmd", self.server_config["colors"]["commands"])
        message = message.replace("§nms", self.server_config["colors"]["names"])
        message = message.replace("§err", self.server_config["colors"]["errors"])
        message = message.replace("§arg", self.server_config["colors"]["arguments"])
        # :trollface:
        message = message.replace("$ip", "I am an idiot and tried to use $ip")
        message = message.replace("$skin", "I am an idiot and tried to use $skin")
        # weird bug fix
        message = message.replace("Â", "")
        
        return message