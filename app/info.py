from app.encoder import Encoder

class Replication:
    header = "#replication"
    role = "master"

    def __init__(self, role = None):
        self.role = role or self.role

    def __str__(self):
        attributes = vars(self)
        key_value_pairs = []
        for key, value in attributes.items():
            key_value_pairs.append(f"{key}:{value}")
        return Encoder(lines = key_value_pairs)

    @classmethod
    def set_role(cls, role):
        cls.role = role
