import asyncio
import os
import sys

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.routers import auth, lists, todos, users, guest, template_items

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

app = FastAPI()

# CORS: configurable via env FRONTEND_ORIGINS (comma-separated)
# Example: FRONTEND_ORIGINS="https://seu-app.vercel.app,https://www.seu-dominio.com"
env_origins = os.getenv('FRONTEND_ORIGINS')
if env_origins:
    origins = [o.strip() for o in env_origins.split(',') if o.strip()]
else:
    origins = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router)
app.include_router(auth.router)
app.include_router(todos.router)
app.include_router(lists.router)
app.include_router(guest.router)
app.include_router(template_items.router)


@app.get('/healthz')
async def healthz():
    return {'status': 'ok'}
