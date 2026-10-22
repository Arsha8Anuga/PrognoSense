import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from . import config
from .deps import BUNDLE, muat_model
from .logging_mw import RequestLoggingMiddleware
from .routers import analisis, armada, prediksi


@asynccontextmanager
async def lifespan(app):
    os.makedirs(config.LOG_DIR, exist_ok=True)
    muat_model()          # sekali saat startup (Kontrak 5)
    yield


app = FastAPI(title='PrognoSense API', version='1.0.0', lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=[os.getenv('CORS_ORIGIN', '*')], allow_methods=['*'], allow_headers=['*'])
app.add_middleware(RequestLoggingMiddleware)


@app.get('/health', tags=['Health'])
def health():
    return {'status': 'ok', 'model_version': BUNDLE.get('versi'), 'dimuat': BUNDLE.get('dimuat')}


app.include_router(armada.router, prefix='/api', tags=['Armada'])
app.include_router(analisis.router, prefix='/api', tags=['Analisis'])
app.include_router(prediksi.router, prefix='/api', tags=['Prediksi'])
