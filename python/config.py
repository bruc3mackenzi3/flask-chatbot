import pathlib


# Using pathlib get absolute path of DB file
# This removes the constraint of running from a specific directory
DB_PATH = str(pathlib.Path(__file__).parent.absolute()) + "/../database.db"
