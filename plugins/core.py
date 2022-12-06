import command
import packet
import constants

class Plugin:
    name = "CorePlugin"
    creator = "Rainb0wSkeppy"
    min_ss_version = (0, 0, 1)

    def __init__(self, server):
        self.server = server

        if self.server.version != self.min_ss_version:
            self.server.warn(f"Plugin was made for {self.server.server_software_name} {self.min_ss_version[0]}.{self.min_ss_version[1]}.{self.min_ss_version[2]} but it's running on {self.server.server_software_name} {self.server.version} {self.server.version[0]}.{self.server.version[1]}.{self.server.version[2]}")

        self.server.logger.info("Loading plugin")

        self.server.add_command(command.Command("help",          self.help_command,         self.help_command_help,             constants.RANK_GUEST))
        self.server.add_command(command.Command("commands",      self.commands_command,     self.commands_command_help,         constants.RANK_GUEST))
        self.server.add_command(command.Command("players",       self.players_command,      self.players_command_help,          constants.RANK_GUEST))
        self.server.add_command(command.Command("blocks",        self.blocks_command,       self.blocks_command_help,           constants.RANK_GUEST))
        self.server.add_command(command.Command("goto",          self.goto_command,         self.goto_command_help,             constants.RANK_GUEST))
        #self.server.add_command(command.Command("overseer",     self.overseer_command,     self.overseer_command_help,        constants.RANK_GUEST))
        self.server.add_command(command.Command("save_all",      self.save_all_command,     self.save_all_command_help,         constants.RANK_OPERATOR))
        self.server.add_command(command.Command("ranks",         self.ranks_command,        self.ranks_command_help,            constants.RANK_GUEST))
        self.server.add_command(command.Command("about_player",  self.about_player_command, self.about_player_command_help,     constants.RANK_GUEST))

    def unload(self):
        self.server.logger.info("Unloading plugin")

        self.server.remove_command("help")
        self.server.remove_command("commands")
        self.server.remove_command("players")
        self.server.remove_command("blocks")
        self.server.remove_command("goto")
        self.server.remove_command("save_all")
        self.server.remove_command("ranks")
        self.server.remove_command("about_player")
    
    help_command_help = "§errSeriously?"

    def help_command(self, player, args):
        args = args.split(", ")

        if args[0] == "":
            player.message("§dftTo see all commands, use §cmd/commands")
            player.message("§dftTo know how to use a command, use §cmd/help [command name]")
        elif args[0] in self.server.commands:
            for i in self.server.commands[args[0]].help.split("\n"):
                player.message(f"§dft{i}")
        else:
            player.message(f"§errUnknown command §cmd{args[0]}")

    commands_command_help = "§cmd/commands §dft- lists all commands"

    def commands_command(self, player, args):
        s = ""
        l = []

        for i in self.server.commands.keys():
            l.append(i)
        
        l.sort()

        for i in l:
            s += i + ", "
        
        s = s[:-2]

        i = 0

        player.message(f"§nms{len(l)} §dftcommands:")
        
        while i < len(s)-2:
            if ", " in l:
                l = s[i:i+64].rindex(", ") + 2
            else:
                l = len(s) - i

            player.message(s[i:i+l])
            i += l
    
    players_command_help = "§cmd/players §dft- lists all players"

    def players_command(self, player, args):
        s = ""
        l = []

        for i in self.server.online_players.keys():
            l.append(i)
        
        l.sort()

        for i in l:
            s += i + ", "
        
        s = s[:-2]
        i = 0

        player.message(f"§nms{len(l)} §dftplayers:")
        
        while i < len(s)-2:
            if ", " in l:
                l = s[i:i+64].rindex(", ") + 2
            else:
                l = len(s) - i

            player.message(s[i:i+l])
            i += l
    
    blocks_command_help = "§cmd/blocks §dft- lists all blocks"

    def blocks_command(self, player, args):
        s = ""
        l = []

        for i in self.server.blocks.values():
            l.append(i.name)
        
        l.sort()

        for i in l:
            s += i + ", "
        
        s = s[:-2]

        i = 0

        player.message(f"§nms{len(l)} §dftblocks:")
        
        while i < len(s)-2:
            if ", " in s[i:i+64]:
                l = s[i:i+64].rindex(", ") + 2
            else:
                l = len(s) - i

            player.message(s[i:i+l])
            i += l
    
    ranks_command_help = "§cmd/ranks §dft- lists all ranks"

    def ranks_command(self, player, args):
        s = ""
        l = []

        for k,v in self.server.ranks.items():
            player.message(f"{v.color}{v.name}§dft - Rank: {v.num}, Draw: {v.max_draw}, Realms: {v.max_maps}")
    
    about_player_command_help = "§cmd/about_player §dft- Gives information about a player"

    def about_player_command(self, player, args):
        args = args.split(" ")

        if args == ['']:
            args = [player.username]

        print(args)
        
        that = None
        if args[0] in self.server.online_players:
            that = self.server.online_players[args[0]]
        else:
            that = self.server.load_player(args[0])

        player.message(f"§nms{that.username}§dft has:")
        player.message(f"§dft  Rank of {that.rank.color}{that.rank.name}")
        player.message(f"§dft  Has been on the server §nms{that.logins}§dft times and is currently {'&coffline' if that.connection is None else '&aonline'}")
    
    goto_command_help = "§cmd/goto §arg[map name] §dft- goes to a map"

    def goto_command(self, player, args):
        args = args.split(", ")
        
        if len(args) != 1:
            player.message("§cmd/goto §arg[map name] §dft- goes to a map")
            return
        
        if not self.server.world_exists(args[0]):
            player.message(f"§errInvalid world §nms{args[0]}")
            return
        
        for k, v in dict(self.server.online_players).items():
            if v.player_id != player.player_id and v.world == player.world:
                v.send_packet(packet.DespawnPlayerPacket(player.player_id))
                player.send_packet(packet.DespawnPlayerPacket(v.player_id))
        
        this_world = self.server.get_world(args[0])
        this_world.send(player)
        player.world = args[0]
        
        for k, v in dict(self.server.online_players).items():
            if v.player_id != player.player_id and v.world == player.world:
                v.send_packet(packet.SpawnPlayerPacket(player.player_id, player.username, player.x, player.y, player.z, 0, 0))
                player.send_packet(packet.SpawnPlayerPacket(v.player_id, v.username, v.x, v.y, v.z, 0, 0))

    #overseer_command_help = "§cmd/overseer §dft- ..."

    #def overseer_command(self, player, args):
        #args = args.split(", ")
        ##if len(args) == 0:
        ##    player.message("§cmd/overseer §dft- ...")
        #
        #if self.server.world_exists(player.username):
        #    player.message(f"§errWorld §nms{player.username} §erralready exists")
        #
        #self.server.make_world(player.username, 128, 128, 128)

    save_all_command_help = "§cmd/save_all §dft- ..."

    def save_all_command(self, player, args):
        for i in self.server.loaded_worlds:
            self.server.save_world(i)
