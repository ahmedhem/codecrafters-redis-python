from typing import List, Any

from src.logger import logger


class Encoder:
    lines: List[str]
    to_array: bool
    to_bulk: bool
    to_int: bool
    to_simple_string: bool
    is_file: bool
    to_simple_array: bool

    def __init__(
        self,
        lines: List[Any],
        to_array: bool = False,
        to_simple_array: bool = False,
        to_bulk: bool = True,
        to_simple_string: bool = False,
        is_file: bool = False,
        to_int:bool = False,
    ):
        self.lines = lines
        self.to_array = to_array
        self.to_bulk = to_bulk
        self.to_simple_string = to_simple_string
        self.is_file = is_file
        self.to_int = to_int
        self.to_simple_array = to_simple_array


    def convert_into_array(self, item):
        response = ""
        if isinstance(item, list):
            response += "*" + str(len(item)) + "\r\n"
            for line in item:
                response += self.convert_into_array(line)
        else:
            response += "$" + str(len(item)) + "\r\n" + item + "\r\n"

        return response

    def execute(self):
        response = ""
        if self.lines and self.lines[0] == "-1":  # None
            return "$-1\r\n".encode("utf-8")
        elif self.to_int:
            response = f":{self.lines[0]}\r\n"
        elif self.to_simple_array:
            response = "*" + str(len(self.lines)) + "\r\n"
            for item in self.lines:
                item = item.decode("utf-8")
                response += str(item)
        elif self.is_file:
            response = f"{len(self.lines[0])}\r\n" + self.lines[0]
        elif self.to_simple_string:
            response = f"+{' '.join(self.lines)}\r\n"
        elif self.to_array:
            response = self.convert_into_array(self.lines)
        elif not self.lines:
            return b""
        elif self.to_bulk:
            data = ""
            for i in range(len(self.lines)):
                data += self.lines[i]
                if i != len(self.lines) - 1:
                    data += "\r\n"
            response = "$" + str(len(data)) + "\r\n" + data + "\r\n"

        return response.encode("utf-8")
