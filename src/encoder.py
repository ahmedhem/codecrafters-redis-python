from typing import List


class Encoder:
    lines: List[str]
    to_array: bool
    to_bulk: bool
    to_simple_string: bool

    def __init__(self, lines: List[str], to_array: bool = False, to_bulk: bool = True, to_simple_string: bool = False):
        self.lines = lines
        self.to_array = to_array
        self.to_bulk = to_bulk
        self.to_simple_string = to_simple_string
        pass

    def execute(self):
        if self.lines and self.lines[0] == "-1":  # None
            return "$-1\r\n".encode("utf-8")

        response = ""
        if self.to_simple_string:
            response = f"+ {' '.join(self.lines)} \r\n"
        elif self.to_array:
            response += "*" + str(len(self.lines)) + "\r\n"
            for word in self.lines:
                response += "$" + str(len(word)) + "\r\n" + word + "\r\n"
        elif self.to_bulk:
            data = ""
            for i in range(len(self.lines)):
                data += self.lines[i]
                if i != len(self.lines) - 1:
                    data += "\r\n"
            response = "$" + str(len(data)) + "\r\n" + data + "\r\n"

        return response.encode("utf-8")
