import streamlit as st
import base64
from streamlit.components.v1 import html
from streamlit_js_eval import streamlit_js_eval

import matplotlib.cm as cm
import matplotlib.colors as colors

import folium
from folium.plugins import PolyLineTextPath
from streamlit_folium import st_folium
from src.polygon_renderer import BemPolygonRenderer, SohPolygonRenderer, SomPolygonRenderer

def group_vessel_positions_by_imo_helper(vessel_positions_df):
    grouped_points = {}
    n_vessels = len(vessel_positions_df.groupby("IMO"))
    colormap = cm.get_cmap("tab10", n_vessels)
    norm = colors.Normalize(vmin=0, vmax=n_vessels - 1)
    id = 0
    for imo, group in vessel_positions_df.groupby("IMO"):
        color = colors.to_hex(colormap(norm(id)))
        vessel_name = group["Vessel Name"].iloc[0]
        points = [
            [lat, lon, vessel_name, "🚢", color, 1.0]
            for lat, lon in zip(group["Latitude"], group["Longitude"])
        ]
        grouped_points[imo] = points
        id += 1
    return grouped_points

# @st.dialog("Bab El Mandeb Region (Past 3 Days Vessel Movements)", width='large')
def show_bem_dialog(vessel_positions_df):
    bem = BemPolygonRenderer(id=3)
    bem_coords = bem.get_polygon_coordinates()
    center_coords = bem.get_center_coordinates()
    bem_coords = [[v, k] for k, v in bem_coords]
    
    m = folium.Map(location=center_coords, zoom_start=7)
    folium.Polygon(
        bem_coords,
        color="red",
        fill=True,
        fill_opacity=0.4,
        popup="Highlighted Region"
    ).add_to(m)

    grouped_points = group_vessel_positions_by_imo_helper(vessel_positions_df)

    def get_map(m, points_by_imo):
        for imo, points in points_by_imo.items():
            # points = [
            #     [14.2346661800, 42.2983343900, "Ship C", "🚢", "green", 1.0],
            #     [14.0202641600, 42.3843925400, "Ship C", "🚢", "green", 1.0],
            #     [13.8438574300, 42.4945851600, "Ship C", "🚢", "green", 1.0],
            #     [13.6484530500, 42.6127518900, "Ship C", "🚢", "green", 1.0],
            # ]
            
            line = folium.PolyLine(
                locations=list(map(lambda p: p[:2], points)),
                color=points[0][-2],
                weight=2,
                opacity=0.0001
            ).add_to(m)

            PolyLineTextPath(
                line,
                " ➤   ",
                repeat=True,
                offset=10,
                attributes={
                    'fill': points[0][-2],
                    'font-weight': 'bold',
                    'font-size': '16',
                    'opacity': '0.7'
                }
            ).add_to(m)

            for lat, lon, label, symbol, color, opacity in points:
                folium.Marker(
                    [lat, lon],
                    icon=folium.DivIcon(
                        html=f"""
                            <div style="
                                font-size:28px;
                                color:{color};
                                opacity:{opacity};
                                text-align:center;
                                ">
                                {symbol}
                            </div>
                        """
                    ),
                    popup=label
                ).add_to(m)
            
        return m
    
    my_map = get_map(m, grouped_points)
    st_folium(my_map, width=700, height=500)

    # if st.button("Close Map", key="close_bem"):
    #     st.session_state.button_clicked = None
    #     st.rerun()

# @st.dialog("Straits of Hormuz Region (Past 3 Days Vessel Movements)", width='large')
def show_soh_dialog(vessel_positions_df):
    soh = SohPolygonRenderer(id=2)
    soh_coords = soh.get_polygon_coordinates()
    center_coords = soh.get_center_coordinates()
    soh_coords = [[v, k] for k, v in soh_coords]
    
    m = folium.Map(location=center_coords, zoom_start=7)  
    folium.Polygon(
        soh_coords,
        color="red",
        fill=True,
        fill_opacity=0.4,
        popup="Highlighted Region"
    ).add_to(m)

    grouped_points = group_vessel_positions_by_imo_helper(vessel_positions_df)
    
    def get_map(m, points_by_imo):
        for imo, points in points_by_imo.items():
            line = folium.PolyLine(
                locations=list(map(lambda p: p[:2], points)),
                color=points[0][-2],
                weight=2,
                opacity=0.0001
            ).add_to(m)

            PolyLineTextPath(
                line,
                " ➤   ",
                repeat=True,
                offset=10,
                attributes={
                    'fill': points[0][-2],
                    'font-weight': 'bold',
                    'font-size': '16',
                    'opacity': '0.7'
                }
            ).add_to(m)

            for lat, lon, label, symbol, color, opacity in points:
                folium.Marker(
                    [lat, lon],
                    icon=folium.DivIcon(
                        html=f"""
                            <div style="
                                font-size:28px;
                                color:{color};
                                opacity:{opacity};
                                text-align:center;
                                ">
                                {symbol}
                            </div>
                        """
                    ),
                    popup=label
                ).add_to(m)
            
        return m

    my_map = get_map(m, grouped_points)
    st_folium(my_map, width=700, height=500)

# @st.dialog("Straits of Malacca Region (Past 3 Days Vessel Movements)", width='large')
def show_som_dialog(vessel_positions_df):
    som = SomPolygonRenderer(id=1)
    som_coords = som.get_polygon_coordinates()
    center_coords = som.get_center_coordinates()
    som_coords = [[v, k] for k, v in som_coords]

    m = folium.Map(location=center_coords, zoom_start=7)
        
    folium.Polygon(
        som_coords,
        color="red",
        fill=True,
        fill_opacity=0.4,
        popup="Highlighted Region"
    ).add_to(m)

    grouped_points = group_vessel_positions_by_imo_helper(vessel_positions_df)

    def get_map(m, points_by_imo):
        for imo, points in points_by_imo.items():
            line = folium.PolyLine(
                locations=list(map(lambda p: p[:2], points)),
                color=points[0][-2],
                weight=2,
                opacity=0.0001
            ).add_to(m)

            PolyLineTextPath(
                line,
                " ➤   ",
                repeat=True,
                offset=10,
                attributes={
                    'fill': points[0][-2],
                    'font-weight': 'bold',
                    'font-size': '16',
                    'opacity': '0.7'
                }
            ).add_to(m)

            for lat, lon, label, symbol, color, opacity in points:
                folium.Marker(
                    [lat, lon],
                    icon=folium.DivIcon(
                        html=f"""
                            <div style="
                                font-size:28px;
                                color:{color};
                                opacity:{opacity};
                                text-align:center;
                                ">
                                {symbol}
                            </div>
                        """
                    ),
                    popup=label
                ).add_to(m)
            
        return m
    
    my_map = get_map(m, grouped_points)
    st_folium(my_map, width=700, height=500)


def create_custom_button_v2(image_base64, button_key, button_text, height=120, additional_styles=""):
    """
    Alternative approach using containers for better isolation
    """
    
    # Create a container for this specific button
    container = st.container()
    
    with container:
        st.markdown(f"""
        <style>
        div[data-testid="stVerticalBlock"] > div:has(button[key="{button_key}"]) .stButton > button,
        .button-container-{button_key} .stButton > button {{
            width: 100%;
            height: {height}px;
            background-image: url('data:image/png;base64,{image_base64}');
            background-size: cover;
            background-position: center;
            background-repeat: no-resources;
            border: none;
            border-radius: 8px;
            color: white;
            font-size: 14px;
            font-weight: bold;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.8);
            position: relative;
            overflow: hidden;
            {additional_styles}
        }}
        
        .button-container-{button_key} .stButton > button::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0,0,0,0.4);
            z-index: 1;
        }}
        
        .button-container-{button_key} .stButton > button:hover {{
            transform: scale(1.02);
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        }}
        
        .button-container-{button_key} .stButton > button span {{
            position: relative;
            z-index: 2;
        }}
        </style>
        
        <div class="button-container-{button_key}">
        """, unsafe_allow_html=True)
        
        # Create the button
        button_clicked = st.button(button_text, key=button_key, use_container_width=True)
        
        # st.markdown("</div>", unsafe_allow_html=True)
        
        return button_clicked



def show_results_page():

    st.title("📊 Vessels Search Results")
    
    # if st.button("← Back to Search", type="secondary"):
    #     st.session_state.current_page = 'input'
    #     st.rerun()
    
    st.subheader("🎯 Search Overview")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Vessels Searched", len(st.session_state.vessels))
    st.markdown("---")
    
    tracked_vessel_dataframe = st.session_state.db_manager.get_vessels_tracked(st.session_state.vessels)
    vessel_pos_dataframe_three_days = st.session_state.db_manager.get_past_three_days_vessel_positions(st.session_state.vessels)

    map_1, map_2, map_3 = st.columns(3)

    with map_1:
        show_som_dialog(vessel_pos_dataframe_three_days)
    with map_2:
        show_soh_dialog(vessel_pos_dataframe_three_days)
    with map_3:
        show_bem_dialog(vessel_pos_dataframe_three_days)


    def get_base64_image(image_path):
        try:
            with open(image_path, "rb") as img_file:
                return base64.b64encode(img_file.read()).decode()
        except FileNotFoundError:
            return None

    # Load your local images
    image1_base64 = get_base64_image("./frontend/assets/bem.png")
    image2_base64 = get_base64_image("./frontend/assets/soh.png")
    image3_base64 = get_base64_image("./frontend/assets/som.png")
    
    # if create_custom_button_v2(
    #     image1_base64, 
    #     "button1", 
    #     "View Vessels @ Bab El Mandeb Straits",
    #     height=120,
    #     additional_styles="border: 2px solid #ff6b6b;"
    # ):
    #     show_bem_dialog(vessel_pos_dataframe_three_days)

    # if create_custom_button_v2(
    #     image2_base64, 
    #     "button2", 
    #     "View Vessels @ Straits of Hormuz",
    #     height=120,
    #     additional_styles="border: 2px solid #ff6b6b;"
    # ):
    #     show_soh_dialog(vessel_pos_dataframe_three_days)

    # if create_custom_button_v2(
    #     image3_base64, 
    #     "button3", 
    #     "View Vessels @ Straits of Malacca",
    #     height=120,
    #     additional_styles="border: 2px solid #ff6b6b;"
    # ):
    #     show_som_dialog(vessel_pos_dataframe_three_days)

    st.markdown("---")

    st.dataframe(tracked_vessel_dataframe)

    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔄 New Search", type="primary", use_container_width=True):
            st.session_state.search_words = []
            st.session_state.search_results = {}
            st.session_state.current_page = 'input'
            st.rerun()
    
    with col2:
        if st.button("📥 Export Results", type="primary", use_container_width=True):
            st.success("Export functionality would be implemented here!")
    
    with col3:
        if st.button("📧 Share Results", type="primary", use_container_width=True):
            st.success("Share functionality would be implemented here!")

    




        # if clicked1 == "button1":
        #     st.success('Button 1 Clicked - Bab El Mandeb Straits')

        # button2_html = create_button_html(image2_base64, "button2", "Straits of Hormuz")
        # clicked2 = st.components.v1.html(button2_html, height=140)
        
        # button3_html = create_button_html(image3_base64, "button3", "Straits of Malacca")
        # clicked3 = st.components.v1.html(button3_html, height=140)

        # clicked = streamlit_js_eval(js_expressions="window.addEventListener('message', (e) => e.data);", key="listener")

        # print(clicked, "SAGEGREGGGEEGGE")
        # print(clicked1, "drhgvggvghhg767767676")
        # if clicked:
        #     print(clicked, 'jsisskjsd')

        # print(clicked, '21214324')
        # if clicked in ["button1", "button2", "button3"]:
        #     st.session_state.button_clicked = clicked


        # if 'button_clicked' not in st.session_state:
        #     st.session_state.button_clicked = None

        # if clicked1:
        #     print('BITCHBITCHBITCHBITCHBITCHBITCHBITCHYES11111')
        #     st.session_state.button_clicked = 'button1'
        #     # st.session_state.button_clicked = clicked1
        #     st.rerun()

        # if clicked2:
        #     print('BITCHBITCHBITCHBITCHBITCHBITCHBITCHYES222222')
        #     st.session_state.button_clicked = 'button2'
        #     # st.session_state.button_clicked = clicked2

        #     st.rerun()

        # if clicked3:
        #     print('BITCHBITCHBITCHBITCHBITCHBITCHBITCHYES3333333')
        #     st.session_state.button_clicked = 'button3'
        #     # st.session_state.button_clicked = clicked3
        #     st.rerun()

        # if st.session_state.button_clicked == 'button1':
        #     show_bem_dialog()
        # elif st.session_state.button_clicked == 'button2':
        #     show_soh_dialog()
        # elif st.session_state.button_clicked == 'button3':
        #     show_som_dialog()

        # print(st.session_state.button_clicked, 'BUTTTTTTTTTTTTTON CLICKEDD')
        
        
        # # Handle button clicks with dialogs
        # if st.session_state.button_clicked == 'button1':
        #     print('BITCHBITCHBITCHBITCHBITCHBITCHBITCH1')
        #     @st.dialog("Modern Pop Up Design")
        #     def show_bem():
        #         st.write("Here’s the folium map inside a popup dialog 🚢")
        #         m = get_map()
        #         st_folium(m, width=700, height=500)

        #         # Custom dismiss button (optional)
        #         if st.button("Close Map"):
        #             st.rerun()

        #     # def show_modern_popup():
        #     #     st.markdown("""
        #     #     ### Modern Pop Up Design
                
        #     #     Create sleek, contemporary popup windows with:
        #     #     - Clean minimalist layouts
        #     #     - Smooth animations
        #     #     - Modern typography
        #     #     - Interactive elements
        #     #     """)
        #     #     if image1_base64:
        #     #         st.image(f"data:image/png;base64,{image1_base64}", use_column_width=True)
        #     #     if st.button("Close", key="close_modern"):
        #     #         st.session_state.button_clicked = None
        #     #         st.rerun()
        #     show_bem()
        
        # elif st.session_state.button_clicked == 'button2':
        #     print('BITCHBITCHBITCHBITCHBITCHBITCHBITCH2')
        #     @st.dialog("Pop Up Window Display")
        #     def show_popup_window():
        #         st.markdown("""
        #         ### Pop Up Window Display
                
        #         Advanced popup functionality featuring:
        #         - Responsive design
        #         - Custom animations
        #         - Interactive content
        #         - User-friendly controls
        #         """)
        #         if image2_base64:
        #             st.image(f"data:image/png;base64,{image2_base64}", use_column_width=True)
        #         if st.button("Close", key="close_popup"):
        #             st.session_state.button_clicked = None
        #             st.rerun()
            
        #     show_popup_window()
        
        # elif st.session_state.button_clicked == 'button3':
        #     print('BITCHBITCHBITCHBITCHBITCHBITCHBITCH3')
        #     @st.dialog("Creative Popup Designs")
        #     def show_creative_popup():
        #         st.markdown("""
        #         ### Creative Popup Designs
                
        #         Innovative popup solutions with:
        #         - Unique visual effects
        #         - Custom styling options
        #         - Enhanced user experience
        #         - Modern aesthetics
        #         """)
        #         if image3_base64:
        #             st.image(f"data:image/png;base64,{image3_base64}", use_column_width=True)
        #         if st.button("Close", key="close_creative"):
        #             st.session_state.button_clicked = None
        #             st.rerun()
        #     show_creative_popup()


    # with main_col1:
    #     all_renderer = st.tabs(list(map(lambda renderer: repr(renderer), st.session_state.screen.polygon_renderer)))
    #     num_still_processing = len(st.session_state.screen.body) * len(st.session_state.screen.polygon_renderer)

    #     while num_still_processing > 0:
    #         if st.session_state.screen.report_renderer.has_result():
    #             section, poly_renderer = st.session_state.screen.report_renderer.get_result()
    #             with all_renderer[poly_renderer.id-1]:
    #                 st.subheader(f"{section.title}")
    #                 st.dataframe(section.render_content())
    #             num_still_processing = num_still_processing - 1


            
    # get_button()
        # def get_base64_image(image_path):
        #     try:
        #         with open(image_path, "rb") as img_file:
        #             return base64.b64encode(img_file.read()).decode()
        #     except FileNotFoundError:
        #         return None
        
        # # Load your local images (replace with your actual image paths)
        # image1_base64 = get_base64_image("./frontend/assets/bem.png")  # Replace with actual path
        # image2_base64 = get_base64_image("./frontend/assets/soh.png")  # Replace with actual path
        # image3_base64 = get_base64_image("./frontend/assets/som.png")  # Replace with actual path

        # image1_url = f"data:image/png;base64,{image1_base64}"
        # image2_url = f"data:image/png;base64,{image2_base64}"
        # image3_url = f"data:image/png;base64,{image3_base64}"
    
        # st.markdown("""
        # <style>
        # .stButton > button {
        #     width: 100%;
        #     height: 120px;
        #     background-size: cover;
        #     background-position: center;
        #     background-repeat: no-repeat;
        #     border: none;
        #     border-radius: 8px;
        #     color: white;
        #     font-size: 16px;
        #     font-weight: bold;
        #     text-shadow: 2px 2px 4px rgba(0,0,0,0.8);
        #     cursor: pointer;
        #     transition: transform 0.2s ease, box-shadow 0.2s ease;
        #     margin-bottom: 10px;
        #     display: flex;
        #     align-items: center;
        #     justify-content: center;
        #     text-align: center;
        # }
        
        # .stButton > button:hover {
        #     transform: scale(1.02);
        #     box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        # }
        
        # .stButton > button:focus {
        #     outline: none;
        #     box-shadow: 0 0 0 2px rgba(255,255,255,0.5);
        # }
        
        # /* Individual button backgrounds */
        # div[data-testid="stVerticalBlock"] > div:nth-child(4) .stButton > button {{
        #     background-image: url('./frontend/assets/bem.png');
        # }}
        # div[data-testid="stVerticalBlock"] > div:nth-child(4) .stButton > button {{
        #     background-image: url('./frontend/assets/soh.png');
        # }}    
        # div[data-testid="stVerticalBlock"] > div:nth-child(4) .stButton > button {{
        #     background-image: url('./frontend/assets/som.png');
        # }}
                    
        # </style>
        # """, unsafe_allow_html=True)































