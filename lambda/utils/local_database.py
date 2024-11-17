import sqlite3
import json

class LocalSQLiteDB:
    def __init__(self, db_name):
        self.db_name = db_name
        self.mf_table_name = 'mutual_fund'
        self.mf_holdings_table_name = 'mutual_fund_holdings'


    def __enter__(self):
        self.connection = sqlite3.connect(self.db_name)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self.connection:
            self.connection.close()

    def create_table(self):
        with self.connection:
            self.connection.execute(f'''
                CREATE TABLE IF NOT EXISTS {self.mf_holdings_table_name} (
                    search_id TEXT PRIMARY KEY,
                    fund_name TEXT,
                    logo_url TEXT,
                    holdings TEXT
                )
            ''')
         
            self.connection.execute(f'''
                CREATE TABLE IF NOT EXISTS {self.mf_table_name} (
                    search_id TEXT PRIMARY KEY, 
                    fund_name TEXT,
                    category TEXT, 
                    sub_category TEXT, 
                    scheme_name TEXT, 
                    scheme_type TEXT, 
                    fund_house TEXT, 
                    risk TEXT, 
                    direct_fund TEXT, 
                    amc TEXT, 
                    aum TEXT, 
                    direct_search_id TEXT, 
                    logo_url TEXT 
                )
            ''')

            self.connection.execute(f''' 
                CREATE INDEX IF NOT EXISTS idx_mutual_fund_search_id ON {self.mf_table_name} (search_id) 
            ''')
            self.connection.execute(f''' 
                CREATE INDEX IF NOT EXISTS idx_mutual_fund_holdings_search_id ON {self.mf_holdings_table_name} (search_id) 
            ''')

    def insert_data_into_holdings(self, search_id, fund_name, logo_url, holdings):
        with self.connection:
            self.connection.execute(f'''
                INSERT INTO {self.mf_holdings_table_name} (search_id, fund_name, logo_url, holdings)
                VALUES (?, ?, ?, ?)
            ''', (search_id, fund_name, logo_url, json.dumps(holdings)))

    def insert_data_into_mutual_funds(self, mutual_fund):
        columns = ', '.join(mutual_fund.keys())
        placeholder = ', '.join('?' * len(mutual_fund))
        with self.connection:
            self.connection.execute(f'''
                INSERT INTO {self.mf_table_name} ({columns})
                VALUES ({placeholder})
            ''', (tuple(mutual_fund.values())))

    def retrieve_holdings(self, mutual_fund_search_id):
        with self.connection:
            cursor = self.connection.execute(f'''
                SELECT * FROM {self.mf_holdings_table_name} WHERE search_id = ?
            ''', (mutual_fund_search_id,))
            row = cursor.fetchone()
            if row:
                column_names = [description[0] for description in cursor.description] 
                mf_data = dict(zip(column_names, row))
                if mf_data.get('holdings'): 
                    mf_data['holdings'] = json.loads(mf_data['holdings'])
                return mf_data
            return None
        
    def retrieve_mutual_funds(self):
        with self.connection:
            cursor = self.connection.execute(f'''
                SELECT scheme_name, search_id FROM {self.mf_table_name}
            ''')
            rows = cursor.fetchall()
            column_names = [description[0] for description in cursor.description] 
            mutual_funds = [dict(zip(column_names, row)) for row in rows]
            return mutual_funds
        
    def retrieve_mutual_funds_by_id(self, mutual_fund_search_id):
        with self.connection:
            cursor = self.connection.execute(f'''
                SELECT * FROM {self.mf_table_name} WHERE search_id = ?
            ''', (mutual_fund_search_id, ))
            row = cursor.fetchone()
            if row:
                column_names = [description[0] for description in cursor.description] 
                mf_data = dict(zip(column_names, row))
                return mf_data
            return None

    def retrieve_all_data(self):
        with self.connection:
            cursor = self.connection.execute(f'''
                SELECT * FROM {self.table_name}
            ''')
            rows = cursor.fetchall()
            return [(row[1], json.loads(row[2])) for row in rows]

