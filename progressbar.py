import time
import sys


class ProgressBar:
    def __init__(self, width):
        self.width = width
        self.progress = 0
        self.one_percent = self.width / 100
        self.add()

    def add(self):
        sys.stdout.write(f'[{(" " * self.width)}')
        sys.stdout.flush()
        sys.stdout.write("\b" * self.width)

    def print_progress(self):
        sys.stdout.write(f'{"#" * round(self.progress * self.one_percent)}{round(self.progress)}%]')
        sys.stdout.write('\r[')
        sys.stdout.flush()

    def set_progress(self, progress):
        self.progress = progress
        self.print_progress()
bar = ProgressBar(40)
bar.set_progress(10.34)
time.sleep(1)
bar.set_progress(12)
time.sleep(1)
bar.set_progress(28)
time.sleep(1)
bar.set_progress(40)
time.sleep(1)
bar.set_progress(60)
time.sleep(1)
bar.set_progress(100)
time.sleep(1)