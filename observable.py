class Observable:
    def __init__(self):
        self.observers = set()
    
    def json(self):
        return NotImplementedError("Override me!")
    
    def notify_all(self):
        o = self.json()
        for observer in list(self.observers): # make a copy so it doesnt break
            observer.notify(o)
    
    def observe(self, observer):
        self.observers.add(observer)
        observer.notify(self.json())
    
    def unobserve(self, observer):
        self.observers.remove(observer)
    
    def refresh(self, observer):
        observer.notify(self.json())    
