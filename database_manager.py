import psycopg2
import psycopg2.sql as sql
import bcrypt
import json
import os
from tkinter import messagebox
from decimal import Decimal, InvalidOperation

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
        
    def register_user(self, username, email, password):
        conn = self.get_connection()
        if not conn:
            messagebox.showerror("Помилка Бази Даних", "Не вдалося підключитися до бази даних для реєстрації.")
            return False

        try:
            password_bytes = password.encode('utf-8')
            salt = bcrypt.gensalt()
            hashed_password_bytes = bcrypt.hashpw(password_bytes, salt)
            hashed_password_str = hashed_password_bytes.decode('utf-8')
        except Exception as e:
            print(f"DB: Помилка хешування пароля для {username}: {e}")
            messagebox.showerror("Помилка Реєстрації", f"Внутрішня помилка під час обробки пароля: {e}")
            return False

        query = sql.SQL("""
            INSERT INTO Users (username, email, password_hash)
            VALUES (%s, %s, %s);
        """)
        params = (username, email, hashed_password_str)

        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute(query, params)
            return True

        except psycopg2.IntegrityError as e:
            print(f"DB: IntegrityError during registration for {username}: {e}")
            if "users_username_key" in str(e).lower():
                messagebox.showerror("Помилка Реєстрації", f"Користувач з іменем '{username}' вже існує.")
            elif "users_email_key" in str(e).lower():
                 messagebox.showerror("Помилка Реєстрації", f"Електронна пошта '{email}' вже використовується.")
            else:
                 messagebox.showerror("Помилка Реєстрації", f"Помилка цілісності даних: {e}")
            return False

        except (Exception, psycopg2.Error) as error:
            print(f"\nDB: Error during user registration for '{username}': {error}")
            print(f"Query: {query.as_string(conn) if conn else query}")
            print(f"Parameters: {params}")
            messagebox.showerror("Помилка Бази Даних", f"Не вдалося зареєструвати користувача:\n{error}")
            return False


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
        
    def fetch_purchased_games(self, user_id):
        query = """
            SELECT DISTINCT
                g.game_id,
                g.title,
                NULL AS genre, -- Placeholder for UI compatibility
                g.price,       -- Current game price
                g.image
            FROM Games g
            JOIN Purchases_Items pi ON g.game_id = pi.game_id
            JOIN Purchases p ON pi.purchase_id = p.purchase_id
            WHERE p.user_id = %s
              AND p.status = 'Completed' -- Ensure the purchase was successful
            ORDER BY g.title;
        """
        print(f"DB: Fetching purchased games for user_id {user_id}...")
        try:
            purchased_games = self.execute_query(query, (user_id,), fetch_all=True)

            if purchased_games is None:
                print(f"DB: Error occurred while fetching purchased games for user_id {user_id}.")
                return None
            elif not purchased_games:
                print(f"DB: No purchased games found for user_id {user_id}.")
                return []
            else:
                print(f"DB: Found {len(purchased_games)} purchased games for user_id {user_id}.")
                return purchased_games
        except Exception as e:
            print(f"DB: Unexpected error fetching purchased games for user_id {user_id}: {e}")
            
    def purchase_game(self, user_id, game_id, price_at_purchase):
        conn = self.get_connection()
        if not conn:
            print("Cannot purchase game: No active database connection")
            return False
        try:
            if price_at_purchase is None or float(price_at_purchase) == 0.0:
                final_price = Decimal('0.00')
            else:
                final_price = Decimal(str(price_at_purchase)).quantize(Decimal("0.01"))
        except (ValueError, TypeError, InvalidOperation):
             print(f"Error: Invalid price format for purchase: {price_at_purchase}")
             return False

        purchase_id = None
        try:
            with conn:
                with conn.cursor() as cur:
                    purchase_query = sql.SQL("""
                        INSERT INTO Purchases (user_id, total_amount, status)
                        VALUES (%s, %s, %s)
                        RETURNING purchase_id;
                    """)
                    cur.execute(purchase_query, (user_id, final_price, 'Completed'))
                    result = cur.fetchone()

                    if result and result[0]:
                        purchase_id = result[0]
                        print(f"DB: Created Purchases record with ID: {purchase_id}")
                    else:
                        print("DB: Failed to create Purchases record or retrieve purchase_id.")
                        raise psycopg2.DatabaseError("Failed to create Purchases record") 

                    item_query = sql.SQL("""
                        INSERT INTO Purchases_Items (purchase_id, game_id, price_at_purchase)
                        VALUES (%s, %s, %s);
                    """)
                    cur.execute(item_query, (purchase_id, game_id, final_price))

                    if cur.rowcount != 1:
                         print(f"DB: Failed to insert into Purchases_Items for purchase_id {purchase_id}, game_id {game_id}.")
                         raise psycopg2.DatabaseError("Failed to insert purchase item")

                    print(f"DB: Added game {game_id} to purchase {purchase_id} successfully.")

            return True

        except (Exception, psycopg2.Error) as error:
            print(f"\nError during game purchase transaction: {error}")
            if purchase_id:
                 print(f"Transaction for purchase_id {purchase_id} rolled back.")
            else:
                 print("Transaction rolled back before Purchases record was fully created.")
            return False
        
    def check_ownership(self, user_id, game_id):
        query = """
            SELECT EXISTS (
                SELECT 1
                FROM Purchases_Items pi
                JOIN Purchases p ON pi.purchase_id = p.purchase_id
                WHERE p.user_id = %s
                  AND pi.game_id = %s
                  AND p.status = 'Completed'
            );
        """
        try:
            result = self.execute_query(query, (user_id, game_id), fetch_one=True)
            return result[0] if result else False
        except Exception as e:
            print(f"DB: Error checking ownership for user {user_id}, game {game_id}: {e}")
            return False
    