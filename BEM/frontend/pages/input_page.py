import streamlit as st
# import pandas as pd
# from frontend.shared.utils import add_word_to_list, remove_word
import re

def show_input_page():
    # map1, map2, map3 = st.columns(3)
    # vessel_pos_dataframe_three_days = st.session_state.db_manager.get_past_three_days_vessel_positions(st.session_state.vessels)
    
    # with map1:
    #     show_soh_dialog(vessel_pos_dataframe_three_days)

    # st.title("🔍 Vessel Zone Tracking Application (BEM)")
    # st.markdown("Add vessel names to search for!")
    
    # # Button to open modal
    # col1, col2, col3 = st.columns([1, 2, 1])
    # with col2:
    #     if st.button("➕ Add Vessels", type="primary", use_container_width=True):
    #         st.session_state.show_modal = True
    
    # # Modal simulation using expander
    # if st.session_state.show_modal:
    #     with st.container():
    #         st.markdown("---")
    #         st.subheader("📝 Add Vessel Name")

    #         word_input = st.text_input(
    #             "Enter a vessel:",
    #             key="word_input",
    #             placeholder="Type a word and press Enter..."
    #         )
            
    #         col1, col2, col3 = st.columns([1, 1, 1])
    #         with col1:
    #             if st.button("Add Vessel..") and word_input:
    #                 add_word_to_list(word_input)
    #                 st.rerun()
            
    #         with col2:
    #             if st.button("Close Section"):
    #                 st.session_state.show_modal = False
    #                 st.rerun()
            
    #         st.markdown("---")

    ###############################################################################################
    # if 'vessels' not in st.session_state:
    #     user_email = st.session_state.user.iloc[0]['email']
    #     st.session_state.vessels = st.session_state.db_manager.get_user_watchlist(user_email).to_dict(orient="records")

    # Custom CSS for styling
    st.markdown("""
    <style>
        .vessel-card {
            background-color: #f8f9fa;
            border: 1px solid #e9ecef;
            border-radius: 8px;
            padding: 15px;
            margin: 10px 0;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }
        
        .vessel-info {
            display: flex;
            align-items: center;
            flex-grow: 1;
        }
        
        .status-indicator {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            margin-right: 15px;
        }
        
        .status-active {
            background-color: #28a745;
        }
        
        .status-inactive {
            background-color: #6c757d;
        }
        
        .vessel-name {
            font-weight: 600;
            font-size: 22px;
            margin-bottom: 2px;
        }
        
        .vessel-type {
            font-size: 14px;
            color: #6c757d;
        }
        
        .vessel-imo {
            font-weight: 600;
            font-size: 16px;
            font-style: italic;
        }
        
        .vessel-build-year {
            font-size: 14px;
            color: #6c757d;
            margin-bottom: 2px;
            font-style: italic;
        }
        
        .vessel-actions {
            display: flex;
            gap: 10px;
            align-items: center;
        }
        
        .action-button {
            background: none;
            border: none;
            cursor: pointer;
            padding: 5px;
            border-radius: 4px;
        }
        
        .action-button:hover {
            background-color: #e9ecef;
        }
        
        .add-vessel-section {
            background-color: #ffffff;
            border: 1px solid #dee2e6;
            border-radius: 8px;
            padding: 20px;
            margin: 20px 0;
        }

        .vessel-card-two {
            background-color: #ffcccc;
            border: #ffcccc;
            border-radius: 8px;
            padding: 15px;
            margin: 10px 0;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }
    </style>
    """, unsafe_allow_html=True)

    with st.sidebar:

        # Title
        st.title("🚢 High Risk Area Vessels Tracking")

        all_vessels_metadata = st.session_state.db_manager.vessels.get_vessel_by_column_as_list(['name', 'imo', 'vessel_type'])
        
        new_vessel_name = st.selectbox(
            "Choose a vessel (type to search):",
            options=[""] + list(map(lambda x: f"{x[0]} (IMO: {x[1]}, Vessel Type: {x[2]})", all_vessels_metadata)),
            index=0,
            help="Start typing to filter options"
        )

        if new_vessel_name:
            st.success(f"You selected: {new_vessel_name} -> Click `Add Vessel` to confirm")
            
        with st.container():
            if st.button("Add Vessel", type="primary", use_container_width=True):
                if new_vessel_name:
                    new_vessel_name = new_vessel_name.strip()
                    match = re.search(r'IMO:\s*(\d+)', new_vessel_name)
                    imo_number = int(match.group(1))
                    vessel_details = st.session_state.db_manager.vessels.get_specific_vessel(imo_number)
                    # Add new vessel with default values
                    new_vessel = {
                        'name': vessel_details.iloc[0]['name'],
                        'imo': vessel_details.iloc[0]['imo'],
                        'vessel_type': vessel_details.iloc[0]['vessel_type'],
                        'build_year': vessel_details.iloc[0]['build_year'],
                        'vessel_id': vessel_details.iloc[0]['vessel_id'],
                        'flag_for_alert': False,
                    }
                    st.session_state.vessels = [new_vessel] + st.session_state.vessels
                    st.success(f"Vessel '{new_vessel_name}' added successfully!")
                    st.rerun()
                else:
                    st.error("Please enter a vessel name")
            
            st.markdown('</div>', unsafe_allow_html=True)

        # Current Vessels List
        st.subheader("Current Vessels List:")

        if st.session_state.vessels:
            for i, vessel in enumerate(st.session_state.vessels):
                if vessel['flag_for_alert'] is False:
                    vessel_card_html = f"""
                    <div class="vessel-card">
                        <div class="vessel-info">
                            <div>
                                <div class="vessel-name">{vessel['name']}</div>
                                <div class="vessel-type">{vessel['vessel_type']}</div>
                            </div>
                        </div>
                        <div style="text-align: right; margin-right: 20px;">
                            <div class="vessel-imo">IMO {vessel['imo']}</div>
                            <div class="vessel-build-year">Build Year {vessel['build_year']}</div>
                        </div>
                    </div>
                    """
                else:
                    if vessel['last_movement'] == 'Inside':
                        status = f'Entered Stipulated HRA on {vessel["alert_sent_date"].strftime("%Y-%m-%d")}'
                    else:
                        status = f'Exited HRA on {vessel["alert_sent_date"].strftime("%Y-%m-%d")}'
                    st.session_state.db_manager.hra_alerts.update_alert_seen(st.session_state.user.iloc[0]['email'], vessel['imo'])

                    vessel_card_html = f"""
                    <div class="vessel-card-two">
                        <div class="vessel-info">
                            <div>
                                <div class="vessel-name">
                                    <b>{vessel['name']}</b>
                                    <span style="color: #555; font-weight: normal; font-size: 20px; margin-left: 8px; opacity: 0.6;">
                                        {status}
                                    </span>
                                </div>
                                <div class="vessel-type">{vessel['vessel_type']}</div>
                            </div>
                        </div>
                        <div style="text-align: right; margin-right: 20px;">
                            <div class="vessel-imo">IMO {vessel['imo']}</div>
                            <div class="vessel-build-year">Build Year {vessel['build_year']}</div>
                        </div>
                    </div>
                    """

                col1, col2 = st.columns([10, 1])
                with col1:
                    st.markdown(vessel_card_html, unsafe_allow_html=True)
                with col2:
                    if st.button("❌", key=f"delete_{i}", help="Delete vessel"):
                        vessel_imo = st.session_state.vessels[i]['imo']
                        st.session_state.db_manager.hra_alerts.delete_alerts_by_imo(st.session_state.user.iloc[0]['email'], vessel_imo)
                        st.session_state.vessels.pop(i)
                        st.rerun()

            tracked_vessel_dataframe = st.session_state.db_manager.get_vessels_tracked(st.session_state.vessels)
            st.session_state.db_manager.hra_alerts.bulk_add_or_update_alerts(st.session_state.user, tracked_vessel_dataframe)
            # Search All Vessels Button
            # st.markdown("<br>", unsafe_allow_html=True)
            # if st.button("🔍 Search All Vessels", type="primary", use_container_width=True):
                # tracked_vessel_dataframe = st.session_state.db_manager.get_vessels_tracked(st.session_state.vessels)
                # st.session_state.db_manager.hra_alerts.bulk_add_or_update_alerts(st.session_state.user, tracked_vessel_dataframe)
                # st.session_state.current_page = 'results'
                # st.rerun()
        else:
            st.info("No vessels added yet. Add your first vessel above!")


    # Optional: Display vessels in a more interactive way with expanders
    # with st.expander("Advanced Vessel Management", expanded=False):
    #     if st.session_state.vessels:
    #         df = pd.DataFrame(st.session_state.vessels)
    #         edited_df = st.data_editor(
    #             df,
    #             use_container_width=True,
    #             hide_index=True,
    #             column_config={
    #                 "status": st.column_config.SelectboxColumn(
    #                     "Status",
    #                     options=["Active", "Inactive"],
    #                     required=True,
    #                 ),
    #                 "plan": st.column_config.SelectboxColumn(
    #                     "Plan",
    #                     options=["Standard", "Premium+"],
    #                     required=True,
    #                 ),
    #                 "price": st.column_config.TextColumn(
    #                     "Price",
    #                     help="Enter price with currency symbol",
    #                     max_chars=10,
    #                 ),
    #             }
    #         )
            
    #         if st.button("Update Vessels", key="update_vessels"):
    #             st.session_state.vessels = edited_df.to_dict('records')
    #             st.success("Vessels updated successfully!")
        


# vessel_card_html = f"""
#             <div class="vessel-card">
#                 <div class="vessel-info">
#                     <div class="status-indicator {status_class}"></div>
#                     <div>
#                         <div class="vessel-name">{vessel['name']}</div>
#                         <div class="vessel-plan">{vessel['vessel_type']}</div>
#                     </div>
#                 </div>
#                 <div style="text-align: right; margin-right: 20px;">
#                     <div class="vessel-price">{vessel['imo']}</div>
#                     <div class="vessel-period">{vessel['build_year']}</div>
#                 </div>
#                 <div class="vessel-actions">
#                     <span>ℹ️</span>
#                     <span>🔗</span>
#                     <span>⚙️</span>
#                     <span>⬇️</span>
#                 </div>
#             </div>
#             """


    # if st.session_state.search_words:
    #     st.subheader("Current Vessels List:")
        
    #     for i, word in enumerate(st.session_state.search_words):
    #         col1, col2 = st.columns([4, 1])
    #         with col1:
    #             st.write(f"• {word}")
    #         with col2:
    #             if st.button("❌", key=f"remove_{i}", help=f"Remove '{word}'"):
    #                 remove_word(word)
    #                 st.rerun()
        
    #     st.markdown("---")
        
    #     # Confirm search button
    #     col1, col2, col3 = st.columns([1, 2, 1])
    #     with col2:
    #         if st.button("🚀 Search All Vessels", type="primary", use_container_width=True):
    #             if st.session_state.search_words:
    #                 with st.spinner("Searching..."):                        
    #                     for section in st.session_state.screen.body:
    #                         for poly_renderer in st.session_state.screen.polygon_renderer:
    #                             section.set_query_vessel_list(st.session_state.search_words)
    #                             success = st.session_state.screen.queue.publish(section, poly_renderer)
    #                             if success:
    #                                 print(f"Section {section.id} sent for processing")
    #                             else:
    #                                 print(f"Failed to send section {section.id} for processing")

    #                 st.session_state.current_page = 'results'
    #                 st.rerun()
    # else:
    #     st.info("No vessels added yet. Click 'Add Vessels' to get started!")

    # vessels = [
    #     {"name": "GAS NOBLE", "imo": 9697492, "vessel_type": "lpg_coasters", "build_year": 2014},
    #     {"name": "AB VICTORY", "imo": 9287871, "vessel_type": "oil_coastal", "build_year": 2003},
    #     {"name": "ABC TRADER", "imo": 9340922, "vessel_type": "oil_intermediate", "build_year": 2007}
    # ]

    # # Inject CSS for card + modal
    # st.markdown("""
    #     <style>
    #         .vessel-card {
    #             background-color: #ffcccc;  /* Light red */
    #             border: 2px solid red;
    #             border-radius: 10px;
    #             padding: 15px;
    #             margin-bottom: 10px;
    #             cursor: pointer;  /* Show hand cursor */
    #         }
    #         .modal {
    #             position: fixed;
    #             top: 0; left: 0;
    #             width: 100%; height: 100%;
    #             background-color: rgba(0,0,0,0.5);  /* Dark overlay */
    #             display: flex;
    #             align-items: center;
    #             justify-content: center;
    #             z-index: 9999;
    #         }
    #         .modal-content {
    #             background-color: white;
    #             padding: 20px;
    #             border-radius: 10px;
    #             max-width: 500px;
    #             text-align: center;
    #         }
    #     </style>
    # """, unsafe_allow_html=True)

    # # Track clicked vessel
    # if "selected_vessel" not in st.session_state:
    #     st.session_state.selected_vessel = None

    # # Display vessel cards
    # for vessel in vessels:
    #     vessel_card_html = f"""
    #     <div class="vessel-card" onclick="window.location.href='?vessel={vessel['imo']}'">
    #         <div style="display:flex; justify-content:space-between;">
    #             <div>
    #                 <div class="vessel-name">
    #                     <b>{vessel['name']}</b>
    #                     <span style="color: #555; font-weight: normal; font-size: 20px; margin-left: 8px; opacity: 0.6;">
    #                         (Exited)
    #                     </span>
    #                 </div>
    #                 <div class="vessel-type">{vessel['vessel_type']}</div>
    #             </div>
    #             <div style="text-align:right;">
    #                 <div class="vessel-imo">IMO {vessel['imo']}</div>
    #                 <div class="vessel-build-year">Build Year {vessel['build_year']}</div>
    #             </div>
    #         </div>
    #     </div>
    #     """
    #     st.markdown(vessel_card_html, unsafe_allow_html=True)

    # # --- Modal Logic ---
    # # Capture query param (which card was clicked)
    # query_params = st.query_params()
    # if "vessel" in query_params:
    #     imo_clicked = int(query_params["vessel"][0])
    #     vessel = next(v for v in vessels if v["imo"] == imo_clicked)

    #     modal_html = f"""
    #     <div class="modal">
    #         <div class="modal-content">
    #             <h2>{vessel['name']}</h2>
    #             <p><b>IMO:</b> {vessel['imo']}</p>
    #             <p><b>Type:</b> {vessel['vessel_type']}</p>
    #             <p><b>Build Year:</b> {vessel['build_year']}</p>
    #             <a href="/">❌ Close</a>
    #         </div>
    #     </div>
    #     """
    #     st.markdown(modal_html, unsafe_allow_html=True)
