# This file is part of the octopusLAB project
# The MIT License (MIT)
# Copyright (c) 2016-2020 Jan Copak, Petr Kracik, Vasek Chalupnicek, Jan Cespivo

"""
from util.shell import shell
shell()

> cat / edit / ls / mkdir / cp / rm / find / df ...
--------
autostart:
>>> from config import Config
>>> cc = Config("boot")
>>> cc.set("import_shell",1)
>>> cc.save()
--------
last update: 
"""
__version__ = "0.27 - 29.01.2020"

# toto: ifconfig, kill, wifion, wifioff, wget, wsend, ... 
# from util.shell.terminal import printTitle
from time import sleep_ms, ticks_ms, ticks_diff
from machine import RTC
rtc = RTC() # real time

SEPARATOR_WIDTH = 50

_command_registry = {}
running_process = ""
process_start_time = 0


def shell_run(command_list):
    cmd, *arguments = command_list
    try:
        func = _command_registry[cmd]
    except KeyError as exc:
        raise KeyError(str(exc) + ": command not found")

    func(*arguments)


def _register_command(func_name):
    def _command(func):
        _command_registry[func_name] = func
        return func

    return _command


def command(func_or_name):
    if callable(func_or_name):
        return _register_command(func_or_name.__name__)(func_or_name)
    elif isinstance(func_or_name, str):
        name = func_or_name
        return _register_command(name)

    raise ImportError('bad decorator command')


def add0(sn):
    ret_str=str(sn)
    if int(sn)<10:
       ret_str = "0"+str(sn)
    return ret_str


def get_hhmmss(separator=":",rtc=rtc):
    #get_hhmm(separator) | separator = string: "-" / " "
    hh=add0(rtc.datetime()[4])
    mm=add0(rtc.datetime()[5])
    ss=add0(rtc.datetime()[6])
    return hh + separator + mm + separator + ss


def printBar(num1, num2, char="|", col1=32, col2=33):
    print("[", end="")
    print((("\033[" + str(col1) + "m" + str(char) + "\033[m") * num1), end="")
    print((("\033[" + str(col2) + "m" + str(char) + "\033[m") * num2), end="")
    print("]  ", end="")


@command
def cat(file='/main.py', title=False):  # concatenate - prepare
    """print data: f("filename") """
    fi = open(file, 'r')
    if title:
        from .terminal import printTitle
        printTitle("file > " + file)
        # file statistic
        lines = 0
        words = 0
        characters = 0
        for line in fi:
            wordslist = line.split()
            lines = lines + 1
            words = words + len(wordslist)
            characters = characters + len(line)

        print("Statistic > lines: " + str(lines) + " | words: " + str(
            words) + " | chars: " + str(characters))
        print('-' * SEPARATOR_WIDTH)
        fi = open(file, 'r')
    for line in fi:
        print(line, end="")
    print()
    globals()["cat"] = cat


@command
def edit(file="/main.py"):
    from .editor import edit
    edit(file)


@command
def ls(directory="", line=False, cols=2, goPrint=True):
    from .terminal import terminal_color
    debug = False
    # if goPrint: printTitle("list > " + directory)
    # from os import listdir
    from uos import ilistdir
    from os import stat
    ls_all = ilistdir(directory)
    if debug:
        print(directory)
        print(str(ls_all))
    # ls.sort()
    if goPrint:
        col = 0
        print("%8s %s " % ("d/[B]", "name"))
        for f in ls_all:
            if f[1] == 16384:
                # print(terminal_color(str(f[0])))
                print("%8s %s " % ("---", terminal_color(str(f[0]))))

            if f[1] == 32768:
                # print(str(f[0]) + "" + str(stat(f[0])[6]))
                try:
                    print(
                        "%8s %s" % (str(stat(f[0])[6]), terminal_color(str(f[0]), 36)))
                except:
                    # print("%8s %s" % ( str(stat(directory+f[0])[6]), terminal_color(str(f[0]),36)))
                    print("%8s %s" % ("?", terminal_color(str(f[0]), 36)))

            """if line:
                print("%25s" %  f,end="")
                col += 1
                if col % cols:
                    print()
            else:"""
        print()
    return ls
    # globals()["ls"]=ls


@command
def cp(fileSource, fileTarget="/main.py"):
    from .terminal import printTitle, runningEffect
    printTitle("file_copy to " + fileTarget)
    print("(Always be careful)")
    fs = open(fileSource)
    data = fs.read()
    fs.close()

    runningEffect()
    ft = open(fileTarget, 'w')
    ft.write(data)
    ft.close()
    print(" ok")


@command
def mkdir(directory):
    try:
        from os import mkdir
        mkdir(directory)
    except Exception as e:
        print("Exception: {0}".format(e))


@command
def rm(file=None):
    if file:
        from .terminal import printTitle, runningEffect
        printTitle("remove file > " + file)
        try:
            from os import remove
            print("(Always be careful)")
            remove(file)
            runningEffect()
        except Exception as e:
            print("Exception: {0}".format(e))
    else:
        print("Input param: path + file name")


@command
def find(xstr, directory="examples"): # ?getcwd()
    from os import listdir
    from .terminal import printTitle
    printTitle("find file > " + xstr)
    ls = listdir(directory)
    ls.sort()
    for f in ls:
        if f.find(xstr) > -1:
            print(f)


@command
def df(echo=True):
    from os import statvfs
    if echo:
        print("> flash info: " + str(statvfs("/")))
    flash_free = int(statvfs("/")[0]) * int(statvfs("/")[3])
    if echo:
        print("> flash free: " + str(flash_free))
    return flash_free


@command
def free(echo=True):
    from gc import mem_free
    if echo:
        print("--- RAM free ---> " + str(mem_free()))
    return mem_free()


@command
def top():
    import os, ubinascii, machine
    from .terminal import terminal_color
    bar100 = 30
    print(terminal_color("-" * (bar100 + 20)))
    print(terminal_color("free Memory and Flash >"))
    ram100 = 128000
    b1 = ram100 / bar100
    ram = free(False)
    print("RAM:   ", end="")
    printBar(bar100 - int(ram / b1), int(ram / b1))
    print(terminal_color(str(ram / 1000) + " kB"))

    flash100 = 4000000
    b1 = flash100 / bar100
    flash = df(False)
    print("Flash: ", end="")
    printBar(bar100 - int(flash / b1), int(flash / b1))
    print(terminal_color(str(flash / 1000) + " kB"))

    print(terminal_color("-" * (bar100 + 20)))
    uid = ubinascii.hexlify(machine.unique_id()).decode()
    print(terminal_color("> ESP32 unique_id: ") + str(uid))
    print(terminal_color("> uPy version:  ") + str(os.uname()[3]))
    print(terminal_color("> octopusLAB shell: ") + __version__)

    print(terminal_color("-" * (bar100 + 20)))
    delta = ticks_diff(ticks_ms(), process_start_time)
    print(terminal_color("[1] ",35) + running_process, str(delta/1000))
    print(terminal_color(get_hhmmss()),36)


@command
def ping(url='google.com'):
    from .uping import ping
    ping(url)


@command # TODO
def upgrade(urlTar="https://octopusengine.org/download/micropython/stable.tar"):
    from ..setup import deploy
    from .terminal import printTitle
    printTitle("upgrade from url > ")
    print(urlTar)
    try:
        deploy(urlTar)
    except Exception as e:
        print("Exception: {0}".format(e))


@command
def clear():
    print(chr(27) + "[2J")  # clear terminal
    print("\x1b[2J\x1b[H")  # cursor up


@command
def run(file="/main.py"):
    global running_process, process_start_time
    running_process = file
    process_start_time = ticks_ms()
    exec(open(file).read(), globals())


@command
def ver():
    print(__version__)


@command
def wget(urlApi="http://www.octopusengine.org/api"):
    # get api text / jsoun / etc
    from ..octopus import w
    try:
        w()
    except Exception as e:
        print("Exception: {0}".format(e))

    from urequests import get
    urltxt = urlApi + "/text123.txt"
    try:
        response = get(urltxt)
        dt_str = response.text
    except Exception as e:
        print("Err. read txt from URL")
    print(dt_str)


@command
def pwd():
    from uos import getcwd
    print(getcwd())


@command
def cd(directory):
    from uos import chdir
    chdir(directory)


@command
def exit():
    raise KeyboardInterrupt('shell exiting...')


@command
def help():
    print("octopusLAB - simple shell help:")
    cat("util/octopus_shell_help.txt", False)
    print()


class _release_cwd:
    def __enter__(self):
        from uos import getcwd
        self.current_directory = getcwd()

    def __exit__(self, type, value, traceback):
        from uos import chdir
        chdir(self.current_directory)


def shell():
    from uos import getcwd
    from sys import print_exception
    from .terminal import terminal_color
    with _release_cwd():
        try:
            while True:
                input_str = input(
                    terminal_color("uPyShell", 32) + ":~" + getcwd() + "$ "
                )
                command_list = input_str.split(" ")

                # hacky support for run ./file.py
                if command_list[0][:2] == "./":
                    cmd = command_list.pop(0)
                    command_list = ['run', cmd[2:]] + command_list

                try:
                    shell_run(command_list)
                except Exception as exc:
                    print_exception(exc)
        except KeyboardInterrupt as exc:
            print(exc)
            return
