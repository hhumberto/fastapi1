from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from datetime import datetime, timedelta
import jwt
import random
from passlib.hash import bcrypt

SECRET_KEY = "AAx45.ZeRA"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

app = FastAPI()

# @app.get("/")
# async def root():
#     return {"message": "Hello World"}

# @app.get('/random')
# async def get_random():
#     rn:int = random.randrange(100)
#     return {'Random number': rn, "Otros": 'Otros datos'}

# @app.get('/random/{limit}')
# async def otroRandom(limit: int):
#     rn:int = random.randint(0, limit)
#     return {'Numeros enteros random ': rn, 'Otro': "Hello World"}



# Sample user model (Replace this with your actual User model)
fake_users_db = {
    "user1": {
        "username": "user1",
        "hashed_password": "$2b$12$GKlC3.2D/bQ8PaLp.pZVMeEnwBGSeW6DBL2zBxSNHd4RJVNKQH6am",  # 'password'
    }
}

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_user(username: str):
    if username in fake_users_db:
        user_dict = fake_users_db[username]
        return user_dict
    return None


def authenticate_user(username: str, password: str):
    user = get_user(username)
    if not user or not verify_password(password, user["hashed_password"]):
        return False
    return user


def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


@app.post("/token")
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    # user = authenticate_user(form_data.username, form_data.password)
    # if not user:
    #     raise HTTPException(
    #         status_code=status.HTTP_401_UNAUTHORIZED,
    #         detail="Invalid credentials",
    #         headers={"WWW-Authenticate": "Bearer"},
    #     )

    # access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    # access_token = create_access_token(data={"sub": user["username"]}, expires_delta=access_token_expires)
    return {"access_token": form_data.username + 'token'}


@app.get("/")
async def protected_route(token: str = Depends(oauth2_scheme)):
    return { "token": token}
