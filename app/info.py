class Replication:
    role = "master"

    def __init__(self, role = None):
        self.role = role or self.role

