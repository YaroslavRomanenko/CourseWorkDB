--- Deletes all data in database ---
TRUNCATE TABLE
    "studios",
    "users",
    "developers",
    "game_studios", 
    "games",
    "developers_games",
    "reviews",
    "reviewcomments",
    "game_platforms",
    "studioapplications",
    "purchases",
    "purchases_items",
    "platforms",
    "genres",
    "game_genres"
RESTART IDENTITY CASCADE;

--- Inserting Users Data ---
INSERT INTO Users (username, email, password_hash, registration_date) VALUES
    --- Terraria ---
    ('Redigit', 'redigit@gmail.com', 'hashed_password_for_Redigit', '2009-06-17'),
    ('Cenx', 'Cenx@gmail.com', 'hashed_password_for_Cenx', '2013-08-05'),
    ('Loki', 'Loki@gmail.com', 'hashed_password_for_Loki', '2012-07-02'),
    ('FoodBarbarian', 'FoodBarbarian@gmail.com', 'hashed_password_for_FoodBarbarian', '2014-09-03'),

    --- Don't Starve Together ---
    ('MatthewMarteinsson', 'MatthewMarteinsson@gmail.com', 'hashed_password_for_MatthewMarteinsson', '2011-03-26'),
    ('BryceDoig', 'BryceDoig@gmail.com', 'hashed_password_for_BryceDoig', '2013-05-11'),
    ('AlexSavin', 'AlexSavin@gmail.com', 'hashed_password_for_AlexSavin', '2014-03-21'),

    --- Astroneer ---
    ('AaronBiddlecom', 'AaronBiddlecom@gmail.com', 'hashed_password_for_AaronBiddlecom', '2011-11-01'),
    ('AdamBromell', 'AdamBromell@gmail.com', 'hashed_password_for_AdamBromell', '2012-12-16'),
    ('AndreMaguire', 'AndreMaguire@gmail.com', 'hashed_password_for_AndreMaguire', '2011-09-28'),

    --- Factorio ---
    ('MichalKovarik', 'MichalKovarik@gmail.com', 'hashed_password_for_MichalKovarik', '2012-02-09'),
    ('Tomax', 'Tomax@gmail.com', 'hashed_password_for_Tomax', '2013-05-30'),
    ('DanStevens', 'DanStevens@gmail.com', 'hashed_password_for_DanStevens', '2014-01-07'),

    --- Stardew Valley ---
    ('EricBarone', 'EricBarone@gmail.com', 'hashed_password_for_EricBarone', '2015-02-15'),

    --- Sid Meier's Civilization VI ---
    ('EdBeach', 'EdBeach@gmail.com', 'hashed_password_for_EdBeach', '2010-08-09'),
    ('DennisShirk', 'DennisShirk@gmail.com', 'hashed_password_for_DennisShirk', '2010-09-14'),
    ('AndrewFrederiksen', 'AndrewFrederiksen@gmail.com', 'hashed_password_for_AndrewFrederiksen', '2010-09-21'),
    ('ChristophHartmann', 'ChristophHartmann@gmail.com', 'hashed_password_for_ChristophHartmann', '2008-04-12'),
    ('JohnChowanec', 'JohnChowanec@gmail.com', 'hashed_password_for_JohnChowanec', '2008-05-03'),
    ('MelissaMiller', 'MelissaMiller@gmail.com', 'hashed_password_for_MelissaMiller', '2008-07-06'),

    --- Marvel Rivals ---
    ('ThaddeusSasser', 'ThaddeusSasser@gmail.com', 'hashed_password_for_ThaddeusSasser', '2013-05-15'),
    ('James', 'James@gmail.com', 'hashed_password_for_James', '2017-07-05'),
    ('GuangyunChen', 'GuangyunChen@gmail.com', 'hashed_password_for_GuangyunChen', '2018-10-29'),

    --- Hades II ---
    ('WillTurnbull', 'WillTurnbull@gmail.com', 'hashed_password_for_WillTurnbull', '2015-01-19'),
    ('AmirRao', 'AmirRao@gmail.com', 'hashed_password_for_AmirRao', '2015-04-02'),
    ('GregKasavin', 'GregKasavin@gmail.com', 'hashed_password_for_GregKasavin', '2016-01-04'),

    -- --- Project Odyssey ---
    ('DanHay', 'DanHay@gmail.com', 'hashed_password_for_DanHay', '2011-01-10'),
    ('RimaBrek', 'RimaBrek@gmail.com', 'hashed_password_for_RimaBrek', '2011-03-14'),
    ('ClementMarcou', 'ClementMarcou@gmail.com', 'hashed_password_for_ClementMarcou', '2011-05-09'),

    --- The Elder Scrolls VI ---
    ('CraigLafferty', 'CraigLafferty@gmail.com', 'hashed_password_for_CraigLafferty', '2009-10-24'),
    ('MarkLampert', 'MarkLampert@gmail.com', 'hashed_password_for_MarkLampert', '2008-09-11'),
    ('AshleyCheng', 'AshleyCheng@gmail.com', 'hashed_password_for_AshleyCheng', '2010-12-27'),

    --- Star citizen ---
    ('ChrisRoberts', 'ChrisRoberts@gmail.com', 'hashed_password_for_ChrisRoberts', '2014-06-13'),
    ('PedroCamacho', 'PedroCamacho@gmail.com', 'hashed_password_for_PedroCamacho', '2015-02-18'),

    --- Deep down ---
    ('KenzoTsujimoto', 'KenzoTsujimoto@gmail.com', 'hashed_password_for_KenzoTsujimoto', '2009-01-09'),
    ('TokuroFujiwara', 'TokuroFujiwara@gmail.com', 'hashed_password_for_TokuroFujiwara', '2010-08-07'),

    --- Hearts of Iron IV ---
    ('JohanAndersson', 'JohanAndersson@gmail.com', 'hashed_password_for_JohanAndersson', '2015-03-04'),
    ('DanLind', 'DanLind@gmail.com', 'hashed_password_for_DanLind', '2015-06-05'),
    ('LindaKiby', 'LindaKiby@gmail.com', 'hashed_password_for_LindaKiby', '2014-03-12'),

    --- Geometry Dash ---
    ('RobTop', 'RobTop@gmail.com', 'hashed_password_for_RobTop', '2011-04-18');

--- Inserting Studios Data ---
INSERT INTO Studios (name, website_url, logo, country, description, established_date) VALUES
    --- Terraria ---
    ('Re-Logic', 'https://re-logic.com/', 're-logic_icon_1.png', 'United States', 'Best known for the Terraria franchise - the revolutionary 2D Sandbox Adventure that has entertained millions of gamers worldwide - Re-Logic seeks to showcase and evolve the limits of what Indie gaming can be!', '2011-01-24'),

    --- Don't Starve Together ---
    ('Klei', 'https://www.klei.com/', 'klei_icon_2.jpg', 'Canada', 'It Rhymes With Play', '2005-07-01'),

    --- Astroneer ---
    ('System Era Softworks', 'https://www.systemera.net/', 'system_era_softworks_icon_3.png', 'United States', 'System Era Softworks is a small development studio led by veteran game developers headquartered in Seattle, Washington. We are currently working on our first game, Astroneer.', '2014-03-07'),

    --- Factorio ---
    ('Wube Software', NULL, 'wube_software_icon_4.jpg', 'Czech Republic', 'Wube Software is a team of passionate professionals dedicated to creating exceptional games.', '2014-09-03'),

    --- Stardew Valley ---
    ('ConcernedApe', NULL, 'concernedape_icon_5.jpg', 'United States', 'ConcernedApe is the moniker of Eric Barone, a solo game developer based in Seattle, WA.', '2012-05-05'),

    --- Sid Meier's Civilization VI ---
    ('Firaxis Games', 'https://firaxis.com/', 'firaxis_games_icon_6.jpg', 'United States', 'Firaxis Games is a world-renowned game development studio with an unwavering mission to "build games that stand the test of time".', '1996-05-12'),
    ('2K', 'https://2k.com/', '2k_icon_7.jpg', 'United States', '2K develops and publishes critically-acclaimed franchises such as BioShock, Borderlands, Sid Meier’s Civilization, XCOM, WWE 2K, and NBA 2K.', '2005-01-25'),

    --- Marvel Rivals ---
    ('NetEaseGames', 'https://www.neteasegames.com/', 'net_ease_games_icon_8.png', 'China', 'NetEase Games is the gaming division of NetEase, Inc., a major Chinese tech company. It focuses on developing and publishing video games across various platforms, including mobile, PC, and consoles.', '2001-09-08'),

    --- Hades II ---
    ('Supergiant Games', 'https://www.supergiantgames.com/', 'supergiant_games_icon_9.jpg', 'United States', 'We make games that spark your imagination like the games you played as a kid.', '2009-07-27'),

    --- Project Odyssey ---
    ('Blizzard Entertainment', 'https://www.blizzard.com/en-us/', 'blizzard_entertainment_icon_10.jpg', 'United States', 'Dedicated to creating the most epic entertainment experiences... ever.', '1991-02-08'),

    --- The Elder Scrolls VI ---
    ('Bethesda Softworks', 'https://bethesda.net/en/dashboard', 'bethesda_softworks_icon_11.png', 'United States', 'Bethesda Softworks is an award-winning development team renowned worldwide for its groundbreaking work on the The Elder Scrolls and Fallout series.', '1986-06-28'),

    --- Star citizen ---
    ('Cloud Imperium Games Corporation', 'https://cloudimperiumgames.com/', 'cloud_imperium_games_corporation_icon_12.jpg', 'United States', 'We never settle and we''re never daunted.', '2012-03-17'), -- Зверніть увагу на подвійні апострофи в we''re

    --- Deep down ---
    ('Capcom', 'https://www.capcom.com/', 'capcom_icon_13.jpg', 'Japan', 'Capcom began in Japan in 1979 as a manufacturer and distributor of electronic game machines.', '1979-09-21'),

    --- Hearts of Iron IV ---
    ('Paradox Interactive', 'https://www.paradoxinteractive.com/', 'paradox_interactive_icon_14.jpg', 'Sweden', 'We Create the Games. You Create the Stories.', '1999-01-04'),

    --- Geometry Dash ---
    ('RobTop Games', 'https://www.robtopgames.com/', 'robtop_games_icon_15.jpg', 'Sweden', 'I have created the mobile games Rune, Boomlings, Boomlings MatchUp, Memory Mastermind, Forlorn', '2012-11-05');

--- Inserting Developers Data ---

INSERT INTO Developers (user_id, studio_id, contact_email, role) VALUES
    --- Terraria ---
    (1, 1, 'redigit@gmail.com', 'Admin'),
    (2, 1, 'Cenx@gmail.com', 'Member'),
    (3, 1, 'Loki@gmail.com', 'Member'),
    (4, 1, 'FoodBarbarian@gmail.com', 'Member'),

    --- Don't Starve Together ---
    (5, 2, 'MatthewMarteinsson@gmail.com', 'Admin'),
    (6, 2, 'BryceDoig@gmail.com', 'Member'),
    (7, 2, 'AlexSavin@gmail.com', 'Member'),

    --- Astroneer ---
    (8, 3, 'AaronBiddlecom@gmail.com', 'Admin'),
    (9, 3, 'AdamBromell@gmail.com', 'Member'),
    (10, 3, 'AndreMaguire@gmail.com', 'Member'),

    --- Factorio ---
    (11, 4, 'MichalKovarik@gmail.com', 'Admin'),
    (12, 4, 'Tomax@gmail.com', 'Member'),
    (13, 4, 'DanStevens@gmail.com', 'Member'),

    --- Stardew Valley ---
    (14, 5, 'EricBarone@gmail.com', 'Admin'),

    --- Sid Meier's Civilization VI ---
	
    --- Firaxis Games ---
    (15, 6, 'EdBeach@gmail.com', 'Admin'),
    (16, 6, 'DennisShirk@gmail.com', 'Member'),
    (17, 6, 'AndrewFrederiksen@gmail.com', 'Member'),
    --- 2K ---
    (18, 7, 'ChristophHartmann@gmail.com', 'Admin'),
    (19, 7, 'JohnChowanec@gmail.com', 'Member'),
    (20, 7, 'MelissaMiller@gmail.com', 'Member'),

    --- Marvel Rivals ---
    (21, 8, 'ThaddeusSasser@gmail.com', 'Admin'),
    (22, 8, 'James@gmail.com', 'Member'),
    (23, 8, 'GuangyunChen@gmail.com', 'Member'),

    -- --- Hades II (Studio ID: 9) ---
    (24, 9, 'WillTurnbull@gmail.com', 'Admin'),
    (25, 9, 'AmirRao@gmail.com', 'Member'),
    (26, 9, 'GregKasavin@gmail.com', 'Member'),

    --- Project Odyssey ---
    (27, 10, 'DanHay@gmail.com', 'Admin'),
    (28, 10, 'RimaBrek@gmail.com', 'Member'),
    (29, 10, 'ClementMarcou@gmail.com', 'Member'),

    --- The Elder Scrolls VI ---
    (30, 11, 'CraigLafferty@gmail.com', 'Admin'),
    (31, 11, 'MarkLampert@gmail.com', 'Member'),
    (32, 11, 'AshleyCheng@gmail.com', 'Member'),

    --- Star citizen ---
    (33, 12, 'ChrisRoberts@gmail.com', 'Admin'),
    (34, 12, 'PedroCamacho@gmail.com', 'Member'),

    --- Deep down ---
    (35, 13, 'KenzoTsujimoto@gmail.com', 'Admin'),
    (36, 13, 'TokuroFujiwara@gmail.com', 'Member'),

    --- Hearts of Iron IV ---
    (37, 14, 'JohanAndersson@gmail.com', 'Admin'),
    (38, 14, 'DanLind@gmail.com', 'Member'),
    (39, 14, 'LindaKiby@gmail.com', 'Member'),

    --- Geometry Dash ---
    (40, 15, 'RobTop@gmail.com', 'Admin');


--- Inserting Games Data ---
INSERT INTO Games (title, description, price, release_date, image, status, created_at, updated_at) VALUES
    --- Terraria ---
    ('Terraria', 'Dig, fight, explore, build! Nothing is impossible in this action-packed adventure game.', 225.00, '2011-05-16', 'terraria_icon_1.png', 'Released', '2011-01-03', '2025-03-27'),

    --- Don't Starve Together ---
    ('Don''t Starve Together', 'Fight, Farm, Build and Explore Together in the standalone multiplayer expansion to the uncompromising wilderness survival game, Don''t Starve.', 229.00, '2016-04-21', 'don''t_starve_together_icon_2.jpg', 'Released', '2014-12-15', '2025-04-17'),

    --- Astroneer ---
    ('Astroneer', 'Interact with strange new worlds in a unique and tactile way, molding the environment itself as if it were clay in your hands.', 600.00, '2019-02-06', 'astroneer_icon_3.jpg', 'Released', '2016-12-16', '2025-04-02'),

    --- Factorio ---
    ('Factorio', 'Factorio is a game about building and creating automated factories to produce items of increasing complexity, within an infinite 2D world.', 300.00, '2020-08-14', 'factorio_icon_4.png', 'Released', '2012-06-22', '2025-03-31'),

    --- Stardew Valley ---
    ('Stardew Valley', 'You''ve inherited your grandfather''s old farm plot in Stardew Valley.', 229.00, '2016-02-26', 'stardew_valley_icon_5.jpg', 'Released', '2011-11-29', '2024-12-20'),

    --- Sid Meier''s Civilization VI ---
    ('Sid Meier''s Civilization VI', 'Expand your empire, advance your culture and go head-to-head against history’s greatest leaders.', 525.00, '2016-10-21', 'sid_meier''s_civilization_vi_icon_6.jpg', 'Released', '2014-05-03', '2025-01-15'),

    --- Marvel Rivals ---
    ('Marvel Rivals', 'Marvel Rivals is a Super Hero Team-Based PVP Shooter! Assemble an all-star Marvel squad, devise countless strategies by combining powers to form unique Team-Up skills and fight in destructible, ever-changing battlefields across the continually evolving Marvel universe!', 0.00, NULL, 'marvel_rivals_icon_7.jpg', 'Alpha', '2024-12-06', '2025-04-17'),

    --- Hades II ---
    ('Hades II', 'Battle beyond the Underworld using dark sorcery to take on the Titan of Time in this bewitching sequel to the award-winning rogue-like dungeon crawler.', 460.00, NULL, 'hades_ii_icon_8.jpg', 'Early Access', '2024-05-06', '2025-02-26'),

    --- Project Odyssey ---
    ('Project Odyssey', NULL, NULL, NULL, 'project_odyssey_icon_9.jpg', 'Cancelled', NULL, NULL),

    --- The Elder Scrolls VI ---
    ('The Elder Scrolls VI', 'It''s an action role-playing video game', NULL, NULL, 'the_elder_scrolls_vi_icon_10.jpg', 'Development', NULL, NULL),

    --- Star citizen ---
    ('Star citizen', 'Star Citizen is a science fiction game, with players taking the role of humans in the milky way 930 years into the future, with the United Empire of Earth ruling over dozens of systems, worlds and moons in the 30th century, and aliens controling their own systems and worlds.', 515.00, NULL, 'star_citizen_icon_11.jpg', 'Beta', '2017-12-23', '2018-03-04'),

    --- Deep down ---
    ('Deep down', 'Deep Down is an Action RPG with procedurally generated caves, real-time mining, crafting, and combat.', NULL, NULL, 'deep_down_icon_12.jpg', 'On Hold', '2014-07-17', '2016-12-02'),

    --- Hearts of Iron IV ---
    ('Hearts of Iron IV', 'Victory is at your fingertips! Your ability to lead your nation is your supreme weapon, the strategy game Hearts of Iron IV lets you take command of any nation in World War II.', 1219.00, '2016-06-06', 'hearts_of_iron_iv_icon_14.jpg', 'Released', '2014-01-23', '2025-04-09'),

    --- Geometry Dash ---
    ('Geometry Dash', 'Jump and fly your way through danger in this rhythm-based action platformer!', 124.00, '2013-08-13', 'geometry_dash_icon_15.jpg', 'Released', '2013-08-13', '2025-04-05');


--- Inserting Genres Data ---

INSERT INTO Genres (name) VALUES
    ('Sandbox'),
    ('Adventure'),
    ('RPG'),
    ('Survival'),
    ('Indie'),
    ('Exploration'),
    ('Simulation'),
    ('Strategy'),
    ('Management'),
    ('Automation'),
    ('Farming Sim'),
    ('Turn-Based Strategy'),
    ('4X'),
    ('Shooter'),
    ('Team-Based'),
    ('PvP'),
    ('Action'),
    ('Action Roguelike'),
    ('Open World'),
    ('Space Sim'),
    ('MMO'),
    ('Sci-Fi'),
    ('Grand Strategy'),
    ('Platformer'),
    ('Rhythm'),
    ('Music'),
    ('WWII');


--- Inserting Platforms Data ---

INSERT INTO Platforms (name) VALUES
    ('PC'),
    ('macOS'),
    ('Linux'),
    ('Mobile');


--- Inserting Game_Genres Data ---

INSERT INTO Game_Genres (game_id, genre_id) VALUES
    (1, 1), (1, 2), (1, 3), (1, 5),
    (2, 4), (2, 1), (2, 2), (2, 5),
    (3, 1), (3, 6), (3, 2), (3, 5),
    (4, 7), (4, 8), (4, 9), (4, 10), (4, 5),
    (5, 7), (5, 3), (5, 11), (5, 5),
    (6, 8), (6, 12), (6, 13),
    (7, 14), (7, 15), (7, 16), (7, 17),
    (8, 18), (8, 3), (8, 17), (8, 5),
    (10, 3), (10, 19), (10, 17), (10, 2),
    (11, 7), (11, 20), (11, 21), (11, 22), (11, 17), (11, 14),
    (12, 17), (12, 3),
    (13, 8), (13, 23), (13, 7), (13, 27),
    (14, 24), (14, 25), (14, 17), (14, 26), (14, 5);


--- Inserting Game_Platforms Data ---

INSERT INTO Game_Platforms (game_id, platform_id) VALUES
    (1, 1), (1, 2), (1, 3), (1, 4),
    (2, 1), (2, 2), (2, 3),
    (3, 1),
    (4, 1), (4, 2), (4, 3),
    (5, 1), (5, 2), (5, 3), (5, 4),
    (6, 1), (6, 2), (6, 3),
    (7, 1),
    (8, 1),
    (10, 1),
    (11, 1),
    (13, 1), (13, 2), (13, 3),
    (14, 1), (14, 4);


--- Inserting Developers_Games Data ---

INSERT INTO Developers_Games (developer_id, game_id) VALUES
    (1, 1),
    (2, 1),
    (6, 2),
    (10, 3),
    (12, 4),
    (14, 5),
    (16, 6),
    (22, 7),
    (24, 8),
    (28, 9),
    (30, 10),
    (34, 11),
    (35, 12),
    (38, 13),
    (40, 14);


--- Inserting Game_Studios Data ---

INSERT INTO Game_Studios (game_id, studio_id, role) VALUES
    (1, 1, 'Developer'), (1, 1, 'Publisher'),
    (2, 2, 'Developer'), (2, 2, 'Publisher'),
    (3, 3, 'Developer'), (3, 3, 'Publisher'),
    (4, 4, 'Developer'), (4, 4, 'Publisher'),
    (5, 5, 'Developer'), (5, 5, 'Publisher'),
    (6, 6, 'Developer'), (6, 7, 'Publisher'),
    (7, 8, 'Developer'), (7, 8, 'Publisher'),
    (8, 9, 'Developer'), (8, 9, 'Publisher'),
    (9, 10, 'Developer'), (9, 10, 'Publisher'),
    (10, 11, 'Developer'), (10, 11, 'Publisher'),
    (11, 12, 'Developer'), (11, 12, 'Publisher'),
    (12, 13, 'Developer'), (12, 13, 'Publisher'),
    (13, 14, 'Developer'), (13, 14, 'Publisher'),
    (14, 15, 'Developer'), (14, 15, 'Publisher');


--- Add funds to the specified user ---
Update Users
SET balance = balance + 1000.00
WHERE username = 'Redigit'