import bcrypt
import math

first_password = "qwerty1234"
first_password_bytes = first_password.encode("utf-8")

second_password = "qwerty1234"
second_password_bytes = second_password.encode("utf-8")

salt = bcrypt.gensalt()
hashed = bcrypt.hashpw(first_password_bytes, salt)

if bcrypt.checkpw(second_password_bytes, hashed):
    print(True)
else:
    print(False)

print(f"Hashed password: {hashed.decode()}")

for i in range(0, len(hashed)):
    i += 1
    
print(i)