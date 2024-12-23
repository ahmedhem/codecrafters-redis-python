from typing import List


class Decoder:
    lines: List[str]

    def __init__(self, msg: bytes):
        self.lines = [line.decode() for line in msg.splitlines()]
        print(msg.decode())

    def validate_protocol(self) -> bool:
        try:
            if not self.lines[0].startswith('*') or not self.lines[0][1:].isdigit():
                return False
            array_len = int(self.lines[0][1:])
            if len(self.lines) != array_len * 2 + 1:
                return False
            for pos in range(1, array_len, 2):
                if not self.lines[pos].startswith('$') or not self.lines[pos][1:].isdigit():
                    return False
                word_len = int(self.lines[pos][1:])
                if len(self.lines[pos + 1]) != word_len:
                    return False
            return True
        except IndexError:
            return False

    def execute(self) -> List[str]:
        args = []
        if len(self.lines) == 1: # in form of spaces e.g Echo Hello
            args = self.lines[0].split()

        else: # in form of redis protocol e.g *1\r\n$4\r\nPING\r\n
            if not self.validate_protocol():
                raise Exception('Invalid protocol')

            for i in range(2, len(self.lines), 2):
                args.append(self.lines[i])

        return args
