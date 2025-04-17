import bcrypt
from database_manager import DatabaseManager

db_manager = DatabaseManager()

def main():
    print("-------------------------")
    print("1. Insert Specified Data")
    print("2. Delete All Data")
    print("-------------------------")
    print("\nChoose and Enter the command:")
    
    command = 0
    while True:
        try:
            command = int(input())
        except:
            print("You've wrote a wrong command! Try again: ", end="")
            continue
    
        if command == 1:
            users_data = [
                # --- Terraria --- #
                ("Redigit", "redigit@gmail.com", hash_password("Redigit"), "2012-06-17"),
                ("Cenx", "Cenx@gmail.com", hash_password("Cenx"), "2016-08-05"),
                ("Loki", "Loki@gmail.com", hash_password("Loki"), "2015-07-02"),
                ("FoodBarbarian", "FoodBarbarian@gmail.com", hash_password("FoodBarbarian"), "2016-09-03"),
                
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
            print("--- Deleting Data ---")
            
            db_manager.clear_specified_table("users")
            
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