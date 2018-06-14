import sys

class _Getch:
    """Gets a single character from standard input."""
    def __init__(self):
        try:
            self.impl = _GetchWindows()
        except ImportError:
            self.impl = _GetchUnix()

    def __call__(self):
        return self.impl()


class _GetchUnix:
    def __init__(self):
        import tty

    def __call__(self):
        import tty, termios
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch


class _GetchWindows:
    def __init__(self):
        import msvcrt

    def __call__(self):
        import msvcrt
        return msvcrt.getch()


parsenum = (lambda num:
            (sys.maxsize if 0 > num else num))


def read_single_keypress():
    """interface for _Getch that interprets backspace and DEL properly"""
    getch = _Getch()
    x = getch.__call__()
    ox = ord(x)
    if ox == 27 or ox == 127:
        sys.stdout.write(chr(8))
        sys.stdout.write(chr(32))  # hacky? indeed. does it *work*? hell yeah!
        sys.stdout.write(chr(8))

    elif ox == 3: raise KeyboardInterrupt
    elif ox == 4: raise EOFError
    return x


def nbsp(x, y):
    """append x to y as long as x is not DEL or backspace"""
    if ord(x) == 27 or ord(x) == 127:
        try:
            y.pop()
        except IndexError:
            pass
        return y
    y.append(x)
    return y


def thismany(count=-1) -> str:
    """get exactly count chars of stdin"""
    y = []
    count = parsenum(count)
    while len(y) <= count:
        i = read_single_keypress()
        _ = sys.stdout.write(i)
        sys.stdout.flush()
        y = nbsp(i, y)
    return "".join(y)


def until(chars, count=-1) -> str:
    """get chars of stdin until any of chars is read,
    or until count chars have been read, whichever comes first"""
    y = []
    chars = list(chars)
    count = parsenum(count)
    while len(y) <= count:
        i = read_single_keypress()
        _ = sys.stdout.write(i)
        sys.stdout.flush()
        if i in chars:
            break
        y = nbsp(i, y)
    return "".join(y)


def until_not(chars, count=-1) -> str:
    """read stdin until any of chars stop being read,
    or until count chars have been read; whichever comes first"""
    y = []
    chars = list(chars)
    count = parsenum(count)
    while len(y) <= count:
        i = read_single_keypress()
        _ = sys.stdout.write(i)
        sys.stdout.flush()
        if i not in chars:
            break
        y = nbsp(i, y)
    return "".join(y)


def pretty_press() -> str:
    """literally just read any fancy char from stdin let caller do whatever"""
    i = read_single_keypress()
    _ = sys.stdout.write(i)
    sys.stdout.flush()
    return nbsp(i, y)