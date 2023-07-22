from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import mysql.connector

app = FastAPI()
security = HTTPBasic()

# Replace these with your actual database credentials
db_config = {
    "host": "localhost",
    "user": "root",
    "password": "14217razh",
    "database": "users"
}

def get_db():
    db = mysql.connector.connect(**db_config)
    return db

def authenticate_user(credentials: HTTPBasicCredentials = Depends(security), db: mysql.connector.connection.MySQLConnection = Depends(get_db)):
    cursor = db.cursor()
    query = "SELECT username, password FROM users WHERE username=%s"
    cursor.execute(query, (credentials.username,))
    user = cursor.fetchone()

    if user is None or credentials.password != user[1]:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return user[0]

@app.post("/login/")
def login(user: str = Depends(authenticate_user)):
    return {"message": f"Logged in as {user}"}
