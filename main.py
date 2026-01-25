from fastapi import FastAPI, HTTPException, Query
from typing import List, Dict, Any
import datetime
import pandas as pd
import json
import numpy as np

from typing import Optional


app = FastAPI(title="Banking Transactions API", version="1.0.0")

# --- CATEGORIE 1: TRANSACTIONS (Routes 1-8) --- [cite: 50]

@app.get("/api/transactions/{id}")
async def get_transactions(id:int):
    """Liste paginée avec filtres [cite: 52-54]."""
    df = pd.read_csv('transactions_data.csv')
    return df[df['id']==id].to_json()


@app.get("/api/abc")
async def get_transactions(page: int = 1, limit: int = 10, type: str = None, 
                           isFraud = True, min_amount: float = None, max_amount: float = None):
    """Liste paginée avec filtres [cite: 52-54]."""
    df = pd.read_csv('transactions_data.csv')
    # begin_line = limit * (page - 1)
    # end_line = begin_line + limit

    filtered_data = df

    if type: 
       filtered_data =  filtered_data[filtered_data["type"] == type]
    
    if min_amount is not None: 
       filtered_data = filtered_data[filtered_data["amount"] >= min_amount] 
    
    if max_amount is not None: 
       filtered_data = filtered_data[filtered_data["amount"] <= max_amount]
     # 2. Logique de pagination 
    start = (page - 1) * limit 
    end = start + limit 
    paginated_data = filtered_data.iloc[start:end]

    transactions = paginated_data.to_dict(orient = 'records')

    return { "page": page, "transactions": transactions }

    # json_string = "{'page': " + str(page) + ", 'transactions': " + df.iloc[begin_line:end_line, :].to_json(orient='records') + "}"
    # return  json_string


@app.get("/api/transactions")
async def get_transactions(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=1000),
    txn_type: Optional[str] = None,
    is_fraud: Optional[bool] = None,
    min_amount: Optional[float] = None,
    max_amount: Optional[float] = None
):
    """
    Liste paginée avec filtres.
    - Filtres: type, is_fraud, min_amount, max_amount
    - Pagination: page, limit
    - Retourne: transactions + métadonnées
    """
    # 1) Charger les données
    df = pd.read_csv("transactions_data.csv", na_values=["", "NA", "NaN", "null", None])

    # 2) Filtrage
    filtered = df


    # 1) Harmoniser les valeurs non conformes JSON
    filtered = filtered.replace([np.inf, -np.inf], np.nan)
    # 2) Convertir tous les NaN en None (JSON null)
    filtered = filtered.where(pd.notna(filtered), None)

    if min_amount is not None:
        # S'assurer que la colonne est numérique
        filtered = filtered[pd.to_numeric(filtered["amount"], errors="coerce") >= min_amount]

    if max_amount is not None:
        filtered = filtered[pd.to_numeric(filtered["amount"], errors="coerce") <= max_amount]

    # 3) Pagination
    total = len(filtered)
    start = (page - 1) * limit
    end = start + limit

    # Éviter un slicing hors bornes et cas page trop grande
    if start >= total and total > 0:
        return {
            "page": page,
            "limit": limit,
            "total": total,
            "pages": (total + limit - 1) // limit,
            "has_next": False,
            "has_prev": page > 1,
            "transactions": []
        }

    paginated = filtered.iloc[start:end]
    transactions = paginated.to_dict(orient="records")

    # 4) Métadonnées
    pages = (total + limit - 1) // limit if total > 0 else 1
    has_next = page < pages
    has_prev = page > 1

    return {
        "page": page,
        "limit": limit,
        "total": total,
        "pages": pages,
        "has_next": has_next,
        "has_prev": has_prev,
        "transactions": transactions
    }
