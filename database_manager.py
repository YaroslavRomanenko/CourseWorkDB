import psycopg2
import psycopg2.sql as sql
import bcrypt
import json
import os
from tkinter import messagebox

class DatabaseManager:

    def __init__(self, config_filename='config.json'):
        self.db_params = self._load_config(config_filename)
        self.connection = None

    def _load_config(self, filename):
        if not os.path.exists(filename):
            print(f"Error: Configuration file '{filename}' not found")
            return None
        
        try:
            with open(filename, 'r') as f:
                config = json.load(f)
                
            if 'database' not in config:
                print(f"Error: Key 'database' not found in the file")
                messagebox.showerror("Помилка конфігурації", "Ключ 'database' не знайдено у файлі.")
                return None
            
            required_keys = {"host", "port", "dbname", "user", "password"} 
            if not required_keys.issubset(config['database'].keys()):
                missing_keys = required_keys - config['database'].keys()
                print(f"Error: Keys {missing_keys} missing from 'database' section")
                messagebox.showerror("Помилка конфігурації", f"Відсутні ключі у секції 'database': {missing_keys}")
                return None
            
            print("Configuration loaded successfully!")
            return config['database']
        
        except json.JSONDecodeError:
            print(f"Error: Unable to parse JSON in '{filename}' file")
            messagebox.showerror("Помилка конфігурації", f"Не вдалося розпарсити JSON у файлі '{filename}'.")
            return None
        except Exception as e:
            print(f"Unexpected error when loading configuration: {e}")
            messagebox.showerror("Помилка конфігурації", f"Неочікувана помилка: {e}")
            return None

    def _connect(self):
        conn = None
        if not self.db_params:
            return None
        try:
            print(f"Connecting to the database '{self.db_params['dbname']}' on {self.db_params['host']}...")
            conn = psycopg2.connect(**self.db_params)
            print("The Connection is Successful!")
            with conn.cursor() as cur:
                 cur.execute("SELECT version();")
                 db_version = cur.fetchone()
                 if db_version:
                    print(f"Postgre Version: {db_version[0]}")
            return conn
        
        except psycopg2.OperationalError as e:
            print(f"\nError connecting to PostgreSQL: {e}")
            return None
        except Exception as e:
            print(f"\nUnexpected error during trying to connect: {e}")
            return None

    def get_connection(self):
        if self.connection and not self.connection.closed:
            return self.connection
        print("Connection lost. Attempting to reconnect...")
        self.connection = self._connect()
        return self.connection

    def close_connection(self):
        if self.connection and not self.connection.closed:
            try:
                self.connection.close()
                print("\n--- Connection with PostgreSQL is closed ---")
            except Exception as e:
                 print(f"Error closing database connection: {e}")
        self.connection = None

    def execute_many_query(self, query, params_list):
        """Executes a query multiple times with different parameters"""
        conn = self.get_connection()
        if not conn:
            print("Cannot execute bulk query: No active database connection")
            return None
        
        result = None
        try:
            with conn:
                with conn.cursor() as cur:
                    cur.executemany(query, params_list)
                    result = cur.rowcount
                    print(f"Successfully executed bulk query for {result} rows")
        
        except(Exception, psycopg2.Error) as error:
            print(f"\nError executing bulk query: {error}")
            print(f"Query: {query}")
            print(f"Number of parameter sets attempted: {len(params_list)}")
            return None
        
        return result

    def execute_query(self, query, params=None, fetch_one=False, fetch_all=False):
        conn = self.get_connection()
        if not conn:
            print("Cannot execute query: No active database connection")
            return None
        
        result = None
        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute(query, params)
                    
                    if fetch_one:
                        result = cur.fetchone()
                    elif fetch_all:
                        result = cur.fetchall()
                    else:
                         try:
                            result = cur.rowcount 
                         except psycopg2.ProgrammingError: 
                             result = None 
                             
        except (Exception, psycopg2.Error) as error:
            print(f"\Error executing query: {error}")
            print(f"query: {query}")
            print(f"Parameters: {params}")
        
            return None 

        return result
    
    def clear_specified_table(self, table_name):
        """Deleting all data from specified table"""
        try:
            query = sql.SQL("TRUNCATE TABLE {} RESTART IDENTITY CASCADE").format(sql.Identifier(table_name))
            print(f"A safe query has formed: {query.as_string(self.get_connection())}")
            
            result = self.execute_query(query)
            
            if result is None:
                print(f"Failed to clear the table '{table_name}'")
                return False
            else:
                return True
        
        except Exception as e:
            print(f"Unexpected error was occurred while trying to clear the table '{table_name}' : {e}")
            return False

    def validate_user(self, username, password):
        print(f"DBManager validating user: {username}")
        query = "SELECT user_id, password_hash FROM Users WHERE username = %s;"
        result = self.execute_query(query, (username,), fetch_one=True)

        if result:
            user_id, stored_hash = result
            if bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8')):
                print(f"User {username} validated successfully. User ID: {user_id}")
                return user_id
            else:
                print(f"Password validation failed for user {username}")
                return None # Пароль невірний
        else:
            print(f"User {username} not found.")
            return None 


    def fetch_all_games(self):
        query = "SELECT game_id, title, NULL AS genre, price, image FROM games ORDER BY title;"
        print("DB: Fetching all games with image IDs...")
        games_data = self.execute_query(query, fetch_all=True)
        if games_data is None:
            print("DB: Failed to fetch games")
        elif not games_data:
            print(f"DB: Fetched {len(games_data)} games")
        return games_data
    
    def fetch_game_details(self, game_id):
        query = """
            SELECT
                game_id, title, description, price, image, status, release_date
            FROM games
            WHERE game_id = %s;
        """
        print(f"DB: Fetching details for game_id {game_id}...")
        game_tuple = self.execute_query(query, (game_id,), fetch_one=True)
        if game_tuple:
            details = {
                'game_id': game_tuple[0], 'title': game_tuple[1], 'description': game_tuple[2],
                'price': game_tuple[3], 'image': game_tuple[4], 'status': game_tuple[5],
                'release_date': game_tuple[6]
            }
            return details
        else: return None

        if game_tuple:
            print(f"DB: Details found for game_id {game_id}.")
            details = {
                'game_id': game_tuple[0],
                'title': game_tuple[1],
                'description': game_tuple[2],
                'price': game_tuple[3],
                'image': game_tuple[4],
                'status': game_tuple[5],
                'release_date': game_tuple[6]
            }
            return details
        else:
            print(f"DB: No details found for game_id {game_id}.")
            return None
    