import threading
import queue

class Queue:

    def __init__(self):
        self._queue = queue.Queue(maxsize=10)
        self._lock = threading.Lock()
        
    def publish(self, section, polygon_renderer):
        try:
            self._queue.put((section, polygon_renderer), block=False)
            print(self._queue.queue, "Queue size after publish")
            print(f"Section {section.id} and Polygon Renderer {polygon_renderer.id} published to queue")
            return True
        except queue.Full:
            print(f"Queue is full! Cannot publish section {section.id} with Polygon Renderer {polygon_renderer.id}")
            return False
    
    def consume(self, timeout):
        try:
            section, polygon_renderer = self._queue.get(timeout=timeout)
            print(f"Section {section.id} with polygon renderer {polygon_renderer.id} consumed from queue")
            return section, polygon_renderer
        except queue.Empty:
            return None, None
    
    def size(self):
        return self._queue.qsize()