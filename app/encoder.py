from typing import List


class Encoder:
    lines: List[str]

    def __init__(self, lines: List[str]):
        self.lines = lines
        pass

    def execute(self):
        response = "*" + str(len(self.lines)) + "\r\n"
        for word in self.lines:
            response += "$" + str(len(word)) + "\r\n" + word + "\r\n"

        return response.encode('utf-8')