from fastapi import FastAPI
import random
app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get('/random')
async def get_random():
    rn:int = random.randrange(100)
    return {'Random number': rn, "Otros": 'Otros datos'}

@app.get('/random/{limit}')
async def otroRandom(limit: int):
    rn:int = random.randint(0, limit)
    return {'Numeros enteros random ': rn, 'Otro': "Hello World"}
