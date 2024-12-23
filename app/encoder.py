from typing import List


class Encoder:
    lines: List[str]
    to_array:bool

    def __init__(self, lines: List[str], to_array:bool = False):
        self.lines = lines
        self.to_array = to_array
        pass

    def execute(self):

        response = ""
        if self.to_array:
           response += "*" + str(len(self.lines)) + "\r\n"

        if self.lines[0] == '-1': #None
            return (response + "$-1\r\n").encode('utf-8')

        for word in self.lines:
            response += "$" + str(len(word)) + "\r\n" + word + "\r\n"

        return response.encode('utf-8')