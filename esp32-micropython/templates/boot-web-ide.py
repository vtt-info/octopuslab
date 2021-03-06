# This file is executed on every boot (including wake-boot from deepsleep)
import esp
esp.osdebug(None)
import webrepl

def setup():
    import util.setup
    util.setup.setup()

def octopus():
    from util.octopus import *
    octopus()

import builtins
builtins.octopus=octopus

def reset():
    import machine
    machine.reset()

# when user enters REPL and executes setup()
webrepl.start()
