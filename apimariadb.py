import datetime
from typing import Annotated
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.params import Form
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from jose import jwt, JWTError
import pymysql
from pydantic import BaseModel

from fastapi.security import HTTPBasic, HTTPBasicCredentials
import mysql.connector
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates


# Create FastAPI app
app = FastAPI()
# app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

security = HTTPBasic()
# JWT configurations
SECRET_KEY = "06e7385f9d2613662d9ff55639cce588"  # Replace this with your secret key
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Database configurations
DB_HOST = "192.168.0.190"
DB_USER = "root"
DB_PASSWORD = "14217razh"
DB_NAME = "users"

def get_db():
    db = pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
    )
    return db

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)



class User(BaseModel):
    username: str
    password: str

@app.post("/signup/", response_class=HTMLResponse)
def signup(request: Request, username: Annotated[str, Form()], password: Annotated[str, Form()], db: pymysql.Connection = Depends(get_db)):
#def signup(request: Request, username: Annotated[str, Form()], password: Annotated[str, Form()], user: User, db: pymysql.Connection = Depends(get_db)):
    hashed_password = hash_password(password)
    cursor = db.cursor()
    print('Crea user')
    token = create_access_token(data={"sub": username})
    try:
        cursor.execute(
            "INSERT INTO users (username, password, token) VALUES (%s, %s, %s)",
            (username, hashed_password, token),
        )
        db.commit()
    except pymysql.IntegrityError:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    userCreated = {"request": request, "username": username, "password": password}
    
    return templates.TemplateResponse("usercreated.html", userCreated)
#{"message": "User created successfully"}

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def create_access_token(data: dict):
    to_encode = data.copy()
    expiration = datetime.datetime.utcnow() + datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expiration})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

@app.post("/token/", response_class=HTMLResponse)
async def login_for_access_token(request: Request, username: Annotated[str, Form()], password: Annotated[str, Form()], db: pymysql.Connection = Depends(get_db)):
# def login_for_access_token(username: str, password: str, db: pymysql.Connection = Depends(get_db)):
    cursor = db.cursor()
    await cursor.execute("SELECT username, password FROM users WHERE username = %s", (username,))
    user = cursor.fetchone()
    if user is None or not verify_password(password, user[1]):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    access_token = create_access_token(data={"sub": user[0]})
    updateTOken = ("INSERT INTO users (token) VALUES (%s)", (access_token),)
    try:
        await cursor.execute(
            "UPDATE users SET token = %s WHERE username= %s",(access_token, username),
            
        )
        db.commit()
    except pymysql.IntegrityError:
        raise HTTPException(status_code=400, detail="Cannot connect to database")
    
    print('Paso por aqui')
    usertokens = {"request": request, "user": username, "token": access_token}
    return templates.TemplateResponse("token.html", usertokens)


#

def authenticate_user(credentials: HTTPBasicCredentials = Depends(security), db: mysql.connector.connection.MySQLConnection = Depends(get_db)):
    cursor = db.cursor()
    query = "SELECT username, password FROM users WHERE username=%s"
    cursor.execute(query, (credentials.username,))
    user = cursor.fetchone()
    print(user, credentials.password, user[1])
    if user is None or credentials.password == user[1]:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return user[0]

@app.post("/login/", response_class=HTMLResponse)
def login(request: Request, username: Annotated[str, Form()], password: Annotated[str, Form()], user: str = Depends(authenticate_user)):
    print(username)
    user = user
    return templates.TemplateResponse("index.html", {'request':request, 'user':password})

@app.get('/', response_class=HTMLResponse)
async def index(request: Request):
    userLogeo = {"request": request, "user": "username"}
    return templates.TemplateResponse("index.html", userLogeo)

    
@app.post("/data/", response_class=HTMLResponse)
def datos(request: Request, username: Annotated[str, Form()], password: Annotated[str, Form()], user: str = Depends(authenticate_user)):
    print(username)
    print(user)
    return templates.TemplateResponse("data.html", {'request':request, 'user':username})

