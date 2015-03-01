# Grabbed from http://code.activestate.com/recipes/131499-observer-pattern/
# Even though it's simple enough to have figured out to begin with.

__all__ = ['Subject', 'ConsoleViewer']

class Subject(object):
    def __init__(self):
        self._observers = []

    def attach(self, observer):
        if not observer in self._observers:
            self._observers.append(observer)

    def detach(self, observer):
        try:
            self._observers.remove(observer)
        except ValueError:
            pass

    def notify(self, message='', modifier=None):
        for observer in self._observers:
            if modifier != observer:
                observer.update(message)

class ConsoleViewer(object):
    def update(self, message):
        print('{0}'.format(message))

