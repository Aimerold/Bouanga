from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from .config import settings
from .database import Base, engine
from .routers import auth, contact
from .routers.contact import limiter


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Crée les tables si elles n'existent pas encore (suffisant en dev ;
    # en prod, utilise Alembic pour gérer les migrations proprement).
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Aimerold BOUANGA",
    description="",
    version="1.0.0",
    lifespan=lifespan,
)

# --- Rate limiting (anti-spam sur l'endpoint public /contact) ---
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# --- CORS : autorise uniquement le frontend React déclaré dans .env ---
origins = [
    "http://localhost:3000",
    "http://localhost:5173",
    "https://aimeroldbouanga.vercel.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# --- Routes ---
app.include_router(auth.router)
app.include_router(contact.router)


@app.get("/health", tags=["health"])
def health_check():
    return {"status": "ok"}
