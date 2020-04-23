from evennia.server.serversession import ServerSession

class Session(ServerSession)
    def full_width_msg(self, msg, **kwargs):
        client_width = self.protocol_flags.get("SCREENWIDTH", {0:80})
        client_width_px = client_width.get(0)
        self.msg(f"$pad({msg}, {client_width},c,-)")
