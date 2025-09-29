class HraAlertsTable:
    def __init__(self, connection):
        self.connection = connection
        self.cursor = connection.cursor()
        self.columns = ['Email', 'IMO', 'Region', 'Last Movement', 'Tracking Start Date', 'Alert Seen Date', 'Is Still Tracking']

    def delete_alerts_by_imo(self, email, imo):
        query = f'''
        UPDATE hra_alert
        SET is_still_tracking = false
        WHERE
            imo = {imo}
        AND
            email = '{email}'
        '''
        try:
            self.cursor.execute(query)
            self.connection.commit()
        except Exception as e:
            print(f"Error on delete by imo: {e}")
            return None

    def bulk_add_or_update_alerts(self, user_df, vessels_tracked_df):
        user_email = user_df.iloc[0]['email']
        tracking_start_date = 'NOW()'
        sb = ''

        all_regions = ['BAB EL MANDAB', 'MALACA', 'HORMUZ']
        for _, row in vessels_tracked_df.iterrows():
            imo = row.get('IMO', '')
            zone = row.get('Currently In Zone', 'None')
            if zone != 'None':
                region = zone
                last_movement = 'Inside'
                is_still_tracking = 'True'
                sb = sb + f"('{user_email}', {imo}, '{region}', '{last_movement}', {tracking_start_date}, NULL, {is_still_tracking}, NULL),"
            else:
                last_movement = 'Outside'
                is_still_tracking = 'True'
                for region in all_regions:
                    sb = sb + f"('{user_email}', {imo}, '{region}', '{last_movement}', {tracking_start_date}, NULL, {is_still_tracking}, NULL),"
        
        query = f'''
        INSERT INTO hra_alert (email, imo, region, last_movement, tracking_start_date, alert_seen_date, is_still_tracking, alert_sent_date)
        VALUES {sb[:-1]}
        ON CONFLICT (email, imo, region) DO UPDATE
        SET
        last_movement       = EXCLUDED.last_movement,
        tracking_start_date = EXCLUDED.tracking_start_date,
        alert_seen_date     = EXCLUDED.alert_seen_date,
        alert_sent_date     = EXCLUDED.alert_sent_date,
        is_still_tracking   = TRUE
        WHERE hra_alert.is_still_tracking = FALSE;
        '''
        try:
            self.cursor.execute(query)
            self.connection.commit()
        except Exception as e:
            print(f"Error on bulk update or addition: {e}")
            return None
    
    def update_alert_seen(self, email, imo):
        query = f'''
        UPDATE hra_alert AS h
        SET alert_seen_date=CURRENT_DATE
        FROM (VALUES
            ({imo}, '{email}')
        ) AS v(imo, email)
        where h.imo = v.imo
        and h.email = v.email
        and is_still_tracking = true
        '''
        try:
            self.cursor.execute(query)
            self.connection.commit()
        except Exception as e:
            print(f"Error on update alert seen: {e}")
            return None

    