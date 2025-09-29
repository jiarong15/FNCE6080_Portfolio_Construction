from src.data_grabber_queue.queue import Queue
from src.polygon_renderer.bem_polygon_renderer import BemPolygonRenderer
from src.report_renderer.report_section_renderer import ReportSectionRenderer
from src.vessel_data_generator.vortexa.vortexa_vessel_grabber import VortexaVesselGrabber

class Section:
    def __init__(self, id, title, type='DEFAULT'):
        self.id = id
        self.title = title
        self.type = type

        self._content = None
        self._query_vessel_name_list = []

    def set_content(self, content):
        self._content = content

    def render_content(self):
        return self._content

    def set_query_vessel_list(self, vessel_list_names):
        self._query_vessel_name_list = vessel_list_names

    def render_vessel_list(self):
        return self._query_vessel_name_list

    def __repr__(self):
        return f"Section(id={self.id}, title={self.title})"

class MainScreen:
    def __init__(self):
        self.queue = Queue()
        self.polygon_renderer = BemPolygonRenderer()
        self.data_grabber = VortexaVesselGrabber()
        self.body = [Section(id=2, title="Entry Vessels In Zone", type='ENTRY'),
                     Section(id=3, title="Exit Vessels In Zone", type='EXIT')]
        # self.body = [Section(id=1, title="All Vessels In Zone", type='ALL'),
        #              Section(id=2, title="Entry Vessels In Zone", type='ENTRY'),
        #              Section(id=3, title="Exit Vessels In Zone", type='EXIT')]

        self.not_processed_count = len(self.body)

        def process_section(section):
            if section.type == 'ALL':
                section_data = self.data_grabber.grab_all_vessel_data_by_names(self.polygon_renderer, section.render_vessel_list())
            elif section.type == 'ENTRY':
                section_data = self.data_grabber.grab_entry_vessel_data_by_names(self.polygon_renderer, section.render_vessel_list())
            elif section.type == 'EXIT':
                section_data = self.data_grabber.grab_exit_vessel_data_by_names(self.polygon_renderer, section.render_vessel_list())
            else:
                section_data = "No data available for this section type."
            section.set_content(section_data)
    
        self.report_renderer = ReportSectionRenderer(self.queue, process_section)

    def start_system(self):
        self.report_renderer.start()
    
    def stop_system(self):
        self.report_renderer.stop()
        print("System shutdown complete")
    
    def send_section_for_processing(self, user_input_vessel_name):
        for section in self.body:
            section.set_query_vessel_list(user_input_vessel_name)
            success = self.queue.publish(section)
            if success:
                print(f"Section {section.id} sent for processing")
            else:
                print(f"Failed to send section {section.id} for processing")
    
    def render_results(self):
        num_still_processing = len(self.body)
        while num_still_processing > 0:
            if self.report_renderer.has_result():
                content = self.report_renderer.get_result()
                print(f"Rendering content for section {content.id}: {content.render_content()}")
                num_still_processing = num_still_processing - 1

        print(f"Finished processing all sections")

if __name__ == "__main__":
    # Example usage
    screen = MainScreen()
    screen.start_system()

    # Simulate user input
    user_input_vessel_name = ["A"]
    screen.send_section_for_processing(user_input_vessel_name)

    # Render results
    screen.render_results()

    # Stop the system
    screen.stop_system()
