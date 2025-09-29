
class UserWhitelistTable:
    def __init__(self, connection):
        self.connection = connection
        self.cursor = connection.cursor()

    def get_all_whitelist_domain(self):
        try:
            self.cursor.execute("SELECT domain FROM email_whitelist")
            all_whitelist = self.cursor.fetchall()
            return all_whitelist
        except Exception as e:
            print(f"Error getting whitelist domains: {e}")
            return None
