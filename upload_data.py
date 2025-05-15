import bcrypt
import decimal
import random
import datetime
import timedelta

from database_manager import DatabaseManager

db_manager = DatabaseManager()

def main():
    print("-------------------------")
    print("1. Insert Users Data")
    print("2. Insert Studios Data")
    print("3. Insert Developers Data")
    print("4. Insert Games Data")
    print("5. Insert Genres Data")
    print("6. Insert Platforms Data")
    print("7. Insert Game-Genre Links")
    print("8. Insert Game-Platform Links")
    print("9. Insert Developer-Game Links")
    print("10. Insert Game-Studio Links")
    print("11. Insert Reviews and Comments")
    print("12. Insert Purchases")
    print("13. Insert StudioApplications")
    print("14. Insert AdminNotifications")
    print("15. Delete All Data")
    print("16. Add Funds to User")
    print("-------------------------")
    print("\nChoose and Enter the command: ", end="")
    
    command = 0
    while True:
        try:
            raw_input = input()
            if not raw_input: continue
            command = int(raw_input)
        except ValueError:
            print("You've wrote a wrong command! Try again: ", end="")
            continue
        except EOFError:
            print("Input stream closed. Exiting")
    
        if command == 1:
            users_data = [
                # --- Terraria --- #
                ("Redigit", "redigit@gmail.com", hash_password("Redigit"), "2009-06-17", False), # have special rights in the game page
                ("Cenx", "Cenx@gmail.com", hash_password("Cenx"), "2013-08-05", False), # have special rights in the game page
                ("Loki", "Loki@gmail.com", hash_password("Loki"), "2012-07-02", False),
                ("FoodBarbarian", "FoodBarbarian@gmail.com", hash_password("FoodBarbarian"), "2014-09-03", False),
                
                # --- Don't Starve Together  --- #
                ("MatthewMarteinsson", "MatthewMarteinsson@gmail.com", hash_password("MatthewMarteinsson"), "2011-03-26", False), # have special rights in the oxygen not included page
                ("BryceDoig", "BryceDoig@gmail.com", hash_password("BryceDoig"), "2013-05-11", False), # have special rights in the don't starve together page
                ("AlexSavin", "AlexSavin@gmail.com", hash_password("AlexSavin"), "2014-03-21", False),
                
                # --- Astroneer --- #
                ("AaronBiddlecom", "AaronBiddlecom@gmail.com", hash_password("AaronBiddlecom"), "2011-11-01", False),
                ("AdamBromell", "AdamBromell@gmail.com", hash_password("AdamBromell"), "2012-12-16", False),
                ("AndreMaguire", "AndreMaguire@gmail.com", hash_password("AndreMaguire"), "2011-09-28", False),
                
                # --- Factorio --- #
                ("MichalKovarik", "MichalKovarik@gmail.com", hash_password("MichalKovarik"), "2012-02-09", False),
                ("Tomax", "Tomax@gmail.com", hash_password("Tomax"), "2013-05-30", False), # have special rights in the game page
                ("DanStevens", "DanStevens@gmail.com", hash_password("DanStevens"), "2014-01-07", False),
                
                # --- Stardew Valley --- #
                ("EricBarone", "EricBarone@gmail.com", hash_password("EricBarone"), "2015-02-15", False), # have special rights in the game page
                
                # --- Sid Meier's Civilization VI --- #
                ("EdBeach", "EdBeach@gmail.com", hash_password("EdBeach"), "2010-08-09", False),
                ("DennisShirk", "DennisShirk@gmail.com", hash_password("DennisShirk"), "2010-09-14", False), # have special rights in the game page
                ("AndrewFrederiksen", "AndrewFrederiksen@gmail.com", hash_password("AndrewFrederiksen"), "2010-09-21", False),
                
                ("ChristophHartmann", "ChristophHartmann@gmail.com", hash_password("ChristophHartmann"), "2008-04-12", False),
                ("JohnChowanec", "JohnChowanec@gmail.com", hash_password("JohnChowanec"), "2008-05-03", False),
                ("MelissaMiller", "MelissaMiller@gmail.com", hash_password("MelissaMiller"), "2008-07-06", False),
            
                # --- Marvel Rivals --- #
                ("ThaddeusSasser", "ThaddeusSasser@gmail.com", hash_password("ThaddeusSasser"), "2013-05-15", False),
                ("James", "James@gmail.com", hash_password("James"), "2017-07-05", False), # have special rights in the game page
                ("GuangyunChen", "GuangyunChen@gmail.com", hash_password("GuangyunChen"), "2018-10-29", False),
                
                # --- Hades II --- #
                ("WillTurnbull", "WillTurnbull@gmail.com", hash_password("WillTurnbull"), "2015-01-19", False), # have special rights in the game page
                ("AmirRao", "AmirRao@gmail.com", hash_password("AmirRao"), "2015-04-02", False),
                ("GregKasavin", "GregKasavin@gmail.com", hash_password("GregKasavin"), "2016-01-04", False),
                
                # --- Project Odyssey --- #
                ("DanHay", "DanHay@gmail.com", hash_password("DanHay"), "2011-01-10", False),
                ("RimaBrek", "RimaBrek@gmail.com", hash_password("RimaBrek"), "2011-03-14", False), # have special rights in the game page
                ("ClementMarcou", "ClementMarcou@gmail.com", hash_password("ClementMarcou"), "2011-05-09", False),
                
                # --- The Elder Scrolls VI --- #
                ("CraigLafferty", "CraigLafferty@gmail.com", hash_password("CraigLafferty"), "2009-10-24", False),
                ("MarkLampert", "MarkLampert@gmail.com", hash_password("MarkLampert"), "2008-09-11", False),
                ("AshleyCheng", "AshleyCheng@gmail.com", hash_password("AshleyCheng"), "2010-12-27", False),
                
                # --- Star citizen --- #
                ("ChrisRoberts", "ChrisRoberts@gmail.com", hash_password("ChrisRoberts"), "2014-06-13", False),
                ("PedroCamacho", "PedroCamacho@gmail.com", hash_password("PedroCamacho"), "2015-02-18", False), # have special rights in the game page
                
                # --- Deep down --- #
                ("KenzoTsujimoto", "KenzoTsujimoto@gmail.com", hash_password("KenzoTsujimoto"), "2009-01-09", False), # have special rights in the game page
                ("TokuroFujiwara", "TokuroFujiwara@gmail.com", hash_password("TokuroFujiwara"), "2010-08-07", False),
                
                # --- Hearts of Iron IV --- #
                ("JohanAndersson", "JohanAndersson@gmail.com", hash_password("JohanAndersson"), "2015-03-04", False),
                ("DanLind", "DanLind@gmail.com", hash_password("DanLind"), "2015-06-05", False), # have special rights in the game page
                ("LindaKiby", "LindaKiby@gmail.com", hash_password("LindaKiby"), "2014-03-12", False),
                
                # --- Geometry Dash --- #
                ("RobTop", "RobTop@gmail.com", hash_password("RobTop"), "2011-04-18", False), # have special rights in the game page
                
                # --- Admin --- #
                ("Admin", "Admin@gmail.com", hash_password("Admin"), "2006-03-27", True),
            ]
            
            print("--- Inserting Users Data ---")
            insert_query = "INSERT INTO Users (username, email, password_hash, registration_date, is_app_admin) VALUES (%s, %s, %s, %s, %s);"
            
            db_manager.execute_many_query(insert_query, users_data)
            
            print("--- The Data is Successfully Inserted ---")
            break
        elif command == 2:
            
            studios_data = [
                # --- Terraria --- #
                ("Re-Logic", "https://re-logic.com/", "re-logic_icon_1.png", "United States", "Best known for the Terraria franchise - the revolutionary 2D Sandbox Adventure that has entertained millions of gamers worldwide - Re-Logic seeks to showcase and evolve the limits of what Indie gaming can be!", "2011-01-24"),
                
                # --- Don't Starve Together --- #
                ("Klei", "https://www.klei.com/", "klei_icon_2.jpg", "Canada", "It Rhymes With Play", "2005-07-01"),
                
                # --- Astroneer --- #
                ("System Era Softworks", "https://www.systemera.net/", "system_era_softworks_icon_3.png", "United States", "System Era Softworks is a small development studio led by veteran game developers headquartered in Seattle, Washington. We are currently working on our first game, Astroneer.", "2014-03-07"),
                
                # --- Factorio --- #
                ("Wube Software", None, "wube_software_icon_4.jpg", "Czech Republic", "Wube Software is a team of passionate professionals dedicated to creating exceptional games.", "2014-09-03"),
                
                # --- Stardew Valley --- #
                ("ConcernedApe", None, "concernedape_icon_5.jpg", "United States", "ConcernedApe is the moniker of Eric Barone, a solo game developer based in Seattle, WA.", "2012-05-05"),
                
                # --- Sid Meier's Civilization VI --- #
                ("Firaxis Games", "https://firaxis.com/", "firaxis_games_icon_6.jpg", "United States", "Firaxis Games is a world-renowned game development studio with an unwavering mission to \"build games that stand the test of time\".", "1996-05-12"),
                
                ("2K", "https://2k.com/", "2k_icon_7.jpg", "United States", "2K develops and publishes critically-acclaimed franchises such as BioShock, Borderlands, Sid Meier’s Civilization, XCOM, WWE 2K, and NBA 2K.", "2005-01-25"),
                
                # --- Marvel Rivals --- #
                ("NetEaseGames", "https://www.neteasegames.com/", "net_ease_games_icon_8.png", "China", "NetEase Games is the gaming division of NetEase, Inc., a major Chinese tech company. It focuses on developing and publishing video games across various platforms, including mobile, PC, and consoles.", "2001-09-08"),
                
                # --- Hades II --- #
                ("Supergiant Games", "https://www.supergiantgames.com/", "supergiant_games_icon_9.jpg", "United States", "We make games that spark your imagination like the games you played as a kid.", "2009-07-27"),
                
                # --- Project Odyssey --- #
                ("Blizzard Entertainment", "https://www.blizzard.com/en-us/", "blizzard_entertainment_icon_10.jpg", "United States", "Dedicated to creating the most epic entertainment experiences... ever.", "1991-02-08"),
                
                # --- The Elder Scrolls VI --- #
                ("Bethesda Softworks", "https://bethesda.net/en/dashboard", "bethesda_softworks_icon_11.png", "United States", "Bethesda Softworks is an award-winning development team renowned worldwide for its groundbreaking work on the The Elder Scrolls and Fallout series.", "1986-06-28"),
                
                # --- Star citizen --- #
                ("Cloud Imperium Games Corporation", "https://cloudimperiumgames.com/", "cloud_imperium_games_corporation_icon_12.jpg", "United States", "We never settle and we're never daunted.", "2012-03-17"),
                
                # --- Deep down --- #
                ("Capcom", "https://www.capcom.com/", "capcom_icon_13.jpg", "Japan", "Capcom began in Japan in 1979 as a manufacturer and distributor of electronic game machines.", "1979-09-21"),
                
                # --- Hearts of Iron IV --- #
                ("Paradox Interactive", "https://www.paradoxinteractive.com/", "paradox_interactive_icon_14.jpg", "Sweden", "We Create the Games. You Create the Stories.", "1999-01-04"),
                
                # --- Geometry Dash --- #
                ("RobTop Games", "https://www.robtopgames.com/", "robtop_games_icon_15.jpg", "Sweden", "I have created the mobile games Rune, Boomlings, Boomlings MatchUp, Memory Mastermind, Forlorn", "2012-11-05")
            ]
            
            print("--- Inserting Studios Data ---")
            insert_query = "INSERT INTO Studios (name, website_url, logo, country, description, established_date) VALUES (%s, %s, %s, %s, %s, %s);"
            
            db_manager.execute_many_query(insert_query, studios_data)
            
            print("--- The Data is Successfully Inserted ---")
            break
        elif command == 3:
            developers_data = [
                # --- Terraria --- #
                (1, 1, "redigit@gmail.com", "Admin"), # have special rights in the game page
                (2, 1, "Cenx@gmail.com", "Member"), # have special rights in the game page
                (3, 1, "Loki@gmail.com", "Member"),
                (4, 1, "FoodBarbarian@gmail.com", "Member"),
                
                # --- Don't Starve Together  --- #
                (5, 2, "MatthewMarteinsson@gmail.com", "Admin"),
                (6, 2, "BryceDoig@gmail.com", "Member"), # have special rights in the game page
                (7, 2, "AlexSavin@gmail.com", "Member"),
                
                # --- Astroneer --- #
                (8, 3, "AaronBiddlecom@gmail.com", "Admin"),
                (9, 3, "AdamBromell@gmail.com", "Member"),
                (10, 3, "AndreMaguire@gmail.com", "Member"), # have special rights in the game page
                
                # --- Factorio --- #
                (11, 4, "MichalKovarik@gmail.com", "Admin"),
                (12, 4, "Tomax@gmail.com", "Member"), # have special rights in the game page
                (13, 4, "DanStevens@gmail.com", "Member"),
                
                # --- Stardew Valley --- #
                (14, 5, "EricBarone@gmail.com", "Admin"), # have special rights in the game page
                
                # --- Sid Meier's Civilization VI --- #
                (15, 6, "EdBeach@gmail.com", "Admin"),
                (16, 6, "DennisShirk@gmail.com", "Member"), # have special rights in the game page
                (17, 6, "AndrewFrederiksen@gmail.com", "Member"),
                
                (18, 7, "ChristophHartmann@gmail.com", "Admin"),
                (19, 7, "JohnChowanec@gmail.com", "Member"),
                (20, 7, "MelissaMiller@gmail.com", "Member"),
            
                # --- Marvel Rivals --- #
                (21, 8, "ThaddeusSasser@gmail.com", "Admin"),
                (22, 8, "James@gmail.com", "Member"), # have special rights in the game page
                (23, 8, "GuangyunChen@gmail.com", "Member"),
                
                # --- Hades II --- #
                (24, 9, "WillTurnbull@gmail.com", "Admin"), # have special rights in the game page
                (25, 9, "AmirRao@gmail.com", "Member"),
                (26, 9, "GregKasavin@gmail.com", "Member"),
                
                # --- Project Odyssey --- #
                (27, 10, "DanHay@gmail.com", "Admin"),
                (28, 10, "RimaBrek@gmail.com", "Member"), # have special rights in the game page
                (29, 10, "ClementMarcou@gmail.com", "Member"),
                
                # --- The Elder Scrolls VI --- #
                (30, 11, "CraigLafferty@gmail.com", "Admin"), # have special rights in the game page
                (31, 11, "MarkLampert@gmail.com", "Member"),
                (32, 11, "AshleyCheng@gmail.com", "Member"),
                
                # --- Star citizen --- #
                (33, 12, "ChrisRoberts@gmail.com", "Admin"),
                (34, 12, "PedroCamacho@gmail.com", "Member"), # have special rights in the game page
                
                # --- Deep down --- #
                (35, 13, "KenzoTsujimoto@gmail.com", "Admin"), # have special rights in the game page
                (36, 13, "TokuroFujiwara@gmail.com", "Member"),
                
                # --- Hearts of Iron IV --- #
                (37, 14, "JohanAndersson@gmail.com", "Admin"),
                (38, 14, "DanLind@gmail.com", "Member"), # have special rights in the game page
                (39, 14, "LindaKiby@gmail.com", "Member"),
                
                # --- Geometry Dash --- #
                (40, 15, "RobTop@gmail.com", "Admin") # have special rights in the game page
            ]
            
            print("--- Inserting Developers Data ---")
            insert_query = "INSERT INTO Developers (user_id, studio_id, contact_email, role) VALUES (%s, %s, %s, %s);"
            
            db_manager.execute_many_query(insert_query, developers_data)
            
            print("--- The Data is Successfully Inserted ---")
            break;
        elif command == 4:
            games_data = [
                # --- Terraria --- #
                ("Terraria", "Dig, fight, explore, build! Nothing is impossible in this action-packed adventure game.", 225.00, "2011-05-16", "terraria_icon_1.png", "Released", "2011-01-03", "2025-03-27"),
                
                # --- Don't Starve Together  --- #
                ("Don't Starve Together", "Fight, Farm, Build and Explore Together in the standalone multiplayer expansion to the uncompromising wilderness survival game, Don't Starve.", 229.00, "2016-04-21", "don't_starve_together_icon_2.jpg", "Released", "2014-12-15", "2025-04-17"),
                
                # --- Astroneer --- #
                ("Astroneer", "Interact with strange new worlds in a unique and tactile way, molding the environment itself as if it were clay in your hands.", 600.00, "2019-02-06", "astroneer_icon_3.jpg", "Released", "2016-12-16", "2025-04-02"),
                
                # --- Factorio --- #
                ("Factorio", "Factorio is a game about building and creating automated factories to produce items of increasing complexity, within an infinite 2D world.", 300.00, "2020-08-14", "factorio_icon_4.png", "Released", "2012-06-22", "2025-03-31"),
                
                # --- Stardew Valley --- #
                ("Stardew Valley", "You've inherited your grandfather's old farm plot in Stardew Valley.", 229.00, "2016-02-26", "stardew_valley_icon_5.jpg", "Released", "2011-11-29", "2024-12-20"),
                
                # --- Sid Meier's Civilization VI --- #
                ("Sid Meier's Civilization VI", "Expand your empire, advance your culture and go head-to-head against history’s greatest leaders.", 525.00, "2016-10-21", "sid_meier's_civilization_vi_icon_6.jpg", "Released", "2014-05-03", "2025-01-15"),
                
                # --- Marvel Rivals --- #
                ("Marvel Rivals", "Marvel Rivals is a Super Hero Team-Based PVP Shooter! Assemble an all-star Marvel squad, devise countless strategies by combining powers to form unique Team-Up skills and fight in destructible, ever-changing battlefields across the continually evolving Marvel universe!", 0.00, None, "marvel_rivals_icon_7.jpg", "Alpha", "2024-12-06", "2025-04-17"),
                
                # --- Hades II --- #
                ("Hades II", "Battle beyond the Underworld using dark sorcery to take on the Titan of Time in this bewitching sequel to the award-winning rogue-like dungeon crawler.", 460.00, None, "hades_ii_icon_8.jpg", "Early Access", "2024-05-06", "2025-02-26"),
                
                # --- Project Odyssey --- #
                ("Project Odyssey", None, None, None, "project_odyssey_icon_9.jpg", "Cancelled", None, None),
                
                # --- The Elder Scrolls VI --- #
                ("The Elder Scrolls VI", "It's an action role-playing video game", None, None, "the_elder_scrolls_vi_icon_10.jpg", "Development", None, None),
                
                # --- Star citizen --- #
                ("Star citizen", "Star Citizen is a science fiction game, with players taking the role of humans in the milky way 930 years into the future, with the United Empire of Earth ruling over dozens of systems, worlds and moons in the 30th century, and aliens controling their own systems and worlds.", 515.00, None, "star_citizen_icon_11.jpg", "Beta", "2017-12-23", "2018-03-04"),
                
                # --- Deep down --- #
                ("Deep down", "Deep Down is an Action RPG with procedurally generated caves, real-time mining, crafting, and combat.", None, None, "deep_down_icon_12.jpg", "On Hold", "2014-07-17", "2016-12-02"),
                
                # --- Hearts of Iron IV --- #
                ("Hearts of Iron IV", "Victory is at your fingertips! Your ability to lead your nation is your supreme weapon, the strategy game Hearts of Iron IV lets you take command of any nation in World War II.", 1219.00, "2016-06-06", "hearts_of_iron_iv_icon_14.jpg", "Released", "2014-01-23", "2025-04-09"),
                
                # --- Geometry Dash --- #
                ("Geometry Dash", "Jump and fly your way through danger in this rhythm-based action platformer!", 124.00, "2013-08-13", "geometry_dash_icon_15.jpg", "Released", "2013-08-13", "2025-04-05"),
                
                # --- Oxygen not included --- #
                ("Oxygen not included", "Oxygen Not Included is a space-colony simulation game. Deep inside an alien space rock your industrious crew will need to master science, overcome strange new lifeforms, and harness incredible space tech to survive, and possibly, thrive.", 329.00, "2019-07-30", "oxygen_not_incluede_icon_15.png", "Released", "2017-02-15", "2025-04-09")
            ]
            
            print("--- Inserting Games Data ---")
            insert_query = "INSERT INTO Games (title, description, price, release_date, image, status, created_at, updated_at) VALUES (%s, %s, %s, %s, %s, %s, %s, %s);"
            
            db_manager.execute_many_query(insert_query, games_data)
            
            print("--- The Data is Successfully Inserted ---")
            break;
        
        elif command == 5:
            genre_names = [
                ("Sandbox"), ("Adventure"), ("RPG"), ("Survival"), ("Indie"), ("Exploration"),
                ("Simulation"), ("Strategy"), ("Management"), ("Automation"), ("Farming Sim"),
                ("Turn-Based Strategy"), ("4X"), ("Shooter"), ("Team-Based"), ("PvP"), ("Action"),
                ("Action Roguelike"), ("Open World"), ("Space Sim"), ("MMO"), ("Sci-Fi"),
                ("Grand Strategy"), ("Platformer"), ("Rhythm"), ("Music"), ("WWII")
            ]
            
            genres_data = [(name,) for name in genre_names]
            
            print("--- Inserting Genres Data ---")
            insert_query = "INSERT INTO Genres (name) VALUES (%s);"
            db_manager.execute_many_query(insert_query, genres_data)
            break
        
        elif command == 6:
            platform_names = [
                ("PC"), ("macOS"), ("Linux"), ("Mobile")
            ]
            
            platforms_data = [(name,) for name in platform_names]
            
            print("--- Inserting Platforms Data ---")
            insert_query = "INSERT INTO Platforms (name) VALUES (%s);"
            db_manager.execute_many_query(insert_query, platforms_data)
            break
        
        elif command == 7:
            game_genres = [
                (1, 1), (1, 2), (1, 3), (1, 5), (2, 4), (2, 1), (2, 2), (2, 5),
                (3, 1), (3, 6), (3, 2), (3, 5), (4, 7), (4, 8), (4, 9), (4, 10), (4, 5), (5, 7), (5, 3),
                (5, 11), (5, 5), (6, 8), (6, 12), (6, 13), (7, 14), (7, 15), (7, 16), (7, 17), (8, 18), (8, 3), (8, 17), (8, 5),
                (10, 3), (10, 19), (10, 17), (10, 2), (11, 7), (11, 20), (11, 21), (11, 22), (11, 17), (11, 14), (12, 17), (12, 3), (13, 8),
                (13, 23), (13, 7), (13, 27), (14, 24), (14, 25), (14, 17), (14, 26), (14, 5), (15, 4), (15, 8)
            ]
            
            print("--- Inserting Game_Genres Data ---")
            insert_query = "INSERT INTO Game_Genres (game_id, genre_id) VALUES (%s, %s);"
            db_manager.execute_many_query(insert_query, game_genres)
            break
        
        elif command == 8:
            game_platforms = [
                (1, 1), (1, 2), (1, 3), (1, 4), (2, 1), (2, 2), (2, 3), (3, 1), (4, 1), (4, 2), (4, 3), (5, 1), (5, 2), (5, 3), (5, 4), (6, 1),
                (6, 2), (6, 3), (7, 1), (8, 1), (10, 1), (11, 1), (13, 1), (13, 2), (13, 3), (14, 1), (14, 4), (15, 1), (15, 2), (15, 3)
            ]
            
            print("--- Inserting Game_Platforms Data ---")
            insert_query = "INSERT INTO Game_Platforms (game_id, platform_id) VALUES (%s, %s);"
            db_manager.execute_many_query(insert_query, game_platforms)
            break
        
        elif command == 9:
            developer_games = [
                (1, 1), (2, 1), (6, 2), (10, 3), (12, 4), (14, 5), (16, 6),
                (22, 7), (24, 8), (28, 9), (30, 10), (34, 11), (35, 12), (38, 13), (40, 14), (5, 15)
            ]
            
            print("--- Inserting Developers_Games Data ---")
            insert_query = "INSERT INTO Developers_Games (developer_id, game_id) VALUES (%s, %s);"
            db_manager.execute_many_query(insert_query, developer_games)
            break
            
        elif command == 10:
            game_studios = [
                (1, 1, 'Developer'), (1, 1, 'Publisher'), (2, 2, 'Developer'), (2, 2, 'Publisher'), (3, 3, 'Developer'), (3, 3, 'Publisher'),
                (4, 4, 'Developer'), (4, 4, 'Publisher'), (5, 5, 'Developer'), (5, 5, 'Publisher'), (6, 6, 'Developer'), (6, 7, 'Publisher'),
                (7, 8, 'Developer'), (7, 8, 'Publisher'), (8, 9, 'Developer'), (8, 9, 'Publisher'), (9, 10, 'Developer'), (9, 10, 'Publisher'),
                (10, 11, 'Developer'), (10, 11, 'Publisher'), (11, 12, 'Developer'), (11, 12, 'Publisher'), (12, 13, 'Developer'), (12, 13, 'Publisher'),
                (13, 14, 'Developer'), (13, 14, 'Publisher'), (14, 15, 'Developer'), (14, 15, 'Publisher'), (15, 2, 'Developer'), (15, 2, 'Publisher')
            ]
            
            print("--- Inserting Game_Studios Data ---")
            insert_query = "INSERT INTO Game_Studios (game_id, studio_id, role) VALUES (%s, %s, %s);"
            db_manager.execute_many_query(insert_query, game_studios)
            break
            
        elif command == 11:
            print("--- Inserting Reviews and Comments Data ---")

            reviews = [
                (1, 1, "Absolutely fantastic game! The atmosphere and gameplay are top-notch.", "2025-05-10 08:32:47"),
                (2, 1, "Pretty good, but I expected a bit more. There's room for improvement.", "2025-05-03 12:47:47"),
                (3, 2, "This is a masterpiece! Highly recommend everyone to try it out.", "2025-05-03 23:33:47"),
                (4, 2, "The graphics are stunning, but the storyline felt a little weak.", "2025-05-09 04:41:47"),
                (5, 3, "Hooked from the first few minutes. Hours just fly by!", "2025-05-10 12:52:47"),
                (6, 3, "Technical issues really spoil the experience. Needs patching ASAP.", "2025-05-13 07:26:47"),
                (7, 4, "Interesting concept, but the execution could have been better.", "2025-05-11 12:16:47"),
                (8, 4, "Worth every penny. Lots of content and replayability.", "2025-05-04 02:02:47"),
                (9, 5, "A must-have for fans of this genre! You won't be disappointed.", "2025-05-10 09:57:47"),
                (10, 5, "It was challenging at first, but once I got the hang of it, I had a blast.", "2025-05-05 18:11:47"),
                (11, 1, "Simple yet incredibly addictive. Great for unwinding after a long day.", "2025-05-10 15:25:47"),
                (12, 2, "Unfortunately, it didn't live up to my expectations at all.", "2025-05-04 18:49:47"),
                (13, 3, "A very original take on familiar mechanics. Refreshing!", "2025-05-05 13:30:47"),
                (14, 4, "More fun with friends, but the solo experience is also quite enjoyable.", "2025-05-12 17:35:47"),
                (15, 5, "Eagerly awaiting a sequel or some substantial DLC!", "2025-05-03 11:36:47")
            ]

            print("--- Inserting Reviews ---")
            insert_query = "INSERT INTO Reviews (user_id, game_id, review_text, review_date) VALUES (%s, %s, %s, %s) RETURNING review_id;"
            db_manager.execute_many_query(insert_query, reviews)
            
            comments_on_review = [
                (7, 7, "Spot on! Great observation.", "2025-05-10 08:32:47"),
                (12, 7, "You might be right about that.", "2025-05-03 12:47:47"),
                (11, 8, "Couldn't agree more!", "2025-05-03 23:33:47"),
                (6, 4, "I'll have to give that a try.", "2025-05-09 04:41:47"),
                (13, 15, "This is worth considering.", "2025-05-10 12:52:47"),
                (1, 12, "Exactly my thoughts.", "2025-05-13 07:26:47"),
                (3, 10, "Actually, that's the part I liked the most.", "2025-05-11 12:16:47"),
                (8, 9, "Thanks for the detailed review!", "2025-05-04 02:02:47"),
                (9, 12, "Well, I have a different opinion on this.", "2025-05-10 09:57:47"),
                (14, 7, "Appreciate you sharing your insights.", "2025-05-05 18:11:47"),
                (5, 1, "Well said, indeed.", "2025-05-10 15:25:47"),
                (10, 8, "That's an interesting point of view.", "2025-05-04 18:49:47"),
                (2, 9, "There's definitely an element of that.", "2025-05-05 13:30:47"),
                (4, 15, "I second every word of this.", "2025-05-12 17:35:47"),
                (15, 4, "Haha, so true!", "2025-05-03 11:36:47")
            ]
            
            print("--- Inserting Comments ---")
            insert_query = "INSERT INTO ReviewComments (review_id, user_id, comment_text, comment_date) VALUES (%s, %s, %s, %s);"
            db_manager.execute_many_query(insert_query, comments_on_review)
            break;
        
        elif command == 12:
            purchases = [
                (1, "2025-02-12 10:38:47", 225.00, 'Completed'),
                (2, "2025-02-14 10:39:48", 229.00, 'Completed'),
                (3, "2025-02-16 10:40:47", 600.00, 'Completed'),
                (1, "2025-02-18 10:41:47", 300.00, 'Completed'),
                (4, "2025-02-20 10:42:47", 229.00, 'Completed'),
                (5, "2025-02-22 10:43:47", 525.00, 'Completed'),
                (2, "2025-02-24 10:44:47", 0.00, 'Completed'),
                (6, "2025-02-26 10:45:47", 460.00, 'Completed'),
                (7, "2025-02-28 10:46:47", 0.00, 'Completed'),
                (3, "2025-03-02 10:47:47", 0.00, 'Completed'),
                (8, "2025-03-04 10:48:47", 225.0, 'Completed'),
                (9, "2025-03-06 10:49:47", 229.00, 'Completed'),
                (10, "2025-03-08 10:50:47", 600.00, 'Completed'),
                (11, "2025-03-08 10:10:47", 229.00, 'Completed'),
                (12, "2025-04-09 11:51:47", 525.00, 'Completed'),
            ]
            
            print("--- Inserting Purchase ---")
            insert_query = "INSERT INTO Purchases (user_id, purchase_date, total_amount, status) VALUES (%s, %s, %s, %s);"
            db_manager.execute_many_query(insert_query, purchases)
            
            purchases_items = [
                (1, 1, 225.00),
                (2, 2, 229.00),
                (3, 3, 600.00),
                (4, 4, 300.00),
                (5, 5, 229.00),
                (6, 6, 525.00),
                (7, 7, 0.00),
                (8, 8, 460.00),
                (9, 9, 0.00),
                (10, 10, 0.00),
                (11, 1, 225.00),
                (12, 2, 229.00),
                (13, 3, 600.00),
                (14, 5, 229.00),
                (15, 6, 525.00)
            ]
            
            print("--- Inserting Purchase Items ---")
            insert_query = "INSERT INTO Purchases_Items (purchase_id, game_id, price_at_purchase) VALUES (%s, %s, %s);"
            db_manager.execute_many_query(insert_query, purchases_items)
            
            break
        
        elif command == 13:
            print("--- Inserting Studio Applications ---")

            studio_applications = [
                (1, 1, "2024-05-13 12:45:18", "Accepted", 41, "2024-05-16 12:46:18"),
                (2, 1, "2024-05-17 12:47:18", "Accepted", 41, "2024-05-19 12:48:18"),
                (3, 1, "2024-05-23 12:49:18", "Accepted", 41, "2024-05-26 12:50:18"),
                (4, 1, "2024-05-29 12:51:18", "Accepted", 41, "2024-06-02 12:52:18"),
                (5, 2, "2024-06-05 12:53:18", "Accepted", 41, "2024-06-06 12:54:18"),
                (6, 2, "2024-06-10 12:55:18", "Accepted", 41, "2024-06-15 12:56:18"),
                (7, 2, "2024-06-13 12:57:18", "Accepted", 41, "2024-06-16 12:58:18"),
                (8, 3, "2024-06-19 12:59:18", "Accepted", 41, "2024-06-20 12:01:18"),
                (9, 3, "2024-06-25 12:02:18", "Accepted", 41, "2024-06-28 12:03:18"),
                (10, 3, "2024-06-29 12:04:18", "Accepted", 41, "2024-07-03 12:05:18"),
                (11, 4, "2024-07-02 12:06:18", "Accepted", 41, "2024-07-05 12:07:18"),
                (12, 4, "2024-07-07 12:08:18", "Accepted", 41, "2024-07-11 12:09:18"),
                (13, 4, "2024-07-10 12:10:18", "Accepted", 41, "2024-07-13 12:11:18"),
                (14, 5, "2024-07-17 12:12:18", "Accepted", 41, "2024-07-19 12:13:18"),
                (15, 6, "2024-07-21 12:14:18", "Accepted", 41, "2024-07-22 12:15:18"),
                (16, 6, "2024-07-25 12:16:18", "Accepted", 41, "2024-07-30 12:17:18"),
                (17, 6, "2024-07-28 12:18:18", "Accepted", 41, "2024-07-31 12:19:18"),
                (18, 7, "2024-07-31 12:20:18", "Accepted", 41, "2024-08-01 12:21:18"),
                (19, 7, "2024-08-06 12:22:18", "Accepted", 41, "2024-08-11 12:23:18"),
                (20, 7, "2024-08-12 12:24:18", "Accepted", 41, "2024-08-15 12:25:18"),
                (21, 8, "2024-08-15 12:26:18", "Accepted", 41, "2024-08-19 12:27:18"),
                (22, 8, "2024-08-19 12:28:18", "Accepted", 41, "2024-08-21 12:29:18"),
                (23, 8, "2024-08-24 12:30:18", "Accepted", 41, "2024-08-27 12:31:18"),
                (24, 9, "2024-08-28 12:32:18", "Accepted", 41, "2024-08-31 12:33:18"),
                (25, 9, "2024-09-03 12:34:18", "Accepted", 41, "2024-09-05 12:35:18"),
                (26, 9, "2024-09-06 12:36:18", "Accepted", 41, "2024-09-11 12:37:18"),
                (27, 10, "2024-09-09 12:38:18", "Accepted", 41, "2024-09-11 12:39:18"),
                (28, 10, "2024-09-12 12:40:18", "Accepted", 41, "2024-09-16 12:41:18"),
                (29, 10, "2024-09-16 12:42:18", "Accepted", 41, "2024-09-20 12:43:18"),
                (30, 11, "2024-09-22 12:44:18", "Accepted", 41, "2024-09-26 12:45:18"),
                (31, 11, "2024-09-29 12:46:18", "Accepted", 41, "2024-10-04 12:47:18"),
                (32, 11, "2024-10-05 12:48:18", "Accepted", 41, "2024-10-09 12:49:18"),
                (33, 12, "2024-10-10 12:50:18", "Accepted", 41, "2024-10-14 12:51:18"),
                (34, 12, "2024-10-14 12:52:18", "Accepted", 41, "2024-10-19 12:53:18"),
                (35, 13, "2024-10-20 12:54:18", "Accepted", 41, "2024-10-23 12:55:18"),
                (36, 13, "2024-10-26 12:56:18", "Accepted", 41, "2024-10-28 12:57:18"),
                (37, 14, "2024-11-02 12:58:18", "Accepted", 41, "2024-11-04 12:59:18"),
                (38, 14, "2024-11-07 12:01:18", "Accepted", 41, "2024-11-09 12:02:18"),
                (39, 14, "2024-11-13 12:03:18", "Accepted", 41, "2024-11-17 12:04:18"),
                (40, 15, "2024-11-19 12:05:18", "Accepted", 41, "2024-11-17 12:06:18"),
            ]

            insert_query = "INSERT INTO StudioApplications (user_id, studio_id, application_date, status, reviewed_by, review_date) VALUES (%s, %s, %s, %s, %s, %s);"
            db_manager.execute_many_query(insert_query, studio_applications)
            print("--- Studio Applications Data Insertion Attempt Complete ---")
            break
        
        elif command == 14:
            print("--- Inserting Admin Notifications ---")
            
            admin_notifications = [
                (1, 1, "developer_status_request", "redigit@gmail.com", "approved", "2023-05-14 14:51:48", 41, "2023-05-15 14:52:48"),
                (2, 2, "developer_status_request", "Cenx@gmail.com", "approved", "2023-05-20 14:53:48", 41, "2023-05-23 14:54:48"),
                (3, 3, "developer_status_request", "Loki@gmail.com", "approved", "2023-05-27 14:55:48", 41, "2023-06-01 14:56:48"),
                (4, 4, "developer_status_request", "FoodBarbarian@gmail.com", "approved", "2023-06-01 14:57:48", 41, "2023-06-04 14:58:48"),
                (5, 5, "developer_status_request", "MatthewMarteinsson@gmail.com", "approved", "2023-06-13 14:59:48", 41, "2023-06-17 14:01:48"),
                (6, 6, "developer_status_request", "BryceDoig@gmail.com", "approved", "2023-06-26 14:02:48", 41, "2023-06-27 14:03:48"),
                (7, 7, "developer_status_request", "AlexSavin@gmail.com", "approved", "2023-07-05 14:04:48", 41, "2023-07-09 14:05:48"),
                (8, 8, "developer_status_request", "AaronBiddlecom@gmail.com", "approved", "2023-07-12 14:06:48", 41, "2023-07-16 14:07:48"),
                (9, 9, "developer_status_request", "AdamBromell@gmail.com", "approved", "2023-07-25 14:08:48", 41, "2023-07-27 14:09:48"),
                (10, 10, "developer_status_request", "AndreMaguire@gmail.com", "approved", "2023-08-09 14:10:48", 41, "2023-08-14 14:11:48"),
                (11, 11, "developer_status_request", "MichalKovarik@gmail.com", "approved", "2023-08-24 14:12:48", 41, "2023-08-30 14:13:48"),
                (12, 12, "developer_status_request", "Tomax@gmail.com", "approved", "2023-09-02 14:14:48", 41, "2023-09-05 14:15:48"),
                (13, 13, "developer_status_request", "DanStevens@gmail.com", "approved", "2023-09-16 14:16:48", 41, "2023-09-21 14:17:48"),
                (14, 14, "developer_status_request", "EricBarone@gmail.com", "approved", "2023-09-21 14:18:48", 41, "2023-09-26 14:19:48"),
                (15, 15, "developer_status_request", "EdBeach@gmail.com", "approved", "2023-09-28 14:20:48", 41, "2023-10-05 14:21:48"),
                (16, 16, "developer_status_request", "DennisShirk@gmail.com", "approved", "2023-10-07 14:22:48", 41, "2023-10-12 14:23:48"),
                (17, 17, "developer_status_request", "AndrewFrederiksen@gmail.com", "approved", "2023-10-22 14:24:48", 41, "2023-10-28 14:25:48"),
                (18, 18, "developer_status_request", "ChristophHartmann@gmail.com", "approved", "2023-11-04 14:26:48", 41, "2023-11-05 14:27:48"),
                (19, 19, "developer_status_request", "JohnChowanec@gmail.com", "approved", "2023-11-14 14:28:48", 41, "2023-11-17 14:29:48"),
                (20, 20, "developer_status_request", "MelissaMiller@gmail.com", "approved", "2023-11-25 14:30:48", 41, "2023-11-29 14:31:48"),
                (21, 21, "developer_status_request", "ThaddeusSasser@gmail.com", "approved", "2023-12-02 14:32:48", 41, "2023-12-03 14:33:48"),
                (22, 22, "developer_status_request", "James@gmail.com", "approved", "2023-12-09 14:34:48", 41, "2023-12-15 14:35:48"),
                (23, 23, "developer_status_request", "GuangyunChen@gmail.com", "approved", "2023-12-18 14:36:48", 41, "2023-12-23 14:37:48"),
                (24, 24, "developer_status_request", "WillTurnbull@gmail.com", "approved", "2023-12-31 14:38:48", 41, "2024-01-07 14:39:48"),
                (25, 25, "developer_status_request", "AmirRao@gmail.com", "approved", "2024-01-05 14:40:48", 41, "2024-01-12 14:41:48"),
                (26, 26, "developer_status_request", "GregKasavin@gmail.com", "approved", "2024-01-18 14:42:48", 41, "2024-01-19 14:43:48"),
                (27, 27, "developer_status_request", "DanHay@gmail.com", "approved", "2024-01-27 14:44:48", 41, "2024-01-29 14:45:48"),
                (28, 28, "developer_status_request", "RimaBrek@gmail.com", "approved", "2024-02-11 14:46:48", 41, "2024-02-16 14:47:48"),
                (29, 29, "developer_status_request", "ClementMarcou@gmail.com", "approved", "2024-02-17 14:48:48", 41, "2024-02-19 14:49:48"),
                (30, 30, "developer_status_request", "CraigLafferty@gmail.com", "approved", "2024-02-24 14:50:48", 41, "2024-02-27 14:51:48"),
                (31, 31, "developer_status_request", "MarkLampert@gmail.com", "approved", "2024-03-06 14:52:48", 41, "2024-03-11 14:53:48"),
                (32, 32, "developer_status_request", "AshleyCheng@gmail.com", "approved", "2024-03-21 14:54:48", 41, "2024-03-27 14:55:48"),
                (33, 33, "developer_status_request", "ChrisRoberts@gmail.com", "approved", "2024-03-26 14:56:48", 41, "2024-04-02 14:57:48"),
                (34, 34, "developer_status_request", "PedroCamacho@gmail.com", "approved", "2024-04-06 14:58:48", 41, "2024-04-12 14:59:48"),
                (35, 35, "developer_status_request", "KenzoTsujimoto@gmail.com", "approved", "2024-04-17 14:01:48", 41, "2024-04-22 14:02:48"),
                (36, 36, "developer_status_request", "TokuroFujiwara@gmail.com", "approved", "2024-04-28 14:03:48", 41, "2024-04-29 14:04:48"),
                (37, 37, "developer_status_request", "JohanAndersson@gmail.com", "approved", "2024-05-13 14:05:48", 41, "2024-05-14 14:06:48"),
                (38, 38, "developer_status_request", "DanLind@gmail.com", "approved", "2024-05-27 14:07:48", 41, "2024-06-02 14:08:48"),
                (39, 39, "developer_status_request", "LindaKiby@gmail.com", "approved", "2024-06-01 14:09:48", 41, "2024-06-04 14:10:48"),
                (40, 40, "developer_status_request", "RobTop@gmail.com", "approved", "2024-06-11 14:11:48", 41, "2024-06-16 14:12:48"),
            ]
            
            insert_query = "INSERT INTO AdminNotifications (user_id, target_user_id, notification_type, message, status, created_at, reviewed_by_admin_id, reviewed_at) VALUES (%s, %s, %s, %s, %s, %s, %s, %s);"
            db_manager.execute_many_query(insert_query, admin_notifications)
            print("--- Admin Notifications Data Insertion Attempt Complete ---")
            
            break
        
        elif command == 15:
            print("--- Deleting Data ---")
            
            db_manager.clear_specified_table("studios")
            db_manager.clear_specified_table("users")
            db_manager.clear_specified_table("developers")
            db_manager.clear_specified_table("game_studios")
            db_manager.clear_specified_table("games")
            db_manager.clear_specified_table("developers_games")
            db_manager.clear_specified_table("studioapplications")
            db_manager.clear_specified_table("purchases")
            db_manager.clear_specified_table("purchases_items")
            db_manager.clear_specified_table("reviews")
            db_manager.clear_specified_table("reviewcomments")
            db_manager.clear_specified_table("genres")
            db_manager.clear_specified_table("game_genres")
            db_manager.clear_specified_table("game_platforms")
            db_manager.clear_specified_table("platforms")
            db_manager.clear_specified_table("adminnotifications")
            
            print("--- The Data is Successfully Deleted ---")
            break
        
        elif command == 16:
            print("--- Add Funds to User Account ---")
            target_user_id = None
            while target_user_id is None:
                try:
                    user_id_input = input("Enter User ID to add funds to: ").strip()
                    if not user_id_input: continue
                    target_user_id = int(user_id_input)
                except ValueError:
                    print("Invalid User ID. Please enter a number.")

            amount = None
            while amount is None:
                try:
                    amount_input = input(f"Enter amount to add for user ID {target_user_id}: ").strip().replace(',', '.')
                    if not amount_input: continue
                    amount_decimal = decimal.Decimal(amount_input)
                    if amount_decimal <= 0:
                        print("Amount must be positive.")
                    else:
                        amount = amount_decimal
                except (ValueError, decimal.InvalidOperation):
                    print("Invalid amount. Please enter a valid number (e.g., 100.50).")

            if db_manager.add_funds(target_user_id, amount):
                print(f"--- Successfully added {amount:.2f} to user ID {target_user_id} ---")
            else:
                print(f"--- Failed to add funds to user ID {target_user_id} ---")
            break

        else:
            print("You've wrote an unexisting command! Try again: ", end="")    
            
    
def hash_password(password):
    password_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt()
    hased = bcrypt.hashpw(password_bytes, salt)
    return hased.decode()

if __name__ == '__main__':
    main()