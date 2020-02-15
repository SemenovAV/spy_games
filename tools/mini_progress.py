import sys
import time


def mini_progress(title, sec=0.8):
    pause = sec / 4
    sys.stdout.write(f'{title}\u00a0\u25dc\u00a0')
    sys.stdout.flush()
    sys.stdout.write("\b" * (len(title) + 3))
    time.sleep(pause)
    sys.stdout.write(f'{title}\u00a0\u25dd\u00a0')
    sys.stdout.flush()
    sys.stdout.write("\b" * (len(title) + 3))
    time.sleep(pause)
    sys.stdout.write(f'{title}\u00a0\u25de\u00a0')
    sys.stdout.flush()
    sys.stdout.write("\b" * (len(title) + 3))
    time.sleep(pause)
    sys.stdout.write(f'{title}\u00a0\u25df\u00a0')
    sys.stdout.flush()
    sys.stdout.write("\b" * (len(title) + 3))
    time.sleep(pause)
