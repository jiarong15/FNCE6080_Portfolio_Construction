from datetime import datetime
import pandas as pd

class HraUserTable:
    def __init__(self, connection):
        self.connection = connection
        self.cursor = connection.cursor()
        self.columns = ['id', 'email', 'first_name', 'last_name', 'status', 'created_at', 'last_login', 'code']

    def get_all_users(self):
        try:
            self.cursor.execute("SELECT * FROM hra_user where status='ACTIVE'")
            all_users = self.cursor.fetchall()
            return pd.DataFrame(all_users, columns=self.columns)
        except Exception as e:
            print(f"Error getting users: {e}")
            return None

    def add_user(self, first_name, last_name, email, code):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            query = f"INSERT INTO hra_user (email, firstname, lastname, status, created_at, last_login, code) VALUES ('{email}', '{first_name}', '{last_name}', 'ACTIVE', '{now}', '{now}', '{code}')"
            self.cursor.execute(query)
            self.connection.commit()
        except Exception as e:
            print(f"Error adding user: {e}")
            return None
    
    def update_otp_code(self, email, code):
        try:
            query = f"UPDATE hra_user SET code='{code}' WHERE email='{email}'"
            self.cursor.execute(query)
            self.connection.commit()
        except Exception as e:
            print(f"Error updating OTP code: {e}")
            return None

    def get_user_by_email(self, email):
        try:
            query = f"SELECT * FROM hra_user WHERE email='{email}' and status='ACTIVE'"
            self.cursor.execute(query)
            user = self.cursor.fetchone()
            return pd.DataFrame([user], columns=self.columns)
        except Exception as e:
            print(f"Error getting users: {e}")
            return None
