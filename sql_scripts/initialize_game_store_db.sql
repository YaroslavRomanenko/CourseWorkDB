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

-- SELECT * FROM Studios;

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


-- SELECT * FROM Users;

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


-- SELECT * FROM Developers;

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

/* ### studio_role_type ### */

CREATE TYPE studio_role_type AS ENUM (
	'Developer',
    'Publisher',
    'Co-Developer',
    'Porting Studio',
    'Support Studio',
    'Other'
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

-- SELECT * FROM Games;

/* SELECT game_id, title, created_at, updated_at
FROM Games
WHERE created_at IS NULL AND updated_at IS NULL; */

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
