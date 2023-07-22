from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel

app = FastAPI()

# This is a basic example. In a real-world scenario, use a proper data store like a database.
# Store user credentials as a dictionary, with the username as the key and the hashed password as the value.
users_db = {
    "user1": {
        "username": "user1",
        "password": "password1"  # In a real scenario, store the hashed version of the password.
    },
    "user2": {
        "username": "user2",
        "password": "password2"
    }
}


class User(BaseModel):
    username: str
    password: str


# Function to simulate user authentication and return a user object if authenticated.
def authenticate_user(username: str, password: str) -> User:
    if username in users_db and users_db[username]["password"] == password:
        return User(username=username, password=password)
    return None


# Function to generate an access token (for simplicity, it's just the username in this example).
def generate_token(user: User = Depends(authenticate_user)):
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    return {"access_token": user.username, "token_type": "bearer"}


# OAuth2PasswordBearer allows you to get the access token from the request.
# In this example, we're using the "username" as the access token.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@app.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    return {"access_token": user.username, "token_type": "bearer"}


# A protected route that requires authentication using the access token.
@app.get("/protected")
async def protected_route(token: str = Depends(oauth2_scheme)):
    if not authenticate_user(token, token):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    return {"message": "This is a protected route", "user": token}
