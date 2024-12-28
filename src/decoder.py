from typing import List

from src.logger import logger


class Decoder:
    lines: List[str]

    def __init__(self, msg: bytes):
        self.lines = [line.decode() for line in msg.splitlines()]

    def _validate_protocol_array(self, command) -> bool:
        try:
            if not command[0].startswith("*") or not command[0][1:].isdigit():
                return False
            array_len = int(command[0][1:])
            if len(command) != array_len * 2 + 1:
                return False
            for pos in range(1, array_len, 2):
                if not command[pos].startswith("$") or not command[pos][1:].isdigit():
                    return False
                word_len = int(command[pos][1:])
                if len(command[pos + 1]) != word_len:
                    return False
            return True
        except IndexError:
            raise

    def split_messages(self):
        splitted_messages = []
        pos = 0
        while pos < len(self.lines):
            cur = pos + 1
            cur_msg = self.lines[pos].encode() + b"\r\n"
            while cur < len(self.lines) and (self.lines[cur][0] not in ["*"] or len(self.lines[cur]) == 1):
                cur_msg +=  self.lines[cur].encode() + b"\r\n"
                cur += 1
            pos = cur
            splitted_messages.append(cur_msg)

        return splitted_messages

    def execute(self) -> List[List[str]]:
        decoded_response = []
        pos = 0
        while pos < len(self.lines):
            args = []
            command = [self.lines[pos]]
            cur = pos + 1
            while cur < len(self.lines) and (self.lines[cur][0] not in ["*"] or len(self.lines[cur]) == 1):
                command.append(self.lines[cur])
                cur += 1
            pos = cur
            self._validate_protocol_array(command)
            for i in range(2, len(command), 2):
                args.append(command[i])

            decoded_response.append(args)

        return decoded_response
