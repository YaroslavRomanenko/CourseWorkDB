import psycopg2
import psycopg2.sql as sql
import bcrypt
import json
import os
import decimal
import traceback

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


    def fetch_all_games(self, sort_by='title', sort_order='ASC'):
        conn = self.get_connection()
        if not conn:
            print("DB: No connection to fetch games.")
            return None

        allowed_sort_columns = {'title', 'price'}
        if sort_by not in allowed_sort_columns:
            print(f"DB Warning: Invalid sort column '{sort_by}'. Defaulting to 'title'.")
            sort_by = 'title'

        sort_order = sort_order.upper()
        if sort_order not in ('ASC', 'DESC'):
            print(f"DB Warning: Invalid sort order '{sort_order}'. Defaulting to 'ASC'.")
            sort_order = 'ASC'

        order_by_clause = sql.SQL("ORDER BY {sort_col} {sort_dir}")

        if sort_by == 'price':
            if sort_order == 'ASC':
                order_by_clause = sql.SQL("ORDER BY {sort_col} {sort_dir} NULLS FIRST, {secondary_col} ASC")
            else: # DESC
                order_by_clause = sql.SQL("ORDER BY {sort_col} {sort_dir} NULLS LAST, {secondary_col} ASC")
            order_by_sql = order_by_clause.format(
                sort_col=sql.Identifier(sort_by),
                sort_dir=sql.SQL(sort_order),
                secondary_col=sql.Identifier('title')
            )
        else:
            order_by_sql = order_by_clause.format(
                sort_col=sql.Identifier(sort_by),
                sort_dir=sql.SQL(sort_order)
            )

        base_query = sql.SQL("SELECT game_id, title, NULL AS genre, price, image FROM games")
        query = sql.SQL(" ").join([base_query, order_by_sql])

        print(f"DB: Fetching all games sorted by {sort_by} {sort_order}...")
        try:
            games_data = self.execute_query(query, fetch_all=True)

            if games_data is None:
                print("DB: Failed to fetch games (execute_query returned None)")
                return None
            elif not games_data:
                print("DB: Fetched 0 games.")
                return []
            else:
                print(f"DB: Fetched {len(games_data)} games.")
                return games_data
        except Exception as e:
            print(f"DB: Unexpected error fetching sorted games: {e}")
            traceback.print_exc()
            return None
    
    def fetch_game_details(self, game_id):
        query = """
            SELECT
                game_id, title, description, price, image, status, release_date,
                created_at, updated_at  -- Додано created_at, updated_at
            FROM games
            WHERE game_id = %s;
        """
        print(f"DB: Fetching details for game_id {game_id}...")
        game_tuple = self.execute_query(query, (game_id,), fetch_one=True)
        if game_tuple:
            details = {
                'game_id': game_tuple[0],
                'title': game_tuple[1],
                'description': game_tuple[2],
                'price': game_tuple[3],
                'image': game_tuple[4],
                'status': game_tuple[5],
                'release_date': game_tuple[6],
                'created_at': game_tuple[7], 
                'updated_at': game_tuple[8]
            }
            return details
        else:
            return None
        
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
            messagebox.showerror("Помилка Бази Даних", "Немає активного підключення до бази даних.")
            return False

        try:
            if price_at_purchase is None:
                 final_price = decimal.Decimal('0.00')
            else:
                final_price = decimal.Decimal(str(price_at_purchase)).quantize(decimal.Decimal("0.01"))
        except (ValueError, TypeError, decimal.InvalidOperation) as e:
             print(f"Error: Invalid price format for purchase: {price_at_purchase} - {e}")
             messagebox.showerror("Помилка ціни", f"Некоректний формат ціни для покупки: {price_at_purchase}")
             return False

        purchase_id = None
        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT balance FROM Users WHERE user_id = %s FOR UPDATE;", (user_id,))
                    current_balance_tuple = cur.fetchone()
                    if not current_balance_tuple:
                        raise ValueError("Користувача не знайдено.")

                    current_balance = decimal.Decimal(str(current_balance_tuple[0])).quantize(decimal.Decimal("0.01"))
                    if current_balance < final_price:
                        messagebox.showerror("Недостатньо коштів", f"На вашому рахунку недостатньо коштів ({current_balance:.2f}₴) для покупки гри за {final_price:.2f}₴.")
                        conn.rollback()
                        return False

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
                        raise psycopg2.DatabaseError("Failed to create Purchases record")

                    item_query = sql.SQL("""
                        INSERT INTO Purchases_Items (purchase_id, game_id, price_at_purchase)
                        VALUES (%s, %s, %s);
                    """)
                    cur.execute(item_query, (purchase_id, game_id, final_price))

                    if cur.rowcount != 1:
                         raise psycopg2.DatabaseError("Failed to insert purchase item")

                    if final_price > 0:
                        new_balance = current_balance - final_price
                        cur.execute("UPDATE Users SET balance = %s WHERE user_id = %s;", (new_balance, user_id))
                        if cur.rowcount != 1:
                             raise psycopg2.DatabaseError("Failed to update user balance")
                        print(f"DB: Updated balance for user {user_id} to {new_balance:.2f}")

                    print(f"DB: Added game {game_id} to purchase {purchase_id} successfully.")
            return True

        except (ValueError, psycopg2.DatabaseError) as db_error:
            print(f"\nError during game purchase transaction: {db_error}")
            return False
        except (Exception, psycopg2.Error) as error:
            print(f"\nUnexpected error during game purchase transaction: {error}")
            traceback.print_exc()
            messagebox.showerror("Помилка Транзакції", f"Сталася неочікувана помилка під час покупки:\n{error}")
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
        
    def add_or_update_review(self, user_id, game_id, review_text, rating=None):
        conn = self.get_connection()
        if not conn:
            messagebox.showerror("Помилка Бази Даних", "Не вдалося підключитися до бази даних.")
            return False

        query = sql.SQL("""
            INSERT INTO reviews (user_id, game_id, review_text, rating, review_date)
            VALUES (%s, %s, %s, %s, CURRENT_TIMESTAMP);
        """)
        params = (user_id, game_id, review_text, rating)

        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute(query, params)
            print(f"DB: Review for game {game_id} by user {user_id} added successfully.")
            return True

        except (Exception, psycopg2.Error) as error:
            print(f"\nDB: Error adding review for game {game_id}, user {user_id}: {error}")
            print(f"Query: {query.as_string(conn) if conn else query}")
            print(f"Parameters: {params}")
            messagebox.showerror("Помилка Бази Даних", f"Не вдалося додати рецензію:\n{error}")
            return False
    
    def fetch_game_reviews(self, game_id):
        conn = self.get_connection()
        if not conn: return None
        query = sql.SQL("""
            SELECT r.review_id, u.username, r.review_text, r.review_date
            FROM reviews r JOIN users u ON r.user_id = u.user_id
            WHERE r.game_id = %s ORDER BY r.review_date DESC;
        """)
        try:
            reviews_data = self.execute_query(query, (game_id,), fetch_all=True)
            return reviews_data
        except Exception as error:
            print(f"DB: Error fetching reviews for game {game_id}: {error}")
            return None
        
    def fetch_review_comments(self, review_id):
        conn = self.get_connection()
        if not conn: return None
        query = sql.SQL("""
            SELECT u.username, rc.comment_text, rc.comment_date
            FROM reviewcomments rc JOIN users u ON rc.user_id = u.user_id
            WHERE rc.review_id = %s ORDER BY rc.comment_date ASC;
        """)
        try:
            comments_data = self.execute_query(query, (review_id,), fetch_all=True)
            return comments_data
        except Exception as error:
            print(f"DB: Error fetching comments for review {review_id}: {error}")
            return None
        
    def add_review_comment(self, review_id, user_id, comment_text):
        conn = self.get_connection()
        if not conn:
            messagebox.showerror("Помилка Бази Даних", "Не вдалося підключитися до бази даних.")
            return False
        query = sql.SQL("""
            INSERT INTO reviewcomments (review_id, user_id, comment_text, comment_date)
            VALUES (%s, %s, %s, CURRENT_TIMESTAMP);
        """)
        params = (review_id, user_id, comment_text)
        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute(query, params)
            return True
        except (Exception, psycopg2.Error) as error:
            print(f"\nDB: Error adding comment to review {review_id} by user {user_id}: {error}")
            messagebox.showerror("Помилка Бази Даних", f"Не вдалося додати коментар:\n{error}")
            return False
        
    def fetch_game_genres(self, game_id):
        conn = self.get_connection()
        if not conn or game_id is None:
            return []

        query = sql.SQL("""
            SELECT g.name
            FROM Genres g
            JOIN Game_Genres gg ON g.genre_id = gg.genre_id
            WHERE gg.game_id = %s
            ORDER BY g.name;
        """)
        try:
            results = self.execute_query(query, (game_id,), fetch_all=True)
            return [row[0] for row in results] if results else []
        except Exception as e:
            print(f"DB: Error fetching genres for game_id {game_id}: {e}")
            return []
        
    def fetch_game_platforms(self, game_id):
        conn = self.get_connection()
        if not conn or game_id is None:
            return []

        query = sql.SQL("""
            SELECT p.name
            FROM Platforms p
            JOIN Game_Platforms gp ON p.platform_id = gp.platform_id
            WHERE gp.game_id = %s
            ORDER BY p.name;
        """)
        try:
            results = self.execute_query(query, (game_id,), fetch_all=True)
            return [row[0] for row in results] if results else []
        except Exception as e:
            print(f"DB: Error fetching platforms for game_id {game_id}: {e}")
            return []
        
    def fetch_game_studios_by_role(self, game_id, role):
        conn = self.get_connection()
        if not conn or game_id is None:
            print(f"DB: Cannot fetch studios for game {game_id}, role {role}. Connection or game_id missing.")
            return []

        valid_roles = ['Developer', 'Publisher']
        if role not in valid_roles:
             print(f"DB: Invalid role '{role}' requested for game {game_id}.")
             return []

        query = sql.SQL("""
            SELECT s.name
            FROM Studios s
            JOIN Game_Studios gs ON s.studio_id = gs.studio_id
            WHERE gs.game_id = %s AND gs.role = %s
            ORDER BY s.name;
        """)
        try:
            params = (game_id, role)
            results = self.execute_query(query, params, fetch_all=True)
            studio_names = [row[0] for row in results] if results else []
            print(f"DB: Fetched {len(studio_names)} {role}(s) for game {game_id}: {studio_names}")
            return studio_names
        except Exception as e:
            print(f"DB: Error fetching {role} studios for game_id {game_id}: {e}")
            return []
        
          
    def fetch_studio_details_by_name(self, studio_name):
        conn = self.get_connection()
        if not conn or not studio_name:
            return None

        query = sql.SQL("""
            SELECT studio_id, name, website_url, logo, country, description, established_date
            FROM Studios
            WHERE name = %s;
        """)
        try:
            studio_tuple = self.execute_query(query, (studio_name,), fetch_one=True)
            if studio_tuple:
                details = {
                    'studio_id': studio_tuple[0], 'name': studio_tuple[1], 'website_url': studio_tuple[2],
                    'logo': studio_tuple[3], 'country': studio_tuple[4], 'description': studio_tuple[5],
                    'established_date': studio_tuple[6]
                }
                print(f"DB: Fetched details for studio: {studio_name}")
                return details
            else:
                print(f"DB: Studio not found: {studio_name}")
                return None
        except Exception as e:
            print(f"DB: Error fetching studio details for '{studio_name}': {e}")
            return None
        
    def fetch_user_info(self, user_id):
        query = "SELECT username, balance FROM Users WHERE user_id = %s;"
        print(f"DB: Fetching user info for user_id {user_id}...")
        result = self.execute_query(query, (user_id,), fetch_one=True)
        if result:
            try:
                balance = decimal.Decimal(str(result[1])).quantize(decimal.Decimal("0.01"))
                return {'username': result[0], 'balance': balance}
            except (TypeError, decimal.InvalidOperation):
                 print(f"DB Warning: Invalid balance format for user {user_id}. Returning 0.00.")
                 return {'username': result[0], 'balance': decimal.Decimal('0.00')}
        else:
            print(f"DB: User info not found for user_id {user_id}.")
            return None

    def add_funds(self, user_id, amount_to_add):
        conn = self.get_connection()
        if not conn:
            print("DB Error: No connection to add funds.")
            return False

        try:
            amount_decimal = decimal.Decimal(str(amount_to_add)).quantize(decimal.Decimal("0.01"))
            if amount_decimal <= 0:
                print(f"DB Error: Amount to add must be positive ({amount_decimal}).")
                return False
        except (ValueError, TypeError, decimal.InvalidOperation) as e:
            print(f"DB Error: Invalid amount format '{amount_to_add}': {e}")
            return False

        query = sql.SQL("UPDATE Users SET balance = balance + %s WHERE user_id = %s;")
        params = (amount_decimal, user_id)

        try:
            print(f"DB: Attempting to add {amount_decimal} to balance for user_id {user_id}")
            with conn:
                with conn.cursor() as cur:
                    cur.execute(query, params)
                    if cur.rowcount == 1:
                        print(f"DB: Successfully added funds for user_id {user_id}.")
                        return True
                    else:
                        print(f"DB Error: User with user_id {user_id} not found.")
                        return False
        except psycopg2.Error as db_error:
            print(f"\nDB Error adding funds for user {user_id}: {db_error}")
            return False
        except Exception as e:
            print(f"\nDB Unexpected error adding funds for user {user_id}: {e}")
            traceback.print_exc()
            return False
        
    def check_developer_status(self, user_id):
        query = sql.SQL("""
            SELECT EXISTS (
                SELECT 1
                FROM Developers
                WHERE user_id = %s
            );
        """)
        print(f"DB: Checking developer status by checking existence in Developers table for user_id {user_id}...")
        try:
            result = self.execute_query(query, (user_id,), fetch_one=True)
            if result:
                is_dev = result[0]
                print(f"DB: Developer status for user {user_id}: {is_dev}")
                return is_dev
            else:
                print(f"DB Warning: Failed to execute developer status check query for user {user_id}.")
                return False
        except Exception as e:
            print(f"DB: Error checking developer status for user {user_id}: {e}")
            traceback.print_exc()
            return False
        
    def set_developer_status(self, user_id, status=True):
        conn = self.get_connection()
        if not conn:
            messagebox.showerror("Помилка Бази Даних", "Немає активного підключення до бази даних.")
            return False

        if status:
            email_query = sql.SQL("SELECT email FROM Users WHERE user_id = %s;")
            user_info = self.execute_query(email_query, (user_id,), fetch_one=True)
            if not user_info or not user_info[0]:
                print(f"DB Error: Could not find email for user_id {user_id} to add to Developers.")
                messagebox.showerror("Помилка", f"Не вдалося знайти email для користувача ID {user_id}.")
                return False
            contact_email = user_info[0]

            print(f"DB Logic Error: Cannot set developer status for user {user_id} without a studio_id. Feature requires redesign or schema change.")
            messagebox.showerror("Помилка Логіки", "Неможливо встановити статус розробника без прив'язки до студії. Зверніться до адміністратора або доопрацюйте функціонал.")
            return False
        
        else:
            delete_query = sql.SQL("DELETE FROM Developers WHERE user_id = %s;")
            params = (user_id,)
            try:
                print(f"DB: Attempting to remove user {user_id} from Developers table.")
                with conn:
                    with conn.cursor() as cur:
                        cur.execute(delete_query, params)
                        print(f"DB: Removed {cur.rowcount} developer entries for user_id {user_id}.")
                        return True
            except psycopg2.Error as db_error:
                print(f"\nDB Error removing developer status for user {user_id}: {db_error}")
                messagebox.showerror("Помилка Бази Даних", f"Не вдалося зняти статус розробника:\n{db_error}")
                return False
            except Exception as e:
                print(f"\nDB Unexpected error removing developer status for user {user_id}: {e}")
                traceback.print_exc()
                messagebox.showerror("Неочікувана Помилка", f"Сталася неочікувана помилка під час зняття статусу:\n{e}")
                return False
          
    def delete_user_account(self, user_id):
        conn = self.get_connection()
        if not conn:
            messagebox.showerror("Помилка Бази Даних", "Немає активного підключення до бази даних.")
            return False

        query = sql.SQL("DELETE FROM Users WHERE user_id = %s;")
        params = (user_id,)

        try:
            print(f"DB: Attempting to delete user account with ID: {user_id}")
            with conn:
                with conn.cursor() as cur:
                    cur.execute(query, params)
                    if cur.rowcount == 1:
                        print(f"DB: Successfully deleted user account with ID: {user_id}")
                        return True
                    else:
                        print(f"DB: User account with ID: {user_id} not found for deletion.")
                        messagebox.showerror("Помилка видалення", f"Користувача з ID {user_id} не знайдено.")
                        return False
        except psycopg2.Error as db_error:
            print(f"\nDB: Error deleting user account {user_id}: {db_error}")
            messagebox.showerror("Помилка Бази Даних", f"Не вдалося видалити акаунт:\n{db_error}")
            return False
        except Exception as e:
            print(f"\nDB: Unexpected error deleting user account {user_id}: {e}")
            traceback.print_exc()
            messagebox.showerror("Неочікувана Помилка", f"Сталася неочікувана помилка під час видалення акаунту:\n{e}")
            return False

    
        