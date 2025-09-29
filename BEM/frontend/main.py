import streamlit as st

from frontend.pages import show_input_page, show_results_page, show_login_form

from src.data_grabber_queue.queue import Queue
from src.polygon_renderer.bem_polygon_renderer import BemPolygonRenderer
from src.polygon_renderer.soh_polygon_renderer import SohPolygonRenderer
from src.polygon_renderer.som_polygon_renderer import SomPolygonRenderer
from src.polygon_renderer.bem_wider_area_polygon_renderer import BemWiderAreaPolygonRenderer
from src.report_renderer.report_section_renderer import ReportSectionRenderer
from src.vessel_data_generator.vortexa.vortexa_vessel_grabber import VortexaVesselGrabber
from src.database.shipping_db_manager import ShippingDBManager

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
        return f"{self.id}. {self.title}"

class MainScreen:
    def __init__(self):
        self.queue = Queue()
        # self.polygon_renderer = SomPolygonRenderer(id=1)
        # BemWiderAreaPolygonRenderer(id=4)
        self.polygon_renderer = [SomPolygonRenderer(id=1),
                                 SohPolygonRenderer(id=2),
                                 BemPolygonRenderer(id=3)]
        self.data_grabber = VortexaVesselGrabber()
        self.body = [Section(id=1, title="Watchlist Vessels (Historical Routes)", type='ALL'),
                     Section(id=2, title="Watchlist Vessels (Just Entered Area)", type='ENTRY'),
                     Section(id=3, title="Watchlist Vessels (Just Exited Area)", type='EXIT')]

        # def process_section(section):
        #     print("Processing section with vessels:", section.render_vessel_list())
        #     if section.type == 'ALL':
        #         section_data = self.data_grabber.grab_all_vessel_data_by_names(self.polygon_renderer, section.render_vessel_list())
        #     elif section.type == 'ENTRY':
        #         section_data = self.data_grabber.grab_entry_vessel_data_by_names(self.polygon_renderer, section.render_vessel_list())
        #     elif section.type == 'EXIT':
        #         section_data = self.data_grabber.grab_exit_vessel_data_by_names(self.polygon_renderer, section.render_vessel_list())
        #     else:
        #         section_data = "No data available for this section type."
        #     section.set_content(section_data)

        def process_section(section, poly_renderer):
            print("Processing section with vessels:", section.render_vessel_list())
            if section.type == 'ALL':
                section_data = self.data_grabber.grab_all_vessel_data_by_names(poly_renderer, section.render_vessel_list())
            elif section.type == 'ENTRY':
                section_data = self.data_grabber.grab_entry_vessel_data_by_names(poly_renderer, section.render_vessel_list())
            elif section.type == 'EXIT':
                section_data = self.data_grabber.grab_exit_vessel_data_by_names(poly_renderer, section.render_vessel_list())
            else:
                section_data = "No data available for this section type."
            section.set_content(section_data)
    
        self.report_renderer = ReportSectionRenderer(self.queue, process_section)

    def start_system(self):
        self.report_renderer.start()
    
    def stop_system(self):
        self.report_renderer.stop()
        print("System shutdown complete")
    
    def run(self):
        st.set_page_config(
            page_title="Vessel Search App (BEM)",
            page_icon="🔍",
            layout="wide",
            initial_sidebar_state="collapsed"
        )
        
        # Custom CSS for better styling
        st.markdown("""
        <style>
        .stButton > button {
            border-radius: 20px;
        }
        .stTextInput > div > div > input {
            border-radius: 10px;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Route to appropriate page
        # if st.session_state.current_page == 'input':
        #     show_input_page()
        if st.session_state.logged_in is True:
            show_input_page()
        if st.session_state.current_page == 'results':
            show_results_page()
        elif st.session_state.current_page == 'login':
            show_login_form()


if __name__ == "__main__":
    @st.cache_resource
    def load_model():
        # Load your ML model here
        return MainScreen()

    st.session_state.screen = load_model()

    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'login'
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'show_modal' not in st.session_state:
        st.session_state.show_modal = False
    if 'db_manager' not in st.session_state:
        st.session_state.db_manager = ShippingDBManager()

    if 'search_words' not in st.session_state:
        st.session_state.search_words = []
        st.session_state.screen.start_system()

    st.session_state.screen.run()

