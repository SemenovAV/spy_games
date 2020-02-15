import sys
import time


def mini_progress(title, sec=1):
    count = round(sec / 1)
    pause = 0.25
    while count:
        count -= 1
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
