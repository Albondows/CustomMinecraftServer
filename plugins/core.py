class Plugin:
    @classmethod
    def load(cls):
        server.logger.info("Loading plugin")

        server.add_command("help",     cls.help_command, cls.help_command_help)
        server.add_command("commands", cls.commands_command, cls.commands_command_help)
        server.add_command("players",  cls.players_command, cls.players_command_help)
        server.add_command("blocks",   cls.blocks_command, cls.blocks_command_help)

    @classmethod
    def unload(cls):
        server.logger.info("Unloading plugin")
    
    help_command_help = "Seriously?\nSERIOUSLY??"

    def help_command(player, args):
        args = args.split(", ")

        if args[0] == "":
            player.message("&eTo see all commands, use &d/commands")
            player.message("&eTo know how to use a command, use &d/help [command name]")
        elif args[0] in server.command_help:
            for i in server.command_help[args[0]].split("\n"):
                player.message(f"&e{i}")
        else:
            player.message(f"&eUnknown command {args[0]}")

    commands_command_help = "&d/commands &e- lists all commands"

    def commands_command(player, args):
        s = ""
        l = []

        for i in server.commands.keys():
            l.append(i)
        
        l.sort()

        for i in l:
            s += i + ", "
        
        s = s[:-2]

        i = 0

        player.message(f"&d{len(l)} &ecommands:")
        
        while i < len(s)-2:
            if ", " in l:
                l = s[i:i+64].rindex(", ") + 2
            else:
                l = len(s) - i

            player.message(s[i:i+l])
            i += l
    
    players_command_help = "&d/players &e- lists all players"

    def players_command(player, args):
        s = ""
        l = []

        for i in server.online_players.keys():
            l.append(i)
        
        l.sort()

        for i in l:
            s += i + ", "
        
        s = s[:-2]
        i = 0

        player.message(f"&d{len(l)} &players:")
        
        while i < len(s)-2:
            if ", " in l:
                l = s[i:i+64].rindex(", ") + 2
            else:
                l = len(s) - i

            player.message(s[i:i+l])
            i += l
    
    blocks_command_help = "&d/blocks &e- lists all blocks"

    def blocks_command(player, args):
        s = ""
        l = []

        for i in server.blocks.values():
            l.append(i.name)
        
        l.sort()

        for i in l:
            s += i + ", "
        
        s = s[:-2]

        i = 0

        player.message(f"&d{len(l)} &eblocks:")
        
        while i < len(s)-2:
            if ", " in s[i:i+64]:
                l = s[i:i+64].rindex(", ") + 2
            else:
                l = len(s) - i

            player.message(s[i:i+l])
            i += l
