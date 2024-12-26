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

    def _validate_protocol_bulk_string(self, command) -> bool:
        try:
            if not command[0].startswith("$") or not command[0][1:].isdigit():
                return False

            string_len = int(command[0][1:])
            if len(command[1]) != string_len:
                return False

            return True
        except IndexError:
            raise

    def execute(self) -> List[List[str]]:
        logger.log("Decoding Started")
        response = []
        pos = 0
        while pos < len(self.lines):
            args = []
            command = [self.lines[pos]]
            cur = pos + 1
            while cur < len(self.lines) and (self.lines[cur][0] not in ["*"]):
                command.append(self.lines[cur])
                cur += 1
            pos = cur
            logger.log(" ".join(command))
            if command[0][0] == "+":  # in form of spaces e.g +Echo Hello
                args = command[0].split()
            elif (
                command[0][0] == "*"
            ):  # in form of redis protocol e.g *1\r\n$4\r\nPING\r\n
                self._validate_protocol_array(command)
                for i in range(2, len(command), 2):
                    args.append(command[i])
            elif command[0][0] == "$":
                self._validate_protocol_bulk_string(command)
                args.append(command[1])

            response.append(args)
        logger.log("Decoding Ended")

        return response
