import threading

class LiveDataManager:
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(LiveDataManager, cls).__new__(cls)
                cls._instance.data = {}
        return cls._instance

    def update_tick(self, token, tick):
        with self._lock:
            self.data[token] = tick

    def get_tick(self, token):
        with self._lock:
            return self.data.get(token)

    def get_all_ticks(self):
        with self._lock:
            return self.data.copy()
