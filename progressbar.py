import sys


class ProgressBar:
    def __init__(self, width):
        self.width = width
        self.progress = 0
        self.one_percent = self.width / 100
        self.add()
        self.set_progress(0)

    def add(self):
        sys.stdout.write(f'[{(" " * self.width)}]')
        sys.stdout.flush()
        sys.stdout.write("\b" * self.width)

    def print_progress(self):
        if self.progress == 100:
            sys.stdout.write(f'[{"#" * round(self.progress * self.one_percent)}{round(self.progress)}%]')
            sys.stdout.write('\n')
            sys.stdout.flush()
        else:
            sys.stdout.write(f'[{"#" * round(self.progress * self.one_percent)}{round(self.progress)}%]')
            sys.stdout.write('\r')
            sys.stdout.flush()

    def set_progress(self, progress):
        self.progress += progress
        self.print_progress()
