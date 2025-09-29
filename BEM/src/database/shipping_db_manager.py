import threading
from psycopg2.pool import ThreadedConnectionPool
from .vessels_table import VesselsTable
from .hra_user_table import HraUserTable
from .user_whitelist_table import UserWhitelistTable
from .hra_alerts_table import HraAlertsTable
from datetime import datetime

import pandas as pd
import numpy as np

class ShippingDBManager:
    def __init__(self):
        self.pool = ThreadedConnectionPool(
            minconn=1,     
            maxconn=30,
            host='ats-ana-uks-prt-sql.postgres.database.azure.com',
            database='aramco',
            user='user_shipping',
            password='fj2329^%dFF'
        )
        self.lock = threading.Lock()
        self.cursor = self._get_connection().cursor()
        self.vessels = VesselsTable(self._get_connection())
        self.user = HraUserTable(self._get_connection())
        self.user_whitelist = UserWhitelistTable(self._get_connection())
        self.hra_alerts = HraAlertsTable(self._get_connection())


    def get_past_three_days_vessel_positions(self, vessels_list_data):
        vessels_imo = tuple(map(lambda mapping: mapping['imo'].item() if type(mapping['imo']) is np.int64 else mapping['imo'], vessels_list_data))

        if len(vessels_imo) == 1:
            vessels_imo = f"({vessels_imo[0]})"

        query = f'''
        select 
            vx_v.imo as "IMO",
            vx_v.name as "Vessel Name",
            vx_pos.date as "Date",
            vx_pos.lat as "Latitude",
            vx_pos.lon as "Longitude"
        from 
            vx_vessel_position vx_pos 
        join 
            vx_vessel vx_v 
        on 
            vx_pos.vessel_id = left(vx_v.vessel_id, 16)
        where
            vx_pos.date >= '{(datetime.today() - pd.Timedelta(days=3)).strftime("%Y-%m-%d 00:00")}'
        and
            vx_v.imo in {vessels_imo}
        order by
            vx_pos.date asc
        '''

        columns = ["IMO", "Vessel Name", "Date", "Latitude", "Longitude"]

        try:
            self.cursor.execute(query)
            vessel_positions = self.cursor.fetchall()
            return pd.DataFrame(vessel_positions, columns=columns)
        except Exception as e:
            print(f"Error getting vessel positions: {e}")
            return None

    def get_vessels_tracked(self, vessels_list_data):
        vessels_imo = tuple(map(lambda mapping: mapping['imo'].item() if type(mapping['imo']) is np.int64 else mapping['imo'], vessels_list_data))
        
        if len(vessels_imo) == 1:
            vessels_imo = f"({vessels_imo[0]})"

        columns = ['IMO', 'Vessel Name', 'Vessel Type', 'Latest Seen Date', 'Latest Seen Zone']

        query = f'''
        with inter as (
            select
                imo as "IMO",
                name as "Vessel Name",
                vessel_type as "Vessel Type",
                date as "Latest Seen Date",
                case when
                    inside_zone = 'FALSE' then 'None'
                else inside_zone 
                end as "Latest Seen Zone",
                rank() over(partition by imo order by date desc) as rnk
            from 
                vx_vessel_position vx_pos 
            join 
                vx_vessel vx_v 
            on 
                vx_pos.vessel_id = left(vx_v.vessel_id, 16)
            where
                vx_v.imo in {vessels_imo}
        )
        select "IMO", "Vessel Name", "Vessel Type", "Latest Seen Date", "Latest Seen Zone"
        from inter
        where rnk=1
        '''

        try:
            self.cursor.execute(query)
            users_watchlist = self.cursor.fetchall()
            return pd.DataFrame(users_watchlist, columns=columns)
        except Exception as e:
            print(f"Error getting users: {e}")
            return None
        
    def get_user_watchlist(self, email):
        query = f'''
        SELECT
            DISTINCT
            name,
            vx_v.imo as imo,
            vessel_type,
            build_year,
            vessel_id,
            last_movement,
            alert_sent_date,
            CASE
                WHEN ((alert_seen_date is null AND alert_sent_date is not null) or (alert_sent_date > alert_seen_date)) THEN true
                ELSE false
                END as "flag_for_alert"
        FROM vx_vessel vx_v
        JOIN hra_alert hra_a
        ON vx_v.imo = hra_a.imo
        WHERE
            is_still_tracking is true
        AND
            email='{email}'
        '''
        # query = f'''
        # select name, imo, vessel_type, build_year, vessel_id
        # from vx_vessel
        # where
        #     imo in (select distinct(imo)
        #             from hra_alert 
        #             where is_still_tracking is true
        #             and email='{email}')
        # '''
        columns = ['name', 'imo', 'vessel_type', 'build_year', 'vessel_id', 'last_movement', 'alert_sent_date', 'flag_for_alert']

        try:
            self.cursor.execute(query)
            users_watchlist = self.cursor.fetchall()
            return pd.DataFrame(users_watchlist, columns=columns)
        except Exception as e:
            print(f"Error getting users: {e}")
            return None

    def _get_connection(self):
        with self.lock:
            try:
                return self.pool.getconn()
            except Exception as e:
                print(f"Error getting connection: {e}")
                return None

    def put_connection(self, conn):
        with self.lock:
            self.pool.putconn(conn)
        