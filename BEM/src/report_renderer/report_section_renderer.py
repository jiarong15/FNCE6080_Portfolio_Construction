from concurrent.futures import ThreadPoolExecutor

import threading
from collections import deque
class ReportSectionRenderer:
    
    def __init__(self, queue, processing_function):
        self.queue = queue
        self.process_function = processing_function
        self.running = False
        self.thread = None
        self.processed_section = deque()
        self.failed_section = deque()
        self.results_lock = threading.Lock()

    def start(self):
        if self.running:
            print("Processor is already running")
            return
            
        self.running = True
        
        self.thread_pool = ThreadPoolExecutor(max_workers=8, thread_name_prefix="Worker")      
        self.coordinator_thread = threading.Thread(target=self._coordination_loop, daemon=True)
        self.coordinator_thread.start()
        print("Section processor started")
    
    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join(timeout=2.0)
        print("Section processor stopped")

    def _coordination_loop(self):
        while self.running:
            section, poly_renderer = self.queue.consume(timeout=1.0)
            if section and poly_renderer:
                print(f"📋 Dispatching section {section.id} with polygon renderer {poly_renderer.id} to worker thread")
                future = self.thread_pool.submit(self._process_single_message, section, poly_renderer)
    
    def _process_single_message(self, section, polygon_renderer):
        if section and polygon_renderer:
            try:
                self.process_function(section, polygon_renderer)
                with self.results_lock:
                    # self.processed_section[section.id] = section
                    self.processed_section.append({
                        'section': section,
                        'polygon_renderer': polygon_renderer
                    })
                print(f"Section {section.id} processed successfully")

            except Exception as e:
                with self.results_lock:
                    print(f"Error processing section {section.id} with polygon renderer {polygon_renderer.id}: {e}")
                    self.failed_section.append({
                        'section': section,
                        'polygon_renderer': polygon_renderer
                    })

    def get_result(self):
        with self.results_lock:
            # earliest_section_id = next(iter(self.processed_section.keys()))
            # section = self.processed_section.pop(earliest_section_id)
            results = self.processed_section.popleft()
            section = results['section']
            polygon_renderer = results['polygon_renderer']
        return section, polygon_renderer
    
    def has_result(self):
        return len(self.processed_section) > 0
    
    