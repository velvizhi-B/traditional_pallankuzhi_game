from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import players, games, moves

app = FastAPI(title="Pallankuzhi API", debug=True)

# Allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or ["http://localhost:5173"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Pallankuzhi API"}

app.include_router(players.router)
app.include_router(games.router)
app.include_router(moves.router)


# from fastapi.middleware.cors import CORSMiddleware

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["http://localhost:5173"],  # or wherever your frontend runs
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )
# from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware
# from app.routers import players, games, moves

# app = FastAPI(title="Pallankuzhi API", debug=True)

# # CORS configuration
# origins = [
#     "http://localhost:5173",
#     "http://localhost:5174",
# ]

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=origins,
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # Routers
# app.include_router(players.router)
# app.include_router(games.router)
# app.include_router(moves.router)

# @app.get("/")
# def read_root():
#     return {"message": "Welcome to the Pallankuzhi API"}
