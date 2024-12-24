from typing import List


class Decoder:
    lines: List[str]

    def __init__(self, msg: bytes):
        self.lines = [line.decode() for line in msg.splitlines()]

    def validate_protocol_array(self) -> bool:
        try:
            if not self.lines[0].startswith("*") or not self.lines[0][1:].isdigit():
                return False
            array_len = int(self.lines[0][1:])
            if len(self.lines) != array_len * 2 + 1:
                return False
            for pos in range(1, array_len, 2):
                if (
                    not self.lines[pos].startswith("$")
                    or not self.lines[pos][1:].isdigit()
                ):
                    return False
                word_len = int(self.lines[pos][1:])
                if len(self.lines[pos + 1]) != word_len:
                    return False
            return True
        except IndexError:
            raise

    def validate_protocol_bulk_string(self) -> bool:
        try:
            if not self.lines[0].startswith("$") or not self.lines[0][1:].isdigit():
                return False

            string_len = int(self.lines[0][1:])
            if len(self.lines[1]) != string_len:
                return False

            return True
        except IndexError:
            raise

    def execute(self) -> List[str]:
        args = []

        if self.lines[0][0] == '+':  # in form of spaces e.g +Echo Hello
            args = self.lines[0].split()
        elif self.lines[0][0] == '*':  # in form of redis protocol e.g *1\r\n$4\r\nPING\r\n
            for i in range(2, len(self.lines), 2):
                args.append(self.lines[i])
        elif self.lines[0][0] == '$':
            args.append(self.lines[1])

        return args
