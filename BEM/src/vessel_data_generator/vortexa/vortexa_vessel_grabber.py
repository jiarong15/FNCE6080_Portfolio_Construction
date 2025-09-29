import requests
from datetime import datetime, timedelta
import pandas as pd
import vortexasdk as vortexa
import pytz

from typing import Protocol
from abc import abstractmethod

from utils.yaml_reader import vortexa_api_key, signal_api_key
from src.vessel_data_generator.vessel_data_grabber import VesselDataGrabber 


class VortexaVesselGrabber(VesselDataGrabber):
    VESSEL_CLASS = [
        "oil_lr1",
        "oil_mr1",
        "oil_mr2",
        "oil_lr2",
        "oil_lr3",
        "oil_vlcc"
    ]
    VORTEXA_OBJ = vortexa #.set_api_key(vortexa_api_key())

    class InputHandler(Protocol):
        
        @abstractmethod
        def handle(self, values):
            pass

    class VesselNameHandler:
        def handle(self, values):
            return f"Handled string: {values.upper()}"

    class VesselIMOHandler:

        def _vessel_imo_details(self, url):
            PARAMS = {
                'timestamp ': datetime.now().isoformat()
            }
            resp = requests.get(url=url, params=PARAMS)
            data = resp.json()
            return data
        
        def handle(self, values):
            IMO_GRAB_URL = f'https://api.vortexa.com/v6/signals/vessel-summary?apikey={vortexa_api_key()}'
            ids = ''.join(f'&ids={num}' for num in values)
            final_url = IMO_GRAB_URL + ids
            vessel_data = self._vessel_imo_details(final_url)
            return vessel_data

    def __init__(self):
        self._user_input_handlers = {
            str: self.VesselNameHandler(),
            int: self.VesselIMOHandler()
        }
        super(VortexaVesselGrabber, self).__init__()

    def _signal_to_event(self, vessel_df, data):
        grouped = data.groupby("vessel_id")
        all_events = []

        for name, group in grouped:
            all_events.extend(self._generate_entry_exit_events(group))

        # Create a DataFrame with the events
        events_df = pd.DataFrame(all_events)

        if events_df.empty:
            print("No entry/exit events found")
            return pd.DataFrame()
        
        final_df = events_df.merge(
            vessel_df, left_on="vessel_id", right_on="id_16", how="left"
        )

        final_df = final_df.drop(columns=["id_16", "id"])

        final_df["entry_timestamp"] = pd.to_datetime(final_df["entry_timestamp"])
        final_df["exit_timestamp"] = pd.to_datetime(final_df["exit_timestamp"])

        # Get the timezone from the entry_timestamp if available, otherwise default to UTC
        timezone = final_df["entry_timestamp"].dt.tz

        # Make current time timezone-aware
        now = datetime.now(pytz.UTC).astimezone(timezone)

        # Calculate time spent for vessels with an exit timestamp
        final_df["time_spent"] = final_df.apply(
            lambda row: (
                (row["exit_timestamp"] - row["entry_timestamp"]).total_seconds() / 3600
                if pd.notnull(row["exit_timestamp"])
                else (now - row["entry_timestamp"]).total_seconds() / 3600
            ),
            axis=1,
        )
        # final_df = final_df[~final_df["exit_timestamp"].isnull()]
        return final_df
    
    def _generate_entry_exit_events(self, group):
        events = []
        current_state = None
        entry_time = None

        for index, row in group.iterrows():
            if row["in_polygon"] != current_state:
                if row["in_polygon"]:  # Entry event
                    entry_time = row["timestamp"]
                else:  # Exit event
                    if entry_time is not None:
                        events.append(
                            {
                                "vessel_id": row["vessel_id"],
                                "entry_timestamp": entry_time,
                                "exit_timestamp": row["timestamp"],
                                "lat": row["lat"],
                                "lon": row["lon"],
                            }
                        )
                    entry_time = None
                current_state = row["in_polygon"]

        # Handle the case where the last state is 'in_polygon'
        if current_state and entry_time is not None:
            events.append(
                {
                    "vessel_id": group.iloc[-1]["vessel_id"],
                    "entry_timestamp": entry_time,
                    "exit_timestamp": None,
                    "lat": group.iloc[-1]["lat"],
                    "lon": group.iloc[-1]["lon"],
                }
            )

        return events
    
    def _vessel_data_clean_up(self, data, polygon_renderer):
        final_data = pd.concat([pd.DataFrame(i) for i in data]).reset_index(drop=True)
        final_data["in_polygon"] = final_data.apply(
            lambda row: polygon_renderer.is_in_region(row["lon"], row["lat"]),
            axis=1
        )

        # Get the current date
        now = datetime.now()

        # Calculate the start of the current month
        start_of_current_month = datetime(now.year, now.month, 1)

        # Calculate the start of the previous month
        if now.month == 1:
            start_of_previous_month = datetime(now.year - 1, 12, 1)
        else:
            start_of_previous_month = datetime(now.year, now.month - 1, 1)

        # Calculate the start of the next month to get the end of the current month
        if now.month == 12:
            start_of_next_month = datetime(now.year + 1, 1, 1)
        else:
            start_of_next_month = datetime(now.year, now.month + 1, 1)

        start_of_current_month_str = start_of_current_month.strftime("%Y-%m-%d")
        start_of_previous_month_str = start_of_previous_month.strftime("%Y-%m-%d")
        start_of_next_month_str = start_of_next_month.strftime("%Y-%m-%d")

        # Filter the data for the current month and the previous month
        filtered_data = final_data[(final_data["timestamp"] >= start_of_previous_month_str)]
        return filtered_data

    def _get_initial_vessel_ids(self, vessel_data):
        end_timestamp = datetime.now()
        start_timestamp = (end_timestamp - timedelta(days=7))

        vessel_df = VortexaVesselGrabber.VORTEXA_OBJ.Vessels().search(term=vessel_data, exact_term_match=False, vessel_classes=VortexaVesselGrabber.VESSEL_CLASS).to_df()
        vessel_df["id_16"] = vessel_df["id"].apply(lambda x: x[:16])
        vessel_df = vessel_df[vessel_df['imo'] != '']
        vessel_list_id = list(map(lambda ves_list: str(int(ves_list)), vessel_df['imo'].values.tolist()))

        data = []
        for i in range(0, len(vessel_list_id), 100):
            vessel_positions = self._extract_all_vessel_positions(vessel_list_id[i:i+100], start_timestamp, end_timestamp, '15m')
            data.append(vessel_positions['data'])
        return vessel_df, data

    def _extract_all_vessel_positions(self, vessel_imo_list, start_timestamp, end_timestamp, interval):
        URL = "https://api.vortexa.com/v6/signals/vessel-positions"
        start_timestamp_iso = start_timestamp.isoformat()
        end_timestamp_iso = end_timestamp.isoformat()

        PARAMS = {
            'apikey': signal_api_key(),
            'time_min': start_timestamp_iso,
            'time_max': end_timestamp_iso,
            'interval': interval,
            'vessel_id': vessel_imo_list
        }
        resp = requests.get(url=URL, params=PARAMS)
        data = resp.json()
        return data
    
    def _get_initial_vessel_for_current_spot_and_clean_up(self, polygon_renderer, vessel_data):
        end_timestamp = datetime.now() + timedelta(days=1)
        start_timestamp = end_timestamp - timedelta(days=2)

        vessel_df = VortexaVesselGrabber.VORTEXA_OBJ.Vessels().search(term=vessel_data, exact_term_match=False, vessel_classes=VortexaVesselGrabber.VESSEL_CLASS).to_df()
        vessel_df["id_16"] = vessel_df["id"].apply(lambda x: x[:16])
        vessel_df = vessel_df[vessel_df['imo'] != '']
        vessel_list_id = list(map(lambda ves_list: str(int(ves_list)), vessel_df['imo'].values.tolist()))

        data = []
        for i in range(0, len(vessel_list_id), 100):
            vessel_positions = self._extract_all_vessel_positions(vessel_list_id[i:i+100], start_timestamp, end_timestamp, '15m')
            data.append(vessel_positions['data'])
        
        final_data = pd.concat([pd.DataFrame(i) for i in data]).reset_index(drop=True)
        final_data["in_polygon"] = final_data.apply(
            lambda row: polygon_renderer.is_in_region(row["lon"], row["lat"]),
            axis=1
        )
        return vessel_df, final_data
    
    def grab_all_vessel_data_by_names(self, polygon_renderer, vessel_data):
        if len(vessel_data) == 0:
            print("No vessel data provided")
            return pd.DataFrame()
        
        vessel_df, data = self._get_initial_vessel_ids(vessel_data)
        vessel_data_cleaned = self._vessel_data_clean_up(data, polygon_renderer)
        df = self._signal_to_event(vessel_df, vessel_data_cleaned)
        print("WADDDUP BUTTERCUP")
        return df
    
    def grab_entry_vessel_data_by_names(self, polygon_renderer, vessel_data):
        if len(vessel_data) == 0:
            print("No vessel data provided")
            return pd.DataFrame()
        
        # REFERENCE_DATETIME = datetime.now() - timedelta(minutes=15)
        vessel_df, data = self._get_initial_vessel_for_current_spot_and_clean_up(polygon_renderer, vessel_data)
        just_before_entering_zone = data[(data['in_polygon']==False) &
                                         (data['timestamp'] <= f'{(datetime.now())}') &
                                         (data['timestamp'] >= f'{(datetime.now() - timedelta(minutes=60))}')
                                        ]

        right_after_entering_zone = data[(data['timestamp'] >= f'{(datetime.now())}') &
                                         (data['timestamp'] <= f'{(datetime.now() + timedelta(minutes=60))}') &
                                         (data['in_polygon']==True)
                                        ]
        
        just_before_entering_zone_df = just_before_entering_zone.merge(vessel_df, left_on="vessel_id", right_on="id_16", how="left")
        just_before_entering_zone_df = just_before_entering_zone_df.dropna(subset=['id_16']).drop(columns=["id_16", "id"]).drop_duplicates(subset='imo')

        right_after_entering_zone_df = right_after_entering_zone.merge(vessel_df, left_on="vessel_id", right_on="id_16", how="left")
        right_after_entering_zone_df = right_after_entering_zone_df.dropna(subset=['id_16']).drop(columns=["id_16", "id"]).drop_duplicates(subset='imo')
        
        final_df = just_before_entering_zone_df.merge(right_after_entering_zone_df, on='imo', how='inner', suffixes=('_left', '_right'))
        final_df = final_df[['imo', 'name_left', 'vessel_class_left', 'lat_left', 'lon_left', 'timestamp_right']]
        final_df = final_df.rename(columns=
                                   {"name_left": "Vessel Name",
                                    "imo": "IMO",
                                    "lat_left": "Latitude",
                                    "lon_left": "Longitude",
                                    "timestamp_right": "Entry Date",
                                    "vessel_class_left": "Vessel Type"
                                    })
        print("WADDDUP BUTTERCUP 2")    
        return final_df
    
    def grab_exit_vessel_data_by_names(self, polygon_renderer, vessel_data):
        if len(vessel_data) == 0:
            print("No vessel data provided")
            return pd.DataFrame()
        
        vessel_df, data = self._get_initial_vessel_for_current_spot_and_clean_up(polygon_renderer, vessel_data)
        just_before_exiting_zone = data[(data['in_polygon']==True) &
                                         (data['timestamp'] <= f'{(datetime.now())}') &
                                         (data['timestamp'] >= f'{(datetime.now() - timedelta(minutes=60))}')
                                        ]

        right_after_exiting_zone = data[(data['timestamp'] >= f'{(datetime.now())}') &
                                         (data['timestamp'] <= f'{(datetime.now() + timedelta(minutes=60))}') &
                                         (data['in_polygon']==False)
                                        ]

        just_before_exiting_zone_df = just_before_exiting_zone.merge(vessel_df, left_on="vessel_id", right_on="id_16", how="left")
        just_before_exiting_zone_df = just_before_exiting_zone_df.dropna(subset=['id_16']).drop(columns=["id_16", "id"]).drop_duplicates(subset='imo')

        right_after_exiting_zone_df = right_after_exiting_zone.merge(vessel_df, left_on="vessel_id", right_on="id_16", how="left")
        right_after_exiting_zone_df = right_after_exiting_zone_df.dropna(subset=['id_16']).drop(columns=["id_16", "id"]).drop_duplicates(subset='imo')
        
        final_df = just_before_exiting_zone_df.merge(right_after_exiting_zone_df, on='imo', how='inner', suffixes=('_left', '_right'))
        final_df = final_df[['imo', 'name_left', 'vessel_class_left', 'lat_left', 'lon_left', 'timestamp_right']]
        final_df = final_df.rename(columns=
                                   {"name_left": "Vessel Name",
                                    "imo": "IMO",
                                    "lat_left": "Latitude",
                                    "lon_left": "Longitude",
                                    "timestamp_right": "Entry Date",
                                    "vessel_class_left": "Vessel Type"
                                    })
        print("WADDDUP BUTTERCUP 3") 
        return final_df


# v = VortexaVesselGrabber()
# from src.polygon_renderer.bem_polygon_renderer import BemPolygonRenderer
# polygon_renderer = BemPolygonRenderer()
# vessel_df = v.grab_entry_vessel_data_by_names(polygon_renderer, ['a'])
# # print(vessel_df.head())

# print(v.grab_current_spot_of_vessel([9291248]))


