from cs50 import SQL

db = SQL("sqlite:///meet_n_eat.db")

if db.execute("SELECT temp_code FROM users WHERE username = ?", "test4571676259")[0]["temp_code"] != 0:
    print("success")