import bcrypt
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
    print("11. Delete Specified Data")
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
                ("Redigit", "redigit@gmail.com", hash_password("Redigit"), "2009-06-17"), # have special rights in the game page
                ("Cenx", "Cenx@gmail.com", hash_password("Cenx"), "2013-08-05"), # have special rights in the game page
                ("Loki", "Loki@gmail.com", hash_password("Loki"), "2012-07-02"),
                ("FoodBarbarian", "FoodBarbarian@gmail.com", hash_password("FoodBarbarian"), "2014-09-03"),
                
                # --- Don't Starve Together  --- #
                ("MatthewMarteinsson", "MatthewMarteinsson@gmail.com", hash_password("MatthewMarteinsson"), "2011-03-26"),
                ("BryceDoig", "BryceDoig@gmail.com", hash_password("BryceDoig"), "2013-05-11"), 
                ("AlexSavin", "AlexSavin@gmail.com", hash_password("AlexSavin"), "2014-03-21"),
                
                # --- Astroneer --- #
                ("AaronBiddlecom", "AaronBiddlecom@gmail.com", hash_password("AaronBiddlecom"), "2011-11-01"),
                ("AdamBromell", "AdamBromell@gmail.com", hash_password("AdamBromell"), "2012-12-16"),
                ("AndreMaguire", "AndreMaguire@gmail.com", hash_password("AndreMaguire"), "2011-09-28"),
                
                # --- Factorio --- #
                ("MichalKovarik", "MichalKovarik@gmail.com", hash_password("MichalKovarik"), "2012-02-09"),
                ("Tomax", "Tomax@gmail.com", hash_password("Tomax"), "2013-05-30"), # have special rights in the game page
                ("DanStevens", "DanStevens@gmail.com", hash_password("DanStevens"), "2014-01-07"),
                
                # --- Stardew Valley --- #
                ("EricBarone", "EricBarone@gmail.com", hash_password("EricBarone"), "2015-02-15"), # have special rights in the game page
                
                # --- Sid Meier's Civilization VI --- #
                ("EdBeach", "EdBeach@gmail.com", hash_password("EdBeach"), "2010-08-09"),
                ("DennisShirk", "DennisShirk@gmail.com", hash_password("DennisShirk"), "2010-09-14"), # have special rights in the game page
                ("AndrewFrederiksen", "AndrewFrederiksen@gmail.com", hash_password("AndrewFrederiksen"), "2010-09-21"),
                
                ("ChristophHartmann", "ChristophHartmann@gmail.com", hash_password("ChristophHartmann"), "2008-04-12"),
                ("JohnChowanec", "JohnChowanec@gmail.com", hash_password("JohnChowanec"), "2008-05-03"),
                ("MelissaMiller", "MelissaMiller@gmail.com", hash_password("MelissaMiller"), "2008-07-06"),
            
                # --- Marvel Rivals --- #
                ("ThaddeusSasser", "ThaddeusSasser@gmail.com", hash_password("ThaddeusSasser"), "2013-05-15"),
                ("James", "James@gmail.com", hash_password("James"), "2017-07-05"), # have special rights in the game page
                ("GuangyunChen", "GuangyunChen@gmail.com", hash_password("GuangyunChen"), "2018-10-29"),
                
                # --- Hades II --- #
                ("WillTurnbull", "WillTurnbull@gmail.com", hash_password("WillTurnbull"), "2015-01-19"), # have special rights in the game page
                ("AmirRao", "AmirRao@gmail.com", hash_password("AmirRao"), "2015-04-02"),
                ("GregKasavin", "GregKasavin@gmail.com", hash_password("GregKasavin"), "2016-01-04"),
                
                # --- Project Odyssey --- #
                ("DanHay", "DanHay@gmail.com", hash_password("DanHay"), "2011-01-10"),
                ("RimaBrek", "RimaBrek@gmail.com", hash_password("RimaBrek"), "2011-03-14"), # have special rights in the game page
                ("ClementMarcou", "ClementMarcou@gmail.com", hash_password("ClementMarcou"), "2011-05-09"),
                
                # --- The Elder Scrolls VI --- #
                ("CraigLafferty", "CraigLafferty@gmail.com", hash_password("CraigLafferty"), "2009-10-24"),
                ("MarkLampert", "MarkLampert@gmail.com", hash_password("MarkLampert"), "2008-09-11"),
                ("AshleyCheng", "AshleyCheng@gmail.com", hash_password("AshleyCheng"), "2010-12-27"),
                
                # --- Star citizen --- #
                ("ChrisRoberts", "ChrisRoberts@gmail.com", hash_password("ChrisRoberts"), "2014-06-13"),
                ("PedroCamacho", "PedroCamacho@gmail.com", hash_password("PedroCamacho"), "2015-02-18"), # have special rights in the game page
                
                # --- Deep down --- #
                ("KenzoTsujimoto", "KenzoTsujimoto@gmail.com", hash_password("KenzoTsujimoto"), "2009-01-09"), # have special rights in the game page
                ("TokuroFujiwara", "TokuroFujiwara@gmail.com", hash_password("TokuroFujiwara"), "2010-08-07"),
                
                # --- Hearts of Iron IV --- #
                ("JohanAndersson", "JohanAndersson@gmail.com", hash_password("JohanAndersson"), "2015-03-04"),
                ("DanLind", "DanLind@gmail.com", hash_password("DanLind"), "2015-06-05"), # have special rights in the game page
                ("LindaKiby", "LindaKiby@gmail.com", hash_password("LindaKiby"), "2014-03-12"),
                
                # --- Geometry Dash --- #
                ("RobTop", "RobTop@gmail.com", hash_password("RobTop"), "2011-04-18"), # have special rights in the game page
            ]
            
            print("--- Inserting Users Data ---")
            insert_query = "INSERT INTO Users (username, email, password_hash, registration_date) VALUES (%s, %s, %s, %s);"
            
            db_manager.execute_many_query(insert_query, users_data)
            
            print("--- The Data is Successfully Inserted ---")
            break
        elif command == 2:
            
            studios_data = [
                # --- Terraria --- #
                ("Re-Logic", "https://re-logic.com/", "re-logic_icon_1.jpg", "United States", "Best known for the Terraria franchise - the revolutionary 2D Sandbox Adventure that has entertained millions of gamers worldwide - Re-Logic seeks to showcase and evolve the limits of what Indie gaming can be!", "2011-01-24"),
                
                # --- Don't Starve Together --- #
                ("Klei", "https://www.klei.com/", "klei_icon_2.jpg", "Canada", "It Rhymes With Play", "2005-07-01"),
                
                # --- Astroneer --- #
                ("System Era Softworks", "https://www.systemera.net/", "system_era_softworks_icon_3.jpg", "United States", "System Era Softworks is a small development studio led by veteran game developers headquartered in Seattle, Washington. We are currently working on our first game, Astroneer.", "2014-03-07"),
                
                # --- Factorio --- #
                ("Wube Software", None, "wube_software_icon_4.jpg", "Czech Republic", "Wube Software is a team of passionate professionals dedicated to creating exceptional games.", "2014-09-03"),
                
                # --- Stardew Valley --- #
                ("ConcernedApe", None, "concernedape_icon_5.jpg", "United States", "ConcernedApe is the moniker of Eric Barone, a solo game developer based in Seattle, WA.", "2012-05-05"),
                
                # --- Sid Meier's Civilization VI --- #
                ("Firaxis Games", "https://firaxis.com/", "firaxis_games_icon_6.jpg", "United States", "Firaxis Games is a world-renowned game development studio with an unwavering mission to \"build games that stand the test of time\".", "1996-05-12"),
                
                ("2K", "https://2k.com/", "2k_icon_7.jpg", "United States", "2K develops and publishes critically-acclaimed franchises such as BioShock, Borderlands, Sid Meier’s Civilization, XCOM, WWE 2K, and NBA 2K.", "2005-01-25"),
                
                # --- Marvel Rivals --- #
                ("NetEaseGames", "https://www.neteasegames.com/", "net_ease_games_icon_8.jpg", "China", "NetEase Games is the gaming division of NetEase, Inc., a major Chinese tech company. It focuses on developing and publishing video games across various platforms, including mobile, PC, and consoles.", "2001-09-08"),
                
                # --- Hades II --- #
                ("Supergiant Games", "https://www.supergiantgames.com/", "supergiant_games_icon_9.jpg", "United States", "We make games that spark your imagination like the games you played as a kid.", "2009-07-27"),
                
                # --- Project Odyssey --- #
                ("Blizzard Entertainment", "https://www.blizzard.com/en-us/", "blizzard_entertainment_icon_10.jpg", "United States", "Dedicated to creating the most epic entertainment experiences... ever.", "1991-02-08"),
                
                # --- The Elder Scrolls VI --- #
                ("Bethesda Softworks", "https://bethesda.net/en/dashboard", "bethesda_softworks_icon_11.jpg", "United States", "Bethesda Softworks is an award-winning development team renowned worldwide for its groundbreaking work on the The Elder Scrolls and Fallout series.", "1986-06-28"),
                
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
                (1, 1, "redigit@gmail.com"), # have special rights in the game page
                (2, 1, "Cenx@gmail.com"), # have special rights in the game page
                (3, 1, "Loki@gmail.com"),
                (4, 1, "FoodBarbarian@gmail.com"),
                
                # --- Don't Starve Together  --- #
                (5, 2, "MatthewMarteinsson@gmail.com"),
                (6, 2, "BryceDoig@gmail.com"), # have special rights in the game page
                (7, 2, "AlexSavin@gmail.com"),
                
                # --- Astroneer --- #
                (8, 3, "AaronBiddlecom@gmail.com"),
                (9, 3, "AdamBromell@gmail.com"),
                (10, 3, "AndreMaguire@gmail.com"), # have special rights in the game page
                
                # --- Factorio --- #
                (11, 4, "MichalKovarik@gmail.com"),
                (12, 4, "Tomax@gmail.com"), # have special rights in the game page
                (13, 4, "DanStevens@gmail.com"),
                
                # --- Stardew Valley --- #
                (14, 5, "EricBarone@gmail.com"), # have special rights in the game page
                
                # --- Sid Meier's Civilization VI --- #
                (15, 6, "EdBeach@gmail.com"),
                (16, 6, "DennisShirk@gmail.com"), # have special rights in the game page
                (17, 6, "AndrewFrederiksen@gmail.com"),
                
                (18, 7, "ChristophHartmann@gmail.com"),
                (19, 7, "JohnChowanec@gmail.com"),
                (20, 7, "MelissaMiller@gmail.com"),
            
                # --- Marvel Rivals --- #
                (21, 8, "ThaddeusSasser@gmail.com"),
                (22, 8, "James@gmail.com"), # have special rights in the game page
                (23, 8, "GuangyunChen@gmail.com"),
                
                # --- Hades II --- #
                (24, 9, "WillTurnbull@gmail.com"), # have special rights in the game page
                (25, 9, "AmirRao@gmail.com"),
                (26, 9, "GregKasavin@gmail.com"),
                
                # --- Project Odyssey --- #
                (27, 10, "DanHay@gmail.com"),
                (28, 10, "RimaBrek@gmail.com"), # have special rights in the game page
                (29, 10, "ClementMarcou@gmail.com"),
                
                # --- The Elder Scrolls VI --- #
                (30, 11, "CraigLafferty@gmail.com"), # have special rights in the game page
                (31, 11, "MarkLampert@gmail.com"),
                (32, 11, "AshleyCheng@gmail.com"),
                
                # --- Star citizen --- #
                (33, 12, "ChrisRoberts@gmail.com"),
                (34, 12, "PedroCamacho@gmail.com"), # have special rights in the game page
                
                # --- Deep down --- #
                (35, 13, "KenzoTsujimoto@gmail.com"), # have special rights in the game page
                (36, 13, "TokuroFujiwara@gmail.com"),
                
                # --- Hearts of Iron IV --- #
                (37, 14, "JohanAndersson@gmail.com"),
                (38, 14, "DanLind@gmail.com"), # have special rights in the game page
                (39, 14, "LindaKiby@gmail.com"),
                
                # --- Geometry Dash --- #
                (40, 15, "RobTop@gmail.com") # have special rights in the game page
            ]
            
            print("--- Inserting Developers Data ---")
            insert_query = "INSERT INTO Developers (user_id, studio_id, contact_email) VALUES (%s, %s, %s);"
            
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
                ("Geometry Dash", "Jump and fly your way through danger in this rhythm-based action platformer!", 124.00, "2013-08-13", "geometry_dash_icon_15.jpg", "Released", "2013-08-13", "2025-04-05")
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
                (13, 23), (13, 7), (13, 27), (14, 24), (14, 25), (14, 17), (14, 26), (14, 5)
            ]
            
            print("--- Inserting Game_Genres Data ---")
            insert_query = "INSERT INTO Game_Genres (game_id, genre_id) VALUES (%s, %s);"
            db_manager.execute_many_query(insert_query, game_genres)
            break
        
        elif command == 8:
            game_platforms = [
                (1, 1), (1, 2), (1, 3), (1, 4), (2, 1), (2, 2), (2, 3), (3, 1), (4, 1), (4, 2), (4, 3), (5, 1), (5, 2), (5, 3), (5, 4), (6, 1),
                (6, 2), (6, 3), (7, 1), (8, 1), (10, 1), (11, 1), (13, 1), (13, 2), (13, 3), (14, 1), (14, 4)
            ]
            
            print("--- Inserting Game_Platforms Data ---")
            insert_query = "INSERT INTO Game_Platforms (game_id, platform_id) VALUES (%s, %s);"
            db_manager.execute_many_query(insert_query, game_platforms)
            break
        
        elif command == 9:
            developer_games = [
                (1, 1), (2, 1), (6, 2), (10, 3), (12, 4), (14, 5), (16, 6),
                (22, 7), (24, 8), (28, 9), (30, 10), (34, 11), (35, 12), (38, 13), (40, 14)
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
                (13, 14, 'Developer'), (13, 14, 'Publisher'), (14, 15, 'Developer'), (14, 15, 'Publisher')
            ]
            
            print("--- Inserting Game_Studios Data ---")
            insert_query = "INSERT INTO Game_Studios (game_id, studio_id, role) VALUES (%s, %s, %s);"
            db_manager.execute_many_query(insert_query, game_studios)
            break
            
        elif command == 11:
            print("--- Deleting Data ---")
            
            db_manager.clear_specified_table("game_g1enres")
            
            print("--- The Data is Successfully Deleted ---")
            break;
        else:
            print("You've wrote an unexisting command! Try again: ", end="")
            
    
def hash_password(password):
    password_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt()
    hased = bcrypt.hashpw(password_bytes, salt)
    return hased.decode()

if __name__ == '__main__':
    main()