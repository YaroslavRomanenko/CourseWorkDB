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
                return None

            required_keys = {"host", "port", "dbname", "user", "password"}
            if not required_keys.issubset(config['database'].keys()):
                missing_keys = required_keys - config['database'].keys()
                print(f"Error: Keys {missing_keys} missing from 'database' section")
                return None

            print("Configuration loaded successfully!")
            return config['database']

        except json.JSONDecodeError:
            print(f"Error: Unable to parse JSON in '{filename}' file")
            return None
        except Exception as e:
            print(f"Unexpected error when loading configuration: {e}")
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
        query = "SELECT user_id, password_hash, is_app_admin FROM Users WHERE username = %s;"
        result = self.execute_query(query, (username,), fetch_one=True)

        if result:
            user_id, stored_hash, is_app_admin = result
            if bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8')):
                print(f"User {username} validated successfully. User ID: {user_id}, Is App Admin: {is_app_admin}")
                return user_id, is_app_admin
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
            return False

        try:
            if price_at_purchase is None:
                 final_price = decimal.Decimal('0.00')
            else:
                final_price = decimal.Decimal(str(price_at_purchase)).quantize(decimal.Decimal("0.01"))
        except (ValueError, TypeError, decimal.InvalidOperation) as e:
             print(f"Error: Invalid price format for purchase: {price_at_purchase} - {e}")
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
        """Fetches all comments for a specific review, ordered by date ascending"""
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
            messagebox.showerror("Помилка Бази Даних", "Немає підключення до бази даних.", parent=None)
            return False

        try:
            amount_decimal = decimal.Decimal(str(amount_to_add)).quantize(decimal.Decimal("0.01"))
            if amount_decimal <= 0:
                messagebox.showerror("Помилка Вводу", "Сума для нарахування повинна бути позитивною.", parent=None)
                print(f"DB Error: Amount to add must be positive ({amount_decimal}).")
                return False
        except (ValueError, TypeError, decimal.InvalidOperation) as e:
            messagebox.showerror("Помилка Вводу", f"Некоректний формат суми: '{amount_to_add}'.", parent=None)
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
                        messagebox.showerror("Помилка", f"Користувача з ID {user_id} не знайдено.", parent=None)
                        print(f"DB Error: User with user_id {user_id} not found when adding funds.")
                        return False
        except psycopg2.Error as db_error:
            messagebox.showerror("Помилка Бази Даних", f"Помилка під час нарахування коштів:\n{db_error}", parent=None)
            print(f"\nDB Error adding funds for user {user_id}: {db_error}")
            return False
        except Exception as e:
            messagebox.showerror("Неочікувана Помилка", f"Неочікувана помилка під час нарахування коштів:\n{e}", parent=None)
            print(f"\nDB Unexpected error adding funds for user {user_id}: {e}")
            traceback.print_exc()
            return False
        
    def check_developer_status(self, user_id):
        """Checks if a user exists in the Developers table"""
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

    def set_developer_status(self, user_id, status=True, contact_email=None, cursor=None):
        """Adds or removes a user from the Developers table. Can operate within an existing transaction if cursor is provided."""
        manage_connection = cursor is None
        conn = None
        if manage_connection:
            conn = self.get_connection()
            if not conn:
                messagebox.showerror("Помилка Бази Даних", "Немає активного підключення до бази даних.")
                return False
        else:
            pass

        try:
            if manage_connection:
                with conn:
                    with conn.cursor() as cur:
                        result = self._execute_set_developer_status_logic(cur, user_id, status, contact_email)
                        return result
            else:
                 return self._execute_set_developer_status_logic(cursor, user_id, status, contact_email)

        except psycopg2.Error as db_error:
            if manage_connection and conn and not conn.closed:
                pass
            action_desc = "ensure/update developer entry" if status else "remove developer status"
            print(f"\nDB Error during '{action_desc}' for user {user_id}: {db_error}")
            return False
        except Exception as e:
            if manage_connection and conn and not conn.closed:
                 pass
            action_desc = "ensure/update developer entry" if status else "remove developer status"
            print(f"\nDB Unexpected error during '{action_desc}' for user {user_id}: {e}")
            traceback.print_exc()
            return False
          
    def _execute_set_developer_status_logic(self, cur, user_id, status, contact_email):
        """Executes the actual SQL logic for setting developer status using the provided cursor."""
        if status:
            if not contact_email:
                 email_query = sql.SQL("SELECT email FROM Users WHERE user_id = %s;")
                 cur.execute(email_query, (user_id,))
                 user_info = cur.fetchone()
                 if user_info and user_info[0]:
                      contact_email = user_info[0]
                      print(f"DB: No contact email provided for becoming developer (user {user_id}). Using primary email: {contact_email}")
                 else:
                      print(f"DB Error: Cannot set developer status for user {user_id} without a contact email if status is True.")
                      return False 

            insert_query = sql.SQL("""
                INSERT INTO Developers (user_id, studio_id, contact_email)
                VALUES (%s, NULL, %s)
                ON CONFLICT (user_id) DO UPDATE SET contact_email = EXCLUDED.contact_email, studio_id = NULL, role = 'Member';
            """)
            params = (user_id, contact_email)
            action_desc = "ensure/update developer entry"
            current_query_to_execute = insert_query
        else:
            dev_studio_id = self.get_developer_studio_id(user_id)

            delete_query = sql.SQL("DELETE FROM Developers WHERE user_id = %s;")
            params = (user_id,)
            action_desc = "remove developer status"
            current_query_to_execute = delete_query

        print(f"DB: Attempting to {action_desc} for user {user_id} using provided cursor.")
        cur.execute(current_query_to_execute, params)
        print(f"DB: Operation '{action_desc}' complete for user {user_id}. Affected rows: {cur.rowcount}")
        return True
    
    def delete_user_account(self, user_id):
        """Deletes a user account and all related data via CASCADE constraints"""
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
                        return False
        except psycopg2.Error as db_error:
            print(f"\nDB: Error deleting user account {user_id}: {db_error}")
            return False
        except Exception as e:
            print(f"\nDB: Unexpected error deleting user account {user_id}: {e}")
            traceback.print_exc()
            return False
        
          
    def fetch_all_studios(self, sort_by='name', sort_order='ASC'):
        """Fetches a list of all studios, optionally sorted"""
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
        """Submits an application for a user to join a studio"""
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
                return False
        except Exception as e:
             print(f"DB: Error checking for existing pending applications for user {user_id}: {e}")
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
                        return False
        except psycopg2.Error as db_error:
            print(f"DB Error submitting application for user {user_id}, studio {studio_id}: {db_error}")
            return False
        except Exception as e:
            print(f"DB Unexpected error submitting application: {e}")
            traceback.print_exc()
            return False
        
    def process_studio_application(self, application_id, new_status, admin_user_id):
        """Processes a pending studio application"""
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
                        return False
                    applicant_user_id, studio_id = app_data

                    cur.execute("""
                        SELECT 1 FROM Developers
                        WHERE user_id = %s AND studio_id = %s AND role = 'Admin';
                    """, (admin_user_id, studio_id))
                    if cur.fetchone() is None:
                        print(f"DB: User {admin_user_id} is not authorized (not Admin) to process applications for studio {studio_id}.")
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
            return False
        except Exception as e:
            print(f"DB Unexpected error processing application {application_id}: {e}")
            traceback.print_exc()
            return False
    
    def fetch_pending_applications(self, studio_id, admin_user_id):
        """Fetches pending applications for a specific studio"""
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
        """Gets the studio_id associated with a developer user"""
        query = "SELECT studio_id FROM Developers WHERE user_id = %s;"
        result = self.execute_query(query, (user_id,), fetch_one=True)
        return result[0] if result and result[0] is not None else None
          
    def check_developer_role(self, user_id, studio_id):
        """Checks the role of a developer within a specific studio"""
        query = "SELECT role FROM Developers WHERE user_id = %s AND studio_id = %s;"
        result = self.execute_query(query, (user_id, studio_id), fetch_one=True)
        return result[0] if result else None

          
    def get_pending_application_count(self, studio_id, admin_user_id):
        """Gets the count of pending applications for a specific studio"""
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
        """Checks if a specific user has a pending application for a specific studio"""
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
        
    def check_game_edit_permission(self, user_id, game_id):
        """Checks if a user has permission to edit a specific game"""
        query = sql.SQL("""
            SELECT EXISTS (
                SELECT 1
                FROM Developers_Games dg
                JOIN Developers d ON dg.developer_id = d.developer_id
                WHERE d.user_id = %s AND dg.game_id = %s
            );
        """)
        try:
            result = self.execute_query(query, (user_id, game_id), fetch_one=True)
            can_edit = result[0] if result else False
            print(f"DB: Edit permission check (link exists) for user {user_id}, game {game_id}: {can_edit}")
            return can_edit
        except Exception as e:
            print(f"DB: Error checking game edit permission (link exists) for user {user_id}, game {game_id}: {e}")
            traceback.print_exc()
            return False
        
    def update_game_details(self, game_id, new_description=None, new_price=None, editor_user_id=None):
        """Updates the description and/or price for a specific game. Relies on DB trigger for updated_at.""" 
        conn = self.get_connection()
        if not conn:
            messagebox.showerror("Помилка Бази Даних", "Немає активного підключення до бази даних для оновлення гри.")
            return False

        if new_description is None and new_price is None:
            print("DB: No changes provided to update_game_details.")
            return True

        update_fields = []
        params = []

        if new_description is not None:
            update_fields.append(sql.SQL("description = %s"))
            params.append(new_description.strip())

        validated_price = None
        if new_price is not None:
            try:
                if isinstance(new_price, str) and new_price.strip() == '':
                     pass 
                else:
                    price_decimal = Decimal(str(new_price)).quantize(Decimal("0.01"))
                    if price_decimal < 0:
                        messagebox.showerror("Помилка Вводу", "Ціна не може бути від'ємною.", parent=None)
                        return False
                    validated_price = price_decimal
                    update_fields.append(sql.SQL("price = %s"))
                    params.append(validated_price)
            except (ValueError, TypeError, InvalidOperation) as e:
                print(f"DB Error: Invalid price format '{new_price}': {e}")
                return False
        params.append(game_id)

        if not update_fields:
            print("DB: No valid fields to update after validation.")
            return True

        set_clause = sql.SQL(", ").join(update_fields)
        query = sql.SQL("UPDATE Games SET {fields} WHERE game_id = %s").format(fields=set_clause)

        print(f"DB: Attempting to update game {game_id} by user {editor_user_id}.")
        print(f"DB: Query: {query.as_string(conn)}")
        print(f"DB: Params: {tuple(params)}")

        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute(query, tuple(params))
                    if cur.rowcount == 1:
                        print(f"DB: Successfully updated game {game_id} (trigger handled updated_at).")
                        return True
                    elif cur.rowcount == 0:
                        print(f"DB Warning: Game with ID {game_id} not found for update, or no actual changes made.")
                        return True
                    else:
                        print(f"DB Error: Unexpected rowcount ({cur.rowcount}) updating game {game_id}.")
                        conn.rollback()
                        return False

        except psycopg2.Error as db_error:
            print(f"\nDB Error updating game {game_id}: {db_error}")
            return False
        except Exception as e:
            print(f"\nDB Unexpected error updating game {game_id}: {e}")
            traceback.print_exc()
            return False
        
    def fetch_all_users_for_admin(self, search_term=None, sort_by='username', sort_order='ASC'):
        conn = self.get_connection()
        if not conn:
            print("DB: No connection to fetch users for admin.")
            return None

        allowed_sort_columns = {'user_id', 'username', 'email', 'registration_date', 'balance', 'owned_games_count', 'total_spent'}
        db_sort_key = sort_by
        if sort_by == 'total_spent':
             print("DB Warning: Sorting by calculated 'total_spent' might be slow or complex. Sorting by username instead for now.")
             db_sort_key = 'username'
        elif sort_by not in allowed_sort_columns:
            db_sort_key = 'username'

        sort_order_sql_literal = sort_order.upper()
        if sort_order_sql_literal not in ('ASC', 'DESC'):
            sort_order_sql_literal = 'ASC'

        sort_order_sql = sql.SQL(sort_order_sql_literal)

        base_query_parts = [
            sql.SQL("""
            SELECT
                u.user_id, u.username, u.email, u.registration_date, u.balance,
                u.is_app_admin, u.is_banned,
                EXISTS (SELECT 1 FROM Developers d WHERE d.user_id = u.user_id) as is_developer,
                (SELECT s.name FROM Studios s JOIN Developers d ON s.studio_id = d.studio_id WHERE d.user_id = u.user_id LIMIT 1) as developer_studio_name,
                (SELECT COUNT(DISTINCT pi.game_id)
                    FROM Purchases_Items pi
                    JOIN Purchases p ON pi.purchase_id = p.purchase_id
                    WHERE p.user_id = u.user_id AND p.status = 'Completed'
                ) as owned_games_count,
                calculate_total_spent(u.user_id) as total_spent
            FROM Users u
            """)
        ]
        params = []

        if search_term:
            base_query_parts.append(sql.SQL("WHERE u.username ILIKE %s OR u.email ILIKE %s"))
            like_pattern = f"%{search_term}%"
            params.extend([like_pattern, like_pattern])

        base_query_parts.append(sql.SQL("ORDER BY {sort_col} {sort_dir}").format(
            sort_col=sql.Identifier(db_sort_key),
            sort_dir=sort_order_sql
        ))

        if db_sort_key != 'user_id':
            base_query_parts.append(sql.SQL(", u.user_id {sort_dir}").format(sort_dir=sort_order_sql))

        query = sql.SQL(" ").join(base_query_parts)

        print(f"DB: Fetching all users for admin. Sort: {db_sort_key} {sort_order_sql_literal}. Search: '{search_term}'")
        try:
            users_data = self.execute_query(query, tuple(params) if params else None, fetch_all=True)
            if users_data is None:
                print("DB: Failed to fetch users for admin.")
                return None

            columns = ['user_id', 'username', 'email', 'registration_date', 'balance',
                       'is_app_admin', 'is_banned', 'is_developer',
                       'developer_studio_name', 'owned_games_count', 'total_spent']
            return [dict(zip(columns, row)) for row in users_data]
        except Exception as e:
            print(f"DB: Unexpected error fetching users for admin: {e}")
            traceback.print_exc()
            return None
        
    def set_user_ban_status(self, target_user_id, ban_status, admin_user_id):
        """Sets the ban status for a target user."""
        conn = self.get_connection()
        if not conn:
            messagebox.showerror("Помилка Бази Даних", "Немає підключення до бази даних.")
            return False
        
        query_check_target_admin = "SELECT is_app_admin FROM Users WHERE user_id = %s;"
        target_admin_status = self.execute_query(query_check_target_admin, (target_user_id,), fetch_one=True)

        if target_admin_status and target_admin_status[0] and target_user_id != admin_user_id:
            messagebox.showerror("Помилка", "Неможливо заблокувати іншого адміністратора додатку.", parent=None)
            return False
        if target_user_id == admin_user_id and ban_status:
             messagebox.showerror("Помилка", "Неможливо заблокувати самого себе.", parent=None)
             return False


        query = sql.SQL("UPDATE Users SET is_banned = %s WHERE user_id = %s;")
        params = (ban_status, target_user_id)

        try:
            print(f"DB: Admin {admin_user_id} attempting to set ban_status={ban_status} for user_id {target_user_id}")
            with conn:
                with conn.cursor() as cur:
                    cur.execute(query, params)
                    if cur.rowcount == 1:
                        print(f"DB: Successfully updated ban status for user_id {target_user_id}.")
                        return True
                    else:
                        print(f"DB Error: User with user_id {target_user_id} not found for ban status update.")
                        return False
        except psycopg2.Error as db_error:
            print(f"\nDB Error updating ban status for user {target_user_id}: {db_error}")
            return False
        except Exception as e:
            print(f"\nDB Unexpected error updating ban status for user {target_user_id}: {e}")
            traceback.print_exc()
            return False
        
    def fetch_all_users_for_admin(self, search_term=None, sort_by='username', sort_order='ASC'):
        conn = self.get_connection()
        if not conn:
            print("DB: No connection to fetch users for admin.")
            return None

        allowed_sort_columns = {'user_id', 'username', 'email', 'registration_date', 'balance', 'owned_games_count', 'total_spent'}
        db_sort_key = sort_by
        
        if sort_by == 'total_spent':
            pass 
        elif sort_by not in allowed_sort_columns:
            db_sort_key = 'username'
        
        sort_order_sql_literal = sort_order.upper()
        if sort_order_sql_literal not in ('ASC', 'DESC'):
            sort_order_sql_literal = 'ASC'
        
        sort_order_sql = sql.SQL(sort_order_sql_literal)

        base_query_parts = [
            sql.SQL("""
            SELECT
                u.user_id, u.username, u.email, u.registration_date, u.balance,
                u.is_app_admin, u.is_banned,
                EXISTS (SELECT 1 FROM Developers d WHERE d.user_id = u.user_id) as is_developer,
                (SELECT s.name FROM Studios s JOIN Developers d ON s.studio_id = d.studio_id WHERE d.user_id = u.user_id LIMIT 1) as developer_studio_name,
                (SELECT COUNT(DISTINCT pi.game_id)
                    FROM Purchases_Items pi
                    JOIN Purchases p ON pi.purchase_id = p.purchase_id
                    WHERE p.user_id = u.user_id AND p.status = 'Completed'
                ) as owned_games_count,
                calculate_total_spent(u.user_id) as total_spent
            FROM Users u
            """)
        ]
        params = []

        if search_term:
            base_query_parts.append(sql.SQL("WHERE u.username ILIKE %s OR u.email ILIKE %s"))
            like_pattern = f"%{search_term}%"
            params.extend([like_pattern, like_pattern])

        base_query_parts.append(sql.SQL("ORDER BY {sort_col} {sort_dir}").format(
            sort_col=sql.Identifier(db_sort_key), 
            sort_dir=sort_order_sql
        ))
        
        if db_sort_key != 'user_id':
            base_query_parts.append(sql.SQL(", u.user_id {sort_dir}").format(sort_dir=sort_order_sql))

        query = sql.SQL(" ").join(base_query_parts)

        print(f"DB: Fetching all users for admin (using calculate_total_spent). Sort: {db_sort_key} {sort_order_sql_literal}. Search: '{search_term}'")
        try:
            users_data_tuples = self.execute_query(query, tuple(params) if params else None, fetch_all=True)
            if users_data_tuples is None:
                print("DB: Failed to fetch users for admin.")
                return None
            
            columns = ['user_id', 'username', 'email', 'registration_date', 'balance',
                       'is_app_admin', 'is_banned', 'is_developer', 
                       'developer_studio_name', 'owned_games_count', 'total_spent']
            
            users_list_of_dicts = []
            for row_tuple in users_data_tuples:
                users_list_of_dicts.append(dict(zip(columns, row_tuple)))
            
            return users_list_of_dicts
        except Exception as e:
            print(f"DB: Unexpected error fetching users for admin: {e}")
            traceback.print_exc()
            return None
        
    def fetch_all_studios_for_admin(self, search_term=None, sort_by='name', sort_order='ASC'):
        conn = self.get_connection()
        if not conn:
            print("DB: No connection to fetch studios for admin.")
            return None

        allowed_sort_columns = {'studio_id', 'name', 'country', 'established_date', 'game_count', 'developer_count'}
        if sort_by not in allowed_sort_columns:
            sort_by = 'name'
        
        sort_order_sql_literal = sort_order.upper()
        if sort_order_sql_literal not in ('ASC', 'DESC'):
            sort_order_sql_literal = 'ASC'
        sort_order_sql = sql.SQL(sort_order_sql_literal)

        base_query_parts = [
            sql.SQL("""
            SELECT
                s.studio_id, s.name, s.logo, s.country, s.established_date,
                (SELECT COUNT(DISTINCT gs.game_id) FROM Game_Studios gs WHERE gs.studio_id = s.studio_id) as game_count,
                (SELECT COUNT(d.developer_id) FROM Developers d WHERE d.studio_id = s.studio_id) as developer_count
            FROM Studios s
            """)
        ]
        params = []

        if search_term:
            base_query_parts.append(sql.SQL("WHERE s.name ILIKE %s"))
            params.append(f"%{search_term}%")

        base_query_parts.append(sql.SQL("ORDER BY {sort_col} {sort_dir}").format(
            sort_col=sql.Identifier(sort_by),
            sort_dir=sort_order_sql
        ))
        if sort_by != 'studio_id':
            base_query_parts.append(sql.SQL(", s.studio_id {sort_dir}").format(sort_dir=sort_order_sql))


        query = sql.SQL(" ").join(base_query_parts)

        print(f"DB: Fetching all studios for admin. Sort: {sort_by} {sort_order_sql_literal}. Search: '{search_term}'")
        try:
            studios_data = self.execute_query(query, tuple(params) if params else None, fetch_all=True)
            if studios_data is None:
                print("DB: Failed to fetch studios for admin.")
                return None
            
            columns = ['studio_id', 'name', 'logo', 'country', 'established_date', 'game_count', 'developer_count']
            return [dict(zip(columns, row)) for row in studios_data]
        except Exception as e:
            print(f"DB: Unexpected error fetching studios for admin: {e}")
            traceback.print_exc()
            return None
        
    def fetch_all_games_for_admin(self, search_term=None, sort_by='title', sort_order='ASC'):
        conn = self.get_connection()
        if not conn:
            return None

        allowed_sort_columns = {'game_id', 'title', 'price', 'status', 'release_date', 'purchase_count'}
        if sort_by not in allowed_sort_columns:
            sort_by = 'title'
        
        sort_order_sql_literal = sort_order.upper()
        if sort_order_sql_literal not in ('ASC', 'DESC'):
            sort_order_sql_literal = 'ASC'
        sort_order_sql = sql.SQL(sort_order_sql_literal)

        base_query_parts = [
            sql.SQL("""
            SELECT
                g.game_id, g.title, g.price, g.status, g.release_date, g.image,
                (SELECT COUNT(pi.purchase_item_id)
                FROM Purchases_Items pi
                JOIN Purchases p ON pi.purchase_id = p.purchase_id
                WHERE pi.game_id = g.game_id AND p.status = 'Completed'
                ) AS purchase_count
            FROM games g
            """)
        ]
        params = []

        if search_term:
            base_query_parts.append(sql.SQL("WHERE g.title ILIKE %s"))
            params.append(f"%{search_term}%")
        
        order_by_clause = sql.SQL("ORDER BY {sort_col} {sort_dir}")
    
        if sort_by == 'price':
            nulls_placement = sql.SQL("NULLS FIRST") if sort_order_sql_literal == 'ASC' else sql.SQL("NULLS LAST")
            primary_order = order_by_clause.format(sort_col=sql.Identifier(sort_by), sort_dir=sort_order_sql)
            secondary_order_col = sql.Identifier('title')
            secondary_order_dir = sql.SQL('ASC')
            base_query_parts.append(sql.SQL(" ").join([primary_order, nulls_placement, sql.SQL(","), secondary_order_col, secondary_order_dir]))
        elif sort_by == 'game_id': 
            primary_order = order_by_clause.format(sort_col=sql.Identifier(sort_by), sort_dir=sort_order_sql)
            base_query_parts.append(primary_order)
        else: 
            primary_order = order_by_clause.format(sort_col=sql.Identifier(sort_by), sort_dir=sort_order_sql)
            secondary_order_col = sql.Identifier('game_id')
            secondary_order_dir = sql.SQL('ASC') 
            base_query_parts.append(sql.SQL(" ").join([primary_order, sql.SQL(","), secondary_order_col, secondary_order_dir]))

        query = sql.SQL(" ").join(base_query_parts)
        print(f"DB: Fetching all games for admin. Sort: {sort_by} {sort_order_sql_literal}. Search: '{search_term}'")
        
        try:
            games_data = self.execute_query(query, tuple(params) if params else None, fetch_all=True)
            if games_data is None: return None
            
            columns = ['game_id', 'title', 'price', 'status', 'release_date', 'image', 'purchase_count']
            return [dict(zip(columns, row)) for row in games_data]
        except Exception as e:
            print(f"DB: Unexpected error fetching games for admin: {e}")
            traceback.print_exc()
            return None
    
    def process_developer_status_request(self, notification_id, admin_user_id, approve=True):
        conn = self.get_connection()
        if not conn:
            messagebox.showerror("Помилка", "Немає підключення до бази даних.")
            return False

        target_user_id = None
        contact_email_from_request = None
        success_flag = False

        try:
            with conn:
                with conn.cursor() as cur:
                    query_get_request = """
                        SELECT target_user_id, message FROM AdminNotifications
                        WHERE notification_id = %s AND status = 'pending' AND notification_type = 'developer_status_request'
                        FOR UPDATE;
                    """
                    cur.execute(query_get_request, (notification_id,))
                    request_details = cur.fetchone()

                    if not request_details:
                        messagebox.showerror("Помилка", "Запит не знайдено або вже оброблено.", parent=None)
                        return False

                    target_user_id, contact_email_from_request = request_details
                    new_status = 'approved' if approve else 'rejected'
                    
                    if approve:
                        set_status_success = self.set_developer_status(
                            target_user_id,
                            status=True,
                            contact_email=contact_email_from_request,
                            cursor=cur 
                        )
                        if not set_status_success:
                            print(f"DB: Failed to set developer status for user {target_user_id} during request approval (inside transaction).")
                            conn.rollback() 
                            messagebox.showerror("Помилка", "Не вдалося оновити статус розробника для користувача.", parent=None)
                            return False
                        
                    query_update_notification = sql.SQL("""
                        UPDATE AdminNotifications
                        SET status = %s, reviewed_by_admin_id = %s, reviewed_at = CURRENT_TIMESTAMP
                        WHERE notification_id = %s;
                    """)
                    params_update = (new_status, admin_user_id, notification_id)

                    cur.execute(query_update_notification, params_update)
                    if cur.rowcount != 1:
                        print(f"DB: Failed to update notification status for ID {notification_id} (inside transaction).")
                        conn.rollback()
                        messagebox.showerror("Помилка", "Не вдалося оновити статус сповіщення.", parent=None)
                        return False

            success_flag = True
            print(f"DB: Admin {admin_user_id} processed developer_status_request {notification_id} to '{new_status}' for user {target_user_id}.")

        except psycopg2.Error as db_error:
             print(f"DB: Transaction error processing developer status request {notification_id}: {db_error}")
             messagebox.showerror("Помилка Транзакції", f"Помилка при обробці запиту: {db_error}", parent=None)
             success_flag = False
        except Exception as e:
            print(f"DB: Unexpected transaction error processing developer status request {notification_id}: {e}")
            traceback.print_exc()
            messagebox.showerror("Неочікувана Помилка", f"Помилка при обробці запиту: {e}", parent=None)
            success_flag = False

        return success_flag
    
    def create_developer_status_request(self, user_id, contact_email_for_request):
        conn = self.get_connection()
        if not conn:
            messagebox.showerror("Помилка", "Немає підключення до бази даних.")
            return False

        if self.check_developer_status(user_id):
            messagebox.showinfo("Інформація", "Ви вже є розробником.", parent=None)
            return False

        if self.has_pending_developer_status_request(user_id):
            messagebox.showinfo("Інформація", "У вас вже є активний запит на отримання статусу розробника, що очікує на розгляд.", parent=None)
            return False

        query = sql.SQL("""
            INSERT INTO AdminNotifications (user_id, target_user_id, notification_type, message, status)
            VALUES (%s, %s, %s, %s, %s) RETURNING notification_id;
        """)
        params = (user_id, user_id, 'developer_status_request', contact_email_for_request, 'pending')
        try:
            result = self.execute_query(query, params, fetch_one=True)
            if result and result[0]:
                print(f"DB: Created developer status request with ID: {result[0]} for user {user_id}")
                return True
            else:
                print(f"DB: Failed to create developer status request for user {user_id}")
                return False
        except Exception as e:
            print(f"DB: Error creating developer status request for user {user_id}: {e}")
            return False
    
    def has_pending_developer_status_request(self, user_id):
        conn = self.get_connection()
        if not conn:
            print("DB: Cannot check pending developer status request: No active database connection")
            return False

        query = sql.SQL("""
            SELECT EXISTS (
                SELECT 1
                FROM AdminNotifications
                WHERE user_id = %s
                  AND notification_type = 'developer_status_request'
                  AND status = 'pending'
            );
        """)
        params = (user_id,)
        print(f"DB: Checking for pending developer_status_request for user_id {user_id}...")
        try:
            result = self.execute_query(query, params, fetch_one=True)
            if result:
                has_pending = result[0]
                print(f"DB: User {user_id} has pending developer_status_request: {has_pending}")
                return has_pending
            else:
                print(f"DB Warning: Failed to execute pending developer_status_request check for user {user_id}.")
                return False
        except Exception as e:
            print(f"DB: Error checking pending developer_status_request for user {user_id}: {e}")
            traceback.print_exc()
            return False

    def fetch_pending_admin_notifications(self, notification_type_filter=None, sort_by='created_at', sort_order='ASC'):
        conn = self.get_connection()
        if not conn: return None

        allowed_sort_columns = {'notification_id', 'created_at', 'notification_type', 'user_id', 'target_user_id'}
        if sort_by not in allowed_sort_columns:
            sort_by = 'created_at'

        sort_order_sql_literal = sort_order.upper()
        if sort_order_sql_literal not in ('ASC', 'DESC'):
            sort_order_sql_literal = 'ASC'
        sort_order_sql = sql.SQL(sort_order_sql_literal)

        query_parts = [
            sql.SQL("""
            SELECT an.notification_id, an.user_id, u.username as initiator_username,
                   an.target_user_id, tu.username as target_username,
                   an.notification_type, an.message, an.status, an.created_at
            FROM AdminNotifications an
            LEFT JOIN Users u ON an.user_id = u.user_id
            LEFT JOIN Users tu ON an.target_user_id = tu.user_id
            WHERE an.status = 'pending'
            """)
        ]
        params = []

        if notification_type_filter:
            query_parts.append(sql.SQL("AND an.notification_type = %s"))
            params.append(notification_type_filter)

        query_parts.append(sql.SQL("ORDER BY {sort_col} {sort_dir}").format(
            sort_col=sql.Identifier(sort_by), sort_dir=sort_order_sql
        ))

        query = sql.SQL(" ").join(query_parts)

        try:
            notifications_data = self.execute_query(query, tuple(params) if params else None, fetch_all=True)
            if notifications_data is None: return None

            columns = ['notification_id', 'user_id', 'initiator_username',
                       'target_user_id', 'target_username',
                       'notification_type', 'message', 'status', 'created_at']
            return [dict(zip(columns, row)) for row in notifications_data]
        except Exception as e:
            print(f"DB: Error fetching pending admin notifications: {e}")
            traceback.print_exc()
            return None
        
    def get_user_total_spent(self, user_id):
        conn = self.get_connection()
        if not conn:
            print("DB: Cannot get total spent: No active database connection")
            return None

        query = sql.SQL("SELECT calculate_total_spent(%s);")
        params = (user_id,)

        print(f"DB: Calculating total spent for user_id {user_id} using SQL function...")
        try:
            result = self.execute_query(query, params, fetch_one=True)
            if result and result[0] is not None:
                total_spent = Decimal(str(result[0])).quantize(Decimal("0.01"))
                print(f"DB: Total spent for user {user_id}: {total_spent}")
                return total_spent
            else:
                print(f"DB: Total spent for user {user_id}: 0.00 (or error occurred)")
                return Decimal('0.00')
        except (InvalidOperation, TypeError) as e:
            print(f"DB: Error converting result to Decimal for user {user_id}: {e}")
            return Decimal('0.00')
        except Exception as e:
            print(f"DB: Unexpected error getting total spent for user {user_id}: {e}")
            traceback.print_exc()
            return None
        
    def get_developer_studio_details(self, user_id):
        query = """
            SELECT d.studio_id, s.name
            FROM Developers d
            JOIN Studios s ON d.studio_id = s.studio_id
            WHERE d.user_id = %s AND d.studio_id IS NOT NULL;
        """
        result = self.execute_query(query, (user_id,), fetch_one=True)
        if result:
            return {'studio_id': result[0], 'studio_name': result[1]}
        return None

    def leave_studio(self, user_id):
        conn = self.get_connection()
        if not conn:
            messagebox.showerror("Помилка Бази Даних", "Немає підключення до бази даних.")
            return False

        dev_info_query = "SELECT studio_id, role FROM Developers WHERE user_id = %s AND studio_id IS NOT NULL;"
        dev_info = self.execute_query(dev_info_query, (user_id,), fetch_one=True)

        if not dev_info:
            messagebox.showinfo("Інформація", "Ви не є учасником жодної студії.", parent=None)
            return False

        studio_id, role = dev_info

        if role == 'Admin':
            other_admins_query = "SELECT COUNT(*) FROM Developers WHERE studio_id = %s AND role = 'Admin' AND user_id != %s;"
            other_admins_count = self.execute_query(other_admins_query, (studio_id, user_id), fetch_one=True)

            if other_admins_count and other_admins_count[0] == 0:
                other_members_query = "SELECT COUNT(*) FROM Developers WHERE studio_id = %s AND role = 'Member';"
                other_members_count = self.execute_query(other_members_query, (studio_id,), fetch_one=True)
                if other_members_count and other_members_count[0] > 0:
                    messagebox.showerror("Дія неможлива",
                                         "Ви єдиний адміністратор у студії, де є інші учасники.\n",
                                         parent=None)
                    return False

        query = sql.SQL("""
            UPDATE Developers
            SET studio_id = NULL, role = 'Member'
            WHERE user_id = %s AND studio_id IS NOT NULL;
        """)

        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute(query, (user_id,))
                    if cur.rowcount > 0:
                        print(f"DB: User {user_id} successfully left studio {studio_id}.")
                        return True
                    else:
                        print(f"DB: User {user_id} was not part of a studio or update failed.")
                        return False
        except psycopg2.Error as db_error:
            print(f"DB Error when user {user_id} trying to leave studio: {db_error}")
            return False
        except Exception as e:
            print(f"DB Unexpected error when user {user_id} trying to leave studio: {e}")
            traceback.print_exc()
            return False