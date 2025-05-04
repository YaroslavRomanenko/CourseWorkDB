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
        """Constructor"""
        self.db_params = self._load_config(config_filename)
        self.connection = None

    def _load_config(self, filename):
        """Loads and checks configuration of data base from JSON-file"""
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
        """Establishes an actual connection with data base"""
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
        """Provides a working connection with data base"""
        if self.connection and not self.connection.closed:
            return self.connection
        print("Connection lost. Attempting to reconnect...")
        self.connection = self._connect()
        return self.connection

    def close_connection(self):
        """Closes an active connection with data base if it still exists"""
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
        """Executes one SQL-query"""
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
        """Checks whether a user with that username exists and whether the provided password matches the stored hash in the database"""
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
                return None
        else:
            print(f"User {username} not found.")
            return None
        
    def register_user(self, username, email, password):
        """Registers a new user in the system"""
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
        """Fetches a list of all games from the database to display in the store. Sortable"""
        conn = self.get_connection()
        if not conn:
            print("DB: No connection to fetch games.")
            return None

        allowed_sort_columns = {'title', 'price', 'purchase_count'}
        if sort_by not in allowed_sort_columns:
            print(f"DB Warning: Invalid sort column '{sort_by}'. Defaulting to 'title'.")
            sort_by = 'title'

        sort_order = sort_order.upper()
        if sort_order not in ('ASC', 'DESC'):
            print(f"DB Warning: Invalid sort order '{sort_order}'. Defaulting to 'ASC'.")
            sort_order = 'ASC'

        base_query = sql.SQL("""
            SELECT
                g.game_id, g.title, NULL AS genre, g.price, g.image,
                COUNT(pi.purchase_item_id) AS purchase_count
            FROM
                games g
            LEFT JOIN
                Purchases_Items pi ON g.game_id = pi.game_id
            LEFT JOIN
                Purchases p ON pi.purchase_id = p.purchase_id AND p.status = 'Completed'
            GROUP BY
                g.game_id, g.title, g.price, g.image
        """)

        order_by_clause = sql.SQL("ORDER BY {sort_col} {sort_dir}")
        secondary_sort_col = 'title' if sort_by != 'title' else 'purchase_count'

        if sort_by == 'price':
            if sort_order == 'ASC':
                order_by_clause = sql.SQL("ORDER BY {sort_col} {sort_dir} NULLS FIRST, {secondary_col} ASC")
            else:
                order_by_clause = sql.SQL("ORDER BY {sort_col} {sort_dir} NULLS LAST, {secondary_col} ASC")
            order_by_sql = order_by_clause.format(
                sort_col=sql.Identifier(sort_by),
                sort_dir=sql.SQL(sort_order),
                secondary_col=sql.Identifier(secondary_sort_col)
            )
        else:
            order_by_sql = order_by_clause.format(
                sort_col=sql.Identifier(sort_by),
                sort_dir=sql.SQL(sort_order),
            )
            order_by_sql = sql.SQL(" ").join([order_by_sql, sql.SQL(", {secondary_col} ASC").format(secondary_col=sql.Identifier(secondary_sort_col))])

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
        """Fetches detailed information about one concrete game by it's id"""
        query = """
            SELECT
                g.game_id, g.title, g.description, g.price, g.image, g.status,
                g.release_date, g.created_at, g.updated_at,
                COUNT(r.review_id) AS review_count
            FROM
                games g
            LEFT JOIN
                reviews r ON g.game_id = r.game_id
            WHERE
                g.game_id = %s
            GROUP BY
                g.game_id, g.title, g.description, g.price, g.image, g.status,
                g.release_date, g.created_at, g.updated_at;
        """
        print(f"DB: Fetching details and review count for game_id {game_id}...")
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
                'updated_at': game_tuple[8],
                'review_count': game_tuple[9]
            }
            print(f"DB: Fetched details for game {game_id}: Review count = {details['review_count']}")
            return details
        else:
            print(f"DB: Game details not found for game_id {game_id}.")
            return None
        
    def fetch_purchased_games(self, user_id):
        """Fetches a list of games that have been successfully bought by a concrete user"""
        query = """
            SELECT DISTINCT
                g.game_id,
                g.title,
                NULL AS genre,
                g.price,
                g.image
            FROM Games g
            JOIN Purchases_Items pi ON g.game_id = pi.game_id
            JOIN Purchases p ON pi.purchase_id = p.purchase_id
            WHERE p.user_id = %s
              AND p.status = 'Completed'
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
            return None
            
    def purchase_game(self, user_id, game_id, price_at_purchase):
        """Implements a logic for user to purchase a game"""
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
        """Checks if the user has a specific game"""
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
        
    def add_or_update_review(self, user_id, game_id, review_text):
        """Adds a new review on a game from the user"""
        conn = self.get_connection()
        if not conn:
            messagebox.showerror("Помилка Бази Даних", "Не вдалося підключитися до бази даних.")
            return False

        query = sql.SQL("""
            INSERT INTO reviews (user_id, game_id, review_text, review_date)
            VALUES (%s, %s, %s, CURRENT_TIMESTAMP);
        """)
        params = (user_id, game_id, review_text)

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
        """Fetches all reviews for concrete game"""
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
        """Adds a new comment to an existing review"""
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
        """Fetches a list of genre names for a specific game"""
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
        """Fetches a list of platform names for a specific game"""
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
        """Fetches a list of studio names associated with game in specific role"""
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
        """Fetches detailed information about studio by it's name"""
        conn = self.get_connection()
        if not conn or not studio_name:
            return None

        details = None
        developer_count = 0
        game_count = 0

        query_details = sql.SQL("""
            SELECT studio_id, name, website_url, logo, country, description, established_date
            FROM Studios WHERE name = %s;
        """)
        try:
            studio_tuple = self.execute_query(query_details, (studio_name,), fetch_one=True)
            if studio_tuple:
                studio_id = studio_tuple[0]
                details = {
                    'studio_id': studio_id, 'name': studio_tuple[1], 'website_url': studio_tuple[2],
                    'logo': studio_tuple[3], 'country': studio_tuple[4], 'description': studio_tuple[5],
                    'established_date': studio_tuple[6]
                }
                print(f"DB: Fetched base details for studio: {studio_name} (ID: {studio_id})")

                query_dev_count = sql.SQL("SELECT COUNT(*) FROM Developers WHERE studio_id = %s;")
                dev_count_result = self.execute_query(query_dev_count, (studio_id,), fetch_one=True)
                if dev_count_result:
                    developer_count = dev_count_result[0]
                print(f"DB: Developer count for studio {studio_id}: {developer_count}")

                query_game_count = sql.SQL("SELECT COUNT(DISTINCT game_id) FROM Game_Studios WHERE studio_id = %s;")
                game_count_result = self.execute_query(query_game_count, (studio_id,), fetch_one=True)
                if game_count_result:
                    game_count = game_count_result[0]
                print(f"DB: Game count for studio {studio_id}: {game_count}")

                details['developer_count'] = developer_count
                details['game_count'] = game_count

            else:
                print(f"DB: Studio not found: {studio_name}")
                return None
        except Exception as e:
            print(f"DB: Error fetching full studio details for '{studio_name}': {e}")
            traceback.print_exc()
            return None

        return details
        
    def fetch_user_info(self, user_id):
        """Fetches the username and their current balance"""
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
        """Adds specified sum of finds on user's balance"""
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
        print(f"DB: Checking developer status for user_id {user_id}...")
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

    def set_developer_status(self, user_id, status=True, contact_email=None):
        conn = self.get_connection()
        if not conn:
            messagebox.showerror("Помилка Бази Даних", "Немає активного підключення до бази даних.")
            return False

        if status:
            if not contact_email:
                email_query = sql.SQL("SELECT email FROM Users WHERE user_id = %s;")
                user_info = self.execute_query(email_query, (user_id,), fetch_one=True)
                if user_info and user_info[0]:
                    contact_email = user_info[0]
                    print(f"DB: No contact email provided for becoming developer (user {user_id}). Using primary email: {contact_email}")
                else:
                    messagebox.showerror("Помилка", "Не вдалося визначити контактну пошту для розробника.")
                    print(f"DB Error: Cannot set developer status for user {user_id} without a contact email.")
                    return False

            insert_query = sql.SQL("""
                INSERT INTO Developers (user_id, studio_id, contact_email)
                VALUES (%s, NULL, %s)
                ON CONFLICT (user_id) DO NOTHING;
            """)
            params = (user_id, contact_email)
            action_desc = "ensure developer entry"

        else:
            insert_query = sql.SQL("DELETE FROM Developers WHERE user_id = %s;")
            params = (user_id,)
            action_desc = "remove developer status"

        try:
            print(f"DB: Attempting to {action_desc} for user {user_id}.")
            with conn:
                with conn.cursor() as cur:
                    cur.execute(insert_query, params)
                    print(f"DB: Operation '{action_desc}' complete for user {user_id}. Affected rows: {cur.rowcount}")
            return True
        except psycopg2.Error as db_error:
            print(f"\nDB Error during '{action_desc}' for user {user_id}: {db_error}")
            messagebox.showerror("Помилка Бази Даних", f"Не вдалося {('встановити' if status else 'зняти')} статус розробника:\n{db_error}")
            return False
        except Exception as e:
            print(f"\nDB Unexpected error during '{action_desc}' for user {user_id}: {e}")
            traceback.print_exc()
            messagebox.showerror("Неочікувана Помилка", f"Сталася неочікувана помилка під час {('встановлення' if status else 'зняття')} статусу:\n{e}")
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
        
          
    def fetch_all_studios(self, sort_by='name', sort_order='ASC'):
        conn = self.get_connection()
        if not conn:
            print("DB: No connection to fetch studios.")
            return None

        allowed_sort_columns = {'name', 'country', 'established_date'}
        if sort_by not in allowed_sort_columns:
            print(f"DB Warning: Invalid sort column '{sort_by}' for studios. Defaulting to 'name'.")
            sort_by = 'name'

        sort_order = sort_order.upper()
        if sort_order not in ('ASC', 'DESC'):
            print(f"DB Warning: Invalid sort order '{sort_order}'. Defaulting to 'ASC'.")
            sort_order = 'ASC'

        order_by_sql = sql.SQL("ORDER BY {sort_col} {sort_dir}").format(
            sort_col=sql.Identifier(sort_by),
            sort_dir=sql.SQL(sort_order)
        )

        base_query = sql.SQL("SELECT studio_id, name, logo, country FROM Studios")
        query = sql.SQL(" ").join([base_query, order_by_sql])

        print(f"DB: Fetching all studios sorted by {sort_by} {sort_order}...")
        try:
            studios_data = self.execute_query(query, fetch_all=True)

            if studios_data is None:
                print("DB: Failed to fetch studios (execute_query returned None)")
                return None
            elif not studios_data:
                print("DB: Fetched 0 studios.")
                return []
            else:
                print(f"DB: Fetched {len(studios_data)} studios.")
                columns = ['studio_id', 'name', 'logo', 'country']
                studios_list = [dict(zip(columns, row)) for row in studios_data]
                return studios_list
        except Exception as e:
            print(f"DB: Unexpected error fetching sorted studios: {e}")
            traceback.print_exc()
            return None

    def submit_studio_application(self, user_id, studio_id):
        conn = self.get_connection()
        if not conn:
            messagebox.showerror("Помилка Бази Даних", "Немає підключення до бази даних.")
            return False

        current_studio_id = self.get_developer_studio_id(user_id)
        if current_studio_id is not None:
            if current_studio_id == studio_id:
                messagebox.showinfo("Вже у студії", "Ви вже є учасником цієї студії.")
            else:
                messagebox.showwarning("Вже у студії", "Ви вже є учасником іншої студії.")
            return False

        query_check_pending = sql.SQL("SELECT 1 FROM StudioApplications WHERE user_id = %s AND status = 'Pending' LIMIT 1;")
        try:
            existing_pending_app = self.execute_query(query_check_pending, (user_id,), fetch_one=True)
            if existing_pending_app:
                print(f"DB: User {user_id} already has a pending application.")
                messagebox.showwarning("Заявка вже існує", "Ви вже маєте активну заявку до іншої студії, що очікує на розгляд. Дочекайтеся її обробки або скасуйте.")
                return False
        except Exception as e:
             print(f"DB: Error checking for existing pending applications for user {user_id}: {e}")
             messagebox.showerror("Помилка перевірки", "Не вдалося перевірити наявність активних заявок.")
             return False

        query_insert = sql.SQL("""
            INSERT INTO StudioApplications (user_id, studio_id, status)
            VALUES (%s, %s, %s)
            ON CONFLICT (user_id, studio_id) WHERE (status = 'Pending')
            DO NOTHING;
        """)
        params = (user_id, studio_id, 'Pending')

        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute(query_insert, params)
                    if cur.rowcount > 0:
                        print(f"DB: Application submitted successfully by user {user_id} for studio {studio_id}.")
                        return True
                    else:
                        print(f"DB: Pending application likely already exists for user {user_id}, studio {studio_id} (ON CONFLICT triggered).")
                        messagebox.showwarning("Заявка вже існує", "Ви вже подали заявку до цієї студії, яка очікує на розгляд.")
                        return False
        except psycopg2.Error as db_error:
            print(f"DB Error submitting application for user {user_id}, studio {studio_id}: {db_error}")
            messagebox.showerror("Помилка Бази Даних", f"Не вдалося подати заявку:\n{db_error}")
            return False
        except Exception as e:
            print(f"DB Unexpected error submitting application: {e}")
            traceback.print_exc()
            messagebox.showerror("Неочікувана Помилка", f"Сталася помилка під час подання заявки:\n{e}")
            return False
        
    def process_studio_application(self, application_id, new_status, admin_user_id):
        conn = self.get_connection()
        if not conn:
            messagebox.showerror("Помилка Бази Даних", "Немає підключення до бази даних.")
            return False

        if new_status not in ('Accepted', 'Rejected'):
            print(f"DB Error: Invalid new status '{new_status}' for application processing.")
            return False

        print(f"DB: Processing application {application_id} to status '{new_status}' by admin {admin_user_id}")

        studio_id = None
        applicant_user_id = None

        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT user_id, studio_id FROM StudioApplications
                        WHERE application_id = %s AND status = 'Pending' FOR UPDATE;
                    """, (application_id,))
                    app_data = cur.fetchone()
                    if not app_data:
                        print(f"DB: Application {application_id} not found or not pending.")
                        messagebox.showwarning("Помилка", "Заявку не знайдено або вона вже оброблена.", parent=self.store_window_ref if hasattr(self, 'store_window_ref') else None)
                        return False
                    applicant_user_id, studio_id = app_data

                    cur.execute("""
                        SELECT 1 FROM Developers
                        WHERE user_id = %s AND studio_id = %s AND role = 'Admin';
                    """, (admin_user_id, studio_id))
                    if cur.fetchone() is None:
                        print(f"DB: User {admin_user_id} is not authorized (not Admin) to process applications for studio {studio_id}.")
                        messagebox.showerror("Відмовлено в доступі", "Ви не маєте прав (Адміністратор) обробляти заявки для цієї студії.", parent=self.store_window_ref if hasattr(self, 'store_window_ref') else None)
                        conn.rollback()
                        return False

                    cur.execute("""
                        UPDATE StudioApplications
                        SET status = %s, reviewed_by = %s, review_date = CURRENT_TIMESTAMP
                        WHERE application_id = %s;
                    """, (new_status, admin_user_id, application_id))
                    if cur.rowcount == 0:
                        print(f"DB: Failed to update application {application_id} status.")
                        conn.rollback()
                        return False

                    if new_status == 'Accepted':
                        cur.execute("""
                            UPDATE Developers SET studio_id = %s, role = 'Member'
                            WHERE user_id = %s AND studio_id IS NULL;
                        """, (studio_id, applicant_user_id))
                        if cur.rowcount == 0:
                            print(f"DB Warning: Could not assign accepted user {applicant_user_id} to studio {studio_id}. User not found in Developers or already has a studio.")
                        else:
                             print(f"DB: User {applicant_user_id} successfully added to studio {studio_id} as Member.")

            print(f"DB: Application {application_id} processed successfully to status '{new_status}'.")
            return True

        except psycopg2.Error as db_error:
            print(f"DB Error processing application {application_id}: {db_error}")
            messagebox.showerror("Помилка Бази Даних", f"Не вдалося обробити заявку:\n{db_error}", parent=self.store_window_ref if hasattr(self, 'store_window_ref') else None)
            return False
        except Exception as e:
            print(f"DB Unexpected error processing application {application_id}: {e}")
            traceback.print_exc()
            messagebox.showerror("Неочікувана Помилка", f"Сталася помилка під час обробки заявки:\n{e}", parent=self.store_window_ref if hasattr(self, 'store_window_ref') else None)
            return False
    
    def fetch_pending_applications(self, studio_id, admin_user_id):
        print(f"DB: Fetching pending applications for studio {studio_id} by admin {admin_user_id}")
        role = self.check_developer_role(admin_user_id, studio_id)
        if role != 'Admin':
            print(f"DB: User {admin_user_id} is not an admin for studio {studio_id}. Role: {role}")
            return []

        query = sql.SQL("""
            SELECT sa.application_id, u.username, sa.application_date
            FROM StudioApplications sa
            JOIN Users u ON sa.user_id = u.user_id
            WHERE sa.studio_id = %s AND sa.status = 'Pending'
            ORDER BY sa.application_date ASC;
        """)
        try:
            results = self.execute_query(query, (studio_id,), fetch_all=True)
            if results is None: return None
            apps = [{'id': row[0], 'username': row[1], 'date': row[2]} for row in results]
            print(f"DB: Found {len(apps)} pending applications for studio {studio_id}.")
            return apps
        except Exception as e:
            print(f"DB: Error fetching pending applications for studio {studio_id}: {e}")
            traceback.print_exc()
            return None
          
    def get_developer_studio_id(self, user_id):
        query = "SELECT studio_id FROM Developers WHERE user_id = %s;"
        result = self.execute_query(query, (user_id,), fetch_one=True)
        return result[0] if result and result[0] is not None else None
          
    def check_developer_role(self, user_id, studio_id):
        query = "SELECT role FROM Developers WHERE user_id = %s AND studio_id = %s;"
        result = self.execute_query(query, (user_id, studio_id), fetch_one=True)
        return result[0] if result else None

          
    def get_pending_application_count(self, studio_id, admin_user_id):
        print(f"DB: Getting pending application count for studio {studio_id} by admin {admin_user_id}")
        role = self.check_developer_role(admin_user_id, studio_id)
        if role != 'Admin':
            print(f"DB: User {admin_user_id} is not an admin for studio {studio_id}. Role: {role}")
            return 0

        query = sql.SQL("SELECT COUNT(*) FROM StudioApplications WHERE studio_id = %s AND status = 'Pending';")
        try:
            result = self.execute_query(query, (studio_id,), fetch_one=True)
            count = result[0] if result else 0
            print(f"DB: Pending application count for studio {studio_id}: {count}")
            return count
        except Exception as e:
            print(f"DB: Error getting pending application count for studio {studio_id}: {e}")
            return 0

    def check_pending_application(self, user_id, studio_id):
        query = sql.SQL("""
            SELECT EXISTS (
                SELECT 1 FROM StudioApplications
                WHERE user_id = %s AND studio_id = %s AND status = 'Pending'
            );
        """)
        try:
            result = self.execute_query(query, (user_id, studio_id), fetch_one=True)
            exists = result[0] if result else False
            print(f"DB: Pending application check for user {user_id}, studio {studio_id}: {'Exists' if exists else 'Does not exist'}")
            return exists
        except Exception as e:
            print(f"DB: Error checking pending application for user {user_id}, studio {studio_id}: {e}")
            return False
    