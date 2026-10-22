import json
import pandas as pd
from .schema import KOLOM_ALL

def load_and_format(filepath, prefix):
    df = pd.read_csv(filepath, sep=r'\s+', header=None, names=KOLOM_ALL)
    df['unit'] = prefix + "_" + df['unit_asli'].astype(str)
    df = df.drop(columns=['unit_asli'])
    return df

def load_splits(filepath='data/splits.json'):
    with open(filepath, 'r') as f:
        return json.load(f)
