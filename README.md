# **Universal Games Store**

A desktop application for browsing, purchasing, and managing computer games, featuring a dedicated portal for game studios and developers, and an admin panel for system management.
This term paper is a store for games

## **Table of Contents**
- [Key Features](#key-features)
- [Technologies Used](#technologies-used)
- [Project Structure](#project-structure)
- [Setup and Running](#setup-and-running)
- [Future Enhancements](#future-enhancements)
- [Author](#author)
## Key Features
- ### For Users:
    - User registration and login.
    - Game catalog browsing with sorting options (by title, price).
    - Detailed game information view (description, genres, platforms, developers, publishers, reviews).
    - Game purchasing (with balance check).
    - Viewing personal library of purchased games.
    - Ability to write game reviews and comment on other reviews.
    - Adding funds to user balance (implemented via admin panel, but can be mentioned as a feature).
    - Deleting own user account.
- ### For Developers/Studios:
    - Ability to apply for developer status.
    - Ability to apply to join an existing studio.
    - (planned) Ability to create their game pages.
    - (planned) Studio member management (for studio admins).
    - Ability to leave a studio.
- ### For App Admins:
    - User management panel (view, search, sort, ban/unban, add funds).
    - Studio management panel (view, search, sort).
    - Game management panel (view, search, sort, edit description/price).
    - Reviewing and processing developer status requests.
- ### General:
    - Data persistence using a PostgreSQL database.
    - Graphical User Interface (GUI) built with Tkinter.
    - Test data population via a separate script.
## Technologies Used
- **Programming Language:** Python 3.12.3
- **Graphical User Interface (GUI):** Tkinter (ttk)
- **Database:** PostgreSQL
- **DB Interaction:** psycopg2
- **Password Hashing:** bcrypt
- **Image Manipulation:** Pillow (PIL)
- **Configuration Management:** json, os

## Project Structure
Briefly describe the main files and folders:
```
.
├── main.py
├── database_manager.py
├── upload_data.py
├── config.json
├── resources/
│   ├── games_icons/
│   └── studios_icons/
└── ui/
    ├── __init__.py
    ├── login.py
    ├── registration.py
    ├── store.py
    ├── game_details.py
    ├── library.py
    ├── studios_tab.py
    ├── studio_details.py
    ├── utils.py
    └── admin/
        ├── __init__.py
        ├── admin_utils.py
        ├── user_management_panel.py
        ├── studio_management_panel.py
        ├── game_management_panel.py
        └── notifications_panel.py
```
## Setup and Running
### 1. Clone the repository:
```
git clone https://github.com/YaroslavRomanenko/online-computer-game-store
cd online-computer-game-store
```
### 2. Install dependencies:
```
pip install -r requirements.txt
```
### 3. Set up PostgreSQL Database:
   - Ensure PostgreSQL is installed and running.
   - Create a new database for the project.
   - Create the config.json file with your database connection details (host, port, dbname, user, password).
   - Run the script to create database tables
### 4. Load Test Data:
```
python upload_data.py
```
### 5. Run the application:
```
python main.py
```
### 6. Test Administrator Account:
   - Username: Admin
   - Password: Admin

## Future Enhancements
 - Allow developers/studios to create and edit their games through the UI.
 - Implement game filtering by genre/platform.
 - Add a wishlist feature.
 - Add a cart
 - Expand admin functionalities (e.g., content management, delete reviews and comments).
 - Interface localization.

## Author
 - Yaroslav Romanenko
 - GitHub: https://github.com/YaroslavRomanenko
 - LinkedIn: www.linkedin.com/in/yaroslav-romanenko-43b990345
 - Email: yaroslavromanenko456@gmail.com
