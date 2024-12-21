from typing import List


class Encoder:
    lines: List[str]
    is_array:bool = False

    def __init__(self, lines: List[str]):
        self.lines = lines
        pass

    def execute(self):
        if self.lines[0] == '-1': #None
            return "$-1\r\n".encode('utf-8')

        response = ""
        if self.is_array:
           response += "*" + str(len(self.lines)) + "\r\n"

        for word in self.lines:
            response += "$" + str(len(word)) + "\r\n" + word + "\r\n"

        return response.encode('utf-8')