import json
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from tortoise import fields
from datetime import datetime, timedelta
import mysql.connector
from mysql.connector import errorcode
from tortoise.models import Model
from tortoise.contrib.pydantic import pydantic_model_creator

JWT_SECRET = 'mysecret'
class User(Model):
    
    username = fields.CharField(50, unique=True)
    password = fields.CharField(50, unique=True)
    


User_Pydantic = pydantic_model_creator(User, name='User')



db_config = {
    "user": "root",
    "password": "14217razh",
    "host": "192.168.0.190",
    "port": "3306",
    "database": "users",
}
def get_db():
    try:
        db_conn = mysql.connector.connect(
            user="root",
            password="14217razh",
            host="192.168.0.190",
            database="users",
        )
        print('Successful connection')
        yield db_conn
        db_conn.close()
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            raise HTTPException(status_code=500, detail="Invalid database credentials.")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            raise HTTPException(status_code=500, detail="Database does not exist.")
        # else:
        #     raise HTTPException(status_code=500, detail="XXXXXDatabase connection error.")






class UserCreate(BaseModel):
    username: str
    password: str
    id: int
    name: str
    email: str
class UserLogin(BaseModel):
    username: str
    password: str
    
class User(UserCreate):
    id: int

class Token(BaseModel):
    access_token: str
    token_type: str
    
# Password hashing
#
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

# end points
#

app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")

@app.post("/signup/", response_model=User)
def signup(user: UserCreate, db: mysql.connector.connection.MySQLConnection = Depends(get_db)):
    user.password = hash_password(user.password)
    cursor = db.cursor()
    insert_query = "INSERT INTO users (username, password, name, email) VALUES (%s, %s, %s, %s)"
    data = (user.username, user.password, user.name, user.email)
    cursor.execute(insert_query, data)
    db.commit()
    user.id = cursor.lastrowid
    return user

@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: mysql.connector.connection.MySQLConnection = Depends(get_db)):
    # try:
        # user.password = hash_password(user.password)
        cursor = db.cursor()
        get_query = "SELECT username, password FROM users WHERE (username == %s)"
        data = (form_data.username, form_data.password)
        cursor.execute(get_query, data)
        # db.commit()
        print('Go oon through here')
        user = cursor.fetchone()
        return user
    # except mysql.connector.Error as err:
    #     raise HTTPException(status_code=500, detail="Database query error.")



@app.post("/token")
def generate_token(form_data: OAuth2PasswordRequestForm = Depends(), db: mysql.connector.connection.MySQLConnection = Depends(get_db)):
    cursor = db.cursor()
    select_query = "SELECT username, password FROM users WHERE username = %s"
    data = (form_data.username,)
    cursor.execute(select_query, data)
    user = cursor.fetchone()
    print("User::::::: ", json.loads(json.dumps(user)))
    # if not user or not verify_password(form_data.password, user[1]):
    #     raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials.")
    # access_token_expires = timedelta(minutes=30)
    
    # access_token = {
    #     "sub": user[0],
    #     "exp": datetime.utcnow() + access_token_expires
    # }
    
    # print(access_token)
    user = json.loads(json.dumps(user))
    
    obj_user = {'username': user[0], 'password':user[1]}
    
    token = jwt.encode(obj_user, JWT_SECRET)
    return {'access token': token, 'token_type': 'bearer'}
# Token(access_token=access_token, token_type="bearer")

# @app.post("/token")
# async def generate_token(form_data: OAuth2PasswordRequestForm = Depends()):
#     user = await authenticate_user(form_data.username, form_data.password)
#     if not user:
#         return { 'error': 'Invalid credentials'}
#     user_obj = await User_Pydantic.from_tortoise_orm(user)
#     token = jwt.encode(user_obj.dict(), JWT_SECRET)
#     return {'access token': token, 'token_type': 'bearer'}
