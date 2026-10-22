import os

MODEL_DIR = os.getenv('MODEL_DIR', 'models/v1')
DATA_DIR = os.getenv('DATA_DIR', 'data/results')
LOG_DIR = os.getenv('LOG_DIR', 'logs')
RASIO = (50, 100, 200)
BATAS_FILE = 20 * 1024 * 1024
