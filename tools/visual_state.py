import sys


def visual_state(title, state):
    symbol = '\u00a0\u2713\u00a0' if state else '\u00a0\u2717\u00a0'
    sys.stdout.write(f'{title}{symbol}')
    sys.stdout.flush()
    sys.stdout.write("\n")
