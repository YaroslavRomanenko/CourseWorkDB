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
	registration_date TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_users_username ON Users(username);
CREATE INDEX idx_users_email ON Users(email);


SELECT * FROM Users;

/* ### Developers ### */

CREATE TABLE Developers (
	developer_id SERIAL PRIMARY KEY,
	user_id INTEGER UNIQUE NOT NULL,
	studio_id INTEGER NULL,
	contact_email VARCHAR(30) NULL,

	CONSTRAINT fk_developer_user
		FOREIGN KEY (user_id)
		REFERENCES Users (user_id)
		ON DELETE CASCADE,
		
	CONSTRAINT fk_developer_studio
		FOREIGN KEY (studio_id)
		REFERENCES Studios (studio_id)
		ON DELETE RESTRICT
);

SELECT * FROM Developers;

/* ### Games_Studios ### */

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
CREATE INDEX idx_gamestudios_game_id ON Game_Studios(game_id);
CREATE INDEX idx_gamestudios_studio_id ON Game_Studios(studio_id);

SELECT * FROM Game_Studios;

/* ### studio_role_type ### */

CREATE TYPE studio_role_type AS ENUM (
	'Developer',
    'Publisher'
);

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
CREATE INDEX idx_games_title ON Games(title);
CREATE INDEX idx_games_status ON Games(status);

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

CREATE TYPE purchase_status AS ENUM (
    'Pending',
    'Completed',
    'Failed',
    'Cancelled',
    'Refunded'
);

CREATE TABLE Purchases (
    purchase_id SERIAL PRIMARY KEY,
    user_id INT NOT NULL,
    purchase_date TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    total_amount DECIMAL(7, 2) NOT NULL DEFAULT 0.00,
    status purchase_status NOT NULL,

    CONSTRAINT fk_purchase_user
        FOREIGN KEY (user_id)
        REFERENCES Users (user_id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
);

CREATE INDEX idx_purchases_user_id ON Purchases(user_id);
CREATE INDEX idx_purchases_purchase_date ON Purchases(purchase_date);

SELECT * FROM Purchases

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

SELECT * FROM Purchases_Items

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
CREATE INDEX idx_gameplatforms_game_id ON Game_Platforms(game_id);
CREATE INDEX idx_gameplatforms_platform_id ON Game_Platforms(platform_id);

SELECT * FROM Game_Platforms;

CREATE TABLE Genres (
    genre_id SERIAL PRIMARY KEY,
    name VARCHAR(30) UNIQUE NOT NULL
);
CREATE INDEX idx_genres_name ON Genres(name);

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
CREATE INDEX idx_gamegenres_game_id ON Game_Genres(game_id);
CREATE INDEX idx_gamegenres_genre_id ON Game_Genres(genre_id);

SELECT * FROM Game_Genres;

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

CREATE INDEX idx_devgames_developer_id ON Developers_Games(developer_id);
CREATE INDEX idx_devgames_game_id ON Developers_Games(game_id);

SELECT * FROM Developers_Games;