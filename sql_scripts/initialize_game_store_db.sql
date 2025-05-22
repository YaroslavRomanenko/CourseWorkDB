/* ### Studios ### */

CREATE TABLE Studios (
	studio_id SERIAL PRIMARY KEY,
	name VARCHAR(50) NOT NULL,
	website_url VARCHAR(255) NULL,
	logo VARCHAR(100) NOT NULL,
	country VARCHAR(50) NOT NULL,
	description TEXT NULL,
	established_date DATE NOT NULL
);
CREATE INDEX idx_studios_name ON Studios(name);

SELECT * FROM Studios;

/* ### Users ### */

CREATE TABLE Users (
	user_id SERIAL PRIMARY KEY,
	username VARCHAR(20) UNIQUE NOT NULL,
	email VARCHAR(30) UNIQUE NOT NULL,
	password_hash VARCHAR(64) NOT NULL,
	registration_date TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
	balance DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
	is_app_admin BOOLEAN NOT NULL DEFAULT FALSE,
	is_banned BOOLEAN NOT NULL DEFAULT FALSE
);
CREATE INDEX idx_users_username ON Users(username);
CREATE INDEX idx_users_email ON Users(email);

SELECT * FROM Users;

/* ### Developers ### */
CREATE TYPE developer_role AS ENUM ('Member', 'Admin');

CREATE TABLE Developers (
	developer_id SERIAL PRIMARY KEY,
	user_id INTEGER UNIQUE NOT NULL,
	studio_id INTEGER NULL,
	contact_email VARCHAR(30) NULL,
	role developer_role NOT NULL DEFAULT 'Member',

	CONSTRAINT fk_developer_user
		FOREIGN KEY (user_id)
		REFERENCES Users (user_id)
		ON DELETE CASCADE,
		
	CONSTRAINT fk_developer_studio
		FOREIGN KEY (studio_id)
		REFERENCES Studios (studio_id)
		ON DELETE RESTRICT
);
CREATE INDEX idx_developers_studio_id ON Developers(studio_id);
CREATE INDEX idx_developers_role ON Developers(role);

SELECT * FROM Developers;

/* ### Games_Studios ### */

CREATE TYPE studio_role_type AS ENUM ('Developer', 'Publisher');

CREATE TABLE Game_Studios (
	game_id INT NOT NULL,
	studio_id INT NOT NULL,
	role studio_role_type NOT NULL,

	CONSTRAINT pk_game_studios PRIMARY KEY (game_id, studio_id, role),

	CONSTRAINT fk_gamestudios_game
		FOREIGN KEY (game_id)
		REFERENCES Games (game_id)
		ON DELETE CASCADE
		ON UPDATE CASCADE,

	CONSTRAINT fk_gamestudios_studio
		FOREIGN KEY (studio_id)
		REFERENCES Studios (studio_id)
		ON DELETE CASCADE
		ON UPDATE CASCADE
);
CREATE INDEX idx_developers_studio_id ON Developers(game_id);
CREATE INDEX idx_developers_studio_id ON Developers(studio_id);

SELECT * FROM Game_Studios;

/* ### game_status ### */

CREATE TYPE game_status AS ENUM (
	'Development',
	'Alpha',
	'Beta',
	'Early Access',
	'Released',
	'Cancelled',
	'On Hold'
);

/* ### Games ### */

CREATE TABLE Games (
	game_id SERIAL PRIMARY KEY,
	title VARCHAR(100) UNIQUE NOT NULL,
	description TEXT NULL,
	price DECIMAL(7, 2) NULL,
	release_date DATE NULL,
	image VARCHAR(100) NOT NULL,
	status game_status NOT NULL,
	created_at DATE NULL DEFAULT CURRENT_DATE,
	updated_at DATE NULL DEFAULT CURRENT_DATE
);
CREATE INDEX idx_games_status ON Games(status);
CREATE INDEX idx_games_price ON Games(price);

SELECT * FROM Games;

/* ### Developers_Games ### */

CREATE TABLE Developers_Games (
	developer_id INT NOT NULL,
	game_id INT NOT NULL,
	CONSTRAINT pk_developers_games PRIMARY KEY (developer_id, game_id),
	
	CONSTRAINT fk_devgames_developer
		FOREIGN KEY (developer_id)
		REFERENCES Developers (developer_id)
		ON DELETE CASCADE
		ON UPDATE CASCADE,

	CONSTRAINT fk_devgames_game
		FOREIGN KEY (game_id)
		REFERENCES Games (game_id)
		ON DELETE CASCADE
		ON UPDATE CASCADE
);

SELECT * FROM Developers_Games;

CREATE TYPE application_status AS ENUM ('Pending', 'Accepted', 'Rejected');
CREATE TABLE StudioApplications (
    application_id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    studio_id INTEGER NOT NULL,
    application_date TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    status application_status NOT NULL DEFAULT 'Pending',
    reviewed_by INTEGER NULL,
    review_date TIMESTAMPTZ NULL,

    CONSTRAINT fk_application_user
        FOREIGN KEY (user_id) REFERENCES Users (user_id) ON DELETE CASCADE,
    CONSTRAINT fk_application_studio
        FOREIGN KEY (studio_id) REFERENCES Studios (studio_id) ON DELETE CASCADE,
    CONSTRAINT fk_application_reviewer
        FOREIGN KEY (reviewed_by) REFERENCES Users (user_id) ON DELETE SET NULL
);
CREATE UNIQUE INDEX uq_pending_application_idx
ON StudioApplications (user_id, studio_id)
WHERE (status = 'Pending');

CREATE INDEX idx_studioapplications_user_id ON StudioApplications(user_id);
CREATE INDEX idx_studioapplications_studio_id ON StudioApplications(studio_id);
CREATE INDEX idx_studioapplications_status ON StudioApplications(status);

SELECT * FROM StudioApplications;

CREATE TYPE purchase_status AS ENUM (
    'Pending',
    'Completed',
    'Failed',
    'Cancelled',
    'Refunded'
);

CREATE TABLE Purchases (
    purchase_id SERIAL PRIMARY KEY,
    user_id INT NULL,
    purchase_date TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    total_amount DECIMAL(7, 2) NOT NULL DEFAULT 0.00,
    status purchase_status NOT NULL,

    CONSTRAINT fk_purchase_user
        FOREIGN KEY (user_id)
        REFERENCES Users (user_id)
        ON DELETE SET NULL
        ON UPDATE CASCADE
);
CREATE INDEX idx_purchases_user_id ON Purchases(user_id);
CREATE INDEX idx_purchases_purchase_date ON Purchases(purchase_date);

SELECT * FROM Purchases;

CREATE TABLE Purchases_Items (
    purchase_item_id SERIAL PRIMARY KEY,
    purchase_id INT NOT NULL,
    game_id INT NOT NULL,
    price_at_purchase DECIMAL(7, 2) NOT NULL,

    CONSTRAINT fk_purchaseitem_purchase
        FOREIGN KEY (purchase_id)
        REFERENCES Purchases (purchase_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    CONSTRAINT fk_purchaseitem_game
        FOREIGN KEY (game_id)
        REFERENCES Games (game_id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
);
CREATE INDEX idx_purchaseitems_purchase_id ON Purchases_Items(purchase_id);
CREATE INDEX idx_purchaseitems_game_id ON Purchases_Items(game_id);

SELECT * FROM Purchases_Items;

CREATE TABLE Reviews (
    review_id SERIAL PRIMARY KEY,
    user_id INT NOT NULL,
    game_id INT NOT NULL,
    review_text TEXT NULL,
    review_date TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_review_user
        FOREIGN KEY (user_id) REFERENCES Users (user_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CONSTRAINT fk_review_game
        FOREIGN KEY (game_id) REFERENCES Games (game_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);
CREATE INDEX idx_reviews_user_id ON Reviews(user_id);
CREATE INDEX idx_reviews_game_id ON Reviews(game_id);
CREATE INDEX idx_reviews_review_date ON Reviews(review_date);

SELECT * FROM Reviews;

CREATE TABLE ReviewComments (
    comment_id SERIAL PRIMARY KEY, 
    review_id INT NOT NULL,
    user_id INT NOT NULL,
    comment_text TEXT NOT NULL,
    comment_date TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
	
    CONSTRAINT fk_comment_review
        FOREIGN KEY (review_id) REFERENCES Reviews (review_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CONSTRAINT fk_comment_user
        FOREIGN KEY (user_id) REFERENCES Users (user_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);
CREATE INDEX idx_reviewcomments_review_id ON ReviewComments(review_id);
CREATE INDEX idx_reviewcomments_user_id ON ReviewComments(user_id);
CREATE INDEX idx_reviewcomments_comment_date ON ReviewComments(comment_date);

SELECT * FROM ReviewComments;

CREATE TABLE Platforms (
    platform_id SERIAL PRIMARY KEY,
    name VARCHAR(30) UNIQUE NOT NULL
);
CREATE INDEX idx_platforms_name ON Platforms(name);

SELECT * FROM Platforms;

CREATE TABLE Game_Platforms (
    game_id INT NOT NULL,
    platform_id INT NOT NULL,

    CONSTRAINT pk_game_platform PRIMARY KEY (game_id, platform_id),
	
    CONSTRAINT fk_gameplatform_game
        FOREIGN KEY (game_id) REFERENCES Games (game_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CONSTRAINT fk_gameplatform_platform
        FOREIGN KEY (platform_id) REFERENCES Platforms (platform_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

SELECT * FROM Game_Platforms;

CREATE TABLE Genres (
    genre_id SERIAL PRIMARY KEY,
    name VARCHAR(30) UNIQUE NOT NULL
);

SELECT * FROM Genres;

CREATE TABLE Game_Genres (
    game_id INT NOT NULL,
    genre_id INT NOT NULL,
	
    CONSTRAINT pk_game_genres PRIMARY KEY (game_id, genre_id),

    CONSTRAINT fk_gamegenre_game
        FOREIGN KEY (game_id) REFERENCES Games (game_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CONSTRAINT fk_gamegenre_genre
        FOREIGN KEY (genre_id) REFERENCES Genres (genre_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

SELECT * FROM Game_Genres;

CREATE OR REPLACE FUNCTION calculate_total_spent(p_user_id INT)
RETURNS DECIMAL(10, 2)
LANGUAGE plpgsql
AS $$
DECLARE
    total_spent DECIMAL(10, 2);
BEGIN
    SELECT COALESCE(SUM(total_amount), 0.00)
    INTO total_spent
    FROM Purchases
    WHERE user_id = p_user_id AND status = 'Completed';

    RETURN total_spent;
END;
$$;

CREATE OR REPLACE FUNCTION update_timestamp_function()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
   NEW.updated_at = NOW();
   RETURN NEW;
END;
$$;

CREATE TRIGGER update_games_updated_at_trigger
BEFORE UPDATE ON Games
FOR EACH ROW
EXECUTE FUNCTION update_timestamp_function();

CREATE TYPE notification_type AS ENUM (
    'developer_status_request'
);

CREATE TYPE notification_status AS ENUM (
    'pending',
    'approved',
    'rejected'
);

CREATE TABLE AdminNotifications (
    notification_id SERIAL PRIMARY KEY,
    user_id INT NULL,                            
    target_user_id INT NULL,                   
    notification_type notification_type NOT NULL,
    message TEXT NULL,                           
    status notification_status NOT NULL DEFAULT 'pending', 
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP, 
    reviewed_by_admin_id INT NULL,               
    reviewed_at TIMESTAMPTZ NULL,

    CONSTRAINT fk_notification_user
        FOREIGN KEY (user_id) REFERENCES Users (user_id) ON DELETE SET NULL,
    CONSTRAINT fk_notification_target_user
        FOREIGN KEY (target_user_id) REFERENCES Users (user_id) ON DELETE CASCADE,
    CONSTRAINT fk_notification_reviewed_by
        FOREIGN KEY (reviewed_by_admin_id) REFERENCES Users (user_id) ON DELETE SET NULL
);
CREATE INDEX idx_adminnotifications_status_type ON AdminNotifications(status, notification_type);
CREATE INDEX idx_adminnotifications_target_user_id ON AdminNotifications(target_user_id);

SELECT * FROM AdminNotifications;

SELECT 
    purchase_id, 
    user_id, 
    purchase_date, 
    total_amount, 
    status 
FROM Purchases
WHERE user_id = 3 AND status = 'Completed';