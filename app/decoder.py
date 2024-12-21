
class Decoder:
    msg: bytes

    def __init__(self, msg: bytes):
        self.msg = msg

    def execute(self):
        lines = [line.decode() for line in self.msg.splitlines()]
        if len(lines) == 1: # in form of spaces e.g Echo Hello
            words = lines[0].split()
            event = words[0]
            args = words[1:]

        else: # in form of redis protocol e.g *1\r\n$4\r\nPING\r\n
            nr_of_words = int(lines[0][1:])
            event = lines[2]
            args = []
            if nr_of_words > 1:
                for i in range(4, nr_of_words * 2 + 1, 2):
                    args.append(lines[i])

        return event, args
