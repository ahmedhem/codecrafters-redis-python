class Replication:
    role = "master"
    master_replid = "8371b4fb1155b71f4a04d3e1bc3e18c4a990aeeb"
    master_repl_offset = "0"

    def __init__(self, role=None, master_replid=None, master_repl_offset=None):
        self.role = role or self.role
        self.master_replid = master_replid or self.master_replid
        self.master_repl_offset = master_repl_offset or self.master_repl_offset
