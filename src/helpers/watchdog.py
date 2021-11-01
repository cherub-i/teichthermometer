import machine

class Watchdog:
    def __init__(self, active=True):
        self._active=active
        if (self._active):
            self._watchdog = machine.WDT()
    
    def feed(self):
        if (self._active):
            self._watchdog.feed()