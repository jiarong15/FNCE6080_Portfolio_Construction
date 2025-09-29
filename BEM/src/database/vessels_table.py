import pandas as pd

class VesselsTable:
    def __init__(self, connection):
        self.connection = connection
        self.cursor = connection.cursor()
        self.columns = ['id', 'name', 'vessel_id', 'imo', 'mmsi', 'build_year', 'vessel_type', 'capacity', 'dead_weight']

    def get_all_vessels(self):
        try:
            self.cursor.execute("SELECT * FROM vx_vessel")
            all_vessels = self.cursor.fetchall()
            return pd.DataFrame(all_vessels, columns=self.columns)
        except Exception as e:
            print(f"Error getting users: {e}")
            return None
    
    def get_specific_vessel(self, imo):
        try:
            self.cursor.execute("SELECT * FROM vx_vessel WHERE imo = %s", (imo,))
            vessel = self.cursor.fetchone()
            return pd.DataFrame([vessel], columns=self.columns)
        except Exception as e:
            print(f"Error getting vessel: {e}")
            return None

    def get_vessel_by_column_as_list(self, column_names):
        try:
            query = f"SELECT {', '.join(column_names)} FROM vx_vessel where imo is not null"
            self.cursor.execute(query)
            vessels = self.cursor.fetchall()
            return vessels
        except Exception as e:
            print(f"Error getting users: {e}")
            return None
