
import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
from src.banking_api.main import app

# Initialisation du client de test
client = TestClient(app)

# --- MOCK DATA (Pour simuler vos CSV/JSON sans les lire) ---
MOCK_TRANSACTIONS = {
    "page": 1, 
    "transactions": [{"id": "tx_001", "amount": 150.0, "type": "PAYMENT"}]
}

MOCK_STATS = {
    "total_transactions": 100, 
    "fraud_rate": 0.01, 
    "avg_amount": 500.0
}

MOCK_FRAUD_PRED = {
    "isFraud": True, 
    "probability": 0.95
}

MOCK_CUSTOMER = {
    "id": "1", 
    "name": "Test User", 
    "transactions_count": 5, 
    "fraudulent": False
}

# --- CATÉGORIE 1 : TRANSACTIONS (Routes 1-8) ---

def test_1_get_transactions():
    """Route 1 : Liste des transactions paginée [cite: 52]"""
    with patch("src.banking_api.services.transactions_service.TransactionsService.fetch_paginated") as mock_get:
        mock_get.return_value = MOCK_TRANSACTIONS
        response = client.get("/api/transactions?page=1&limit=10")
        assert response.status_code == 200
        assert response.json()["page"] == 1
        assert len(response.json()["transactions"]) > 0

def test_2_get_transaction_by_id():
    """Route 2 : Détail d'une transaction [cite: 58]"""
    with patch("src.banking_api.services.transactions_service.TransactionsService.get_by_id") as mock_get:
        mock_get.return_value = {"id": "tx_001", "amount": 100.0}
        response = client.get("/api/transactions/tx_001")
        assert response.status_code == 200
        assert response.json()["id"] == "tx_001"

def test_3_search_transactions():
    """Route 3 : Recherche multicritère (POST) [cite: 60]"""
    payload = {"type": "TRANSFER", "isFraud": 1, "amount_range": [100, 1000]}
    with patch("src.banking_api.services.transactions_service.TransactionsService.search") as mock_search:
        mock_search.return_value = {"results": []}
        response = client.post("/api/transactions/search", json=payload)
        assert response.status_code == 200
        assert "results" in response.json()

def test_4_get_transaction_types():
    """Route 4 : Types de transactions [cite: 65]"""
    with patch("src.banking_api.services.transactions_service.TransactionsService.get_unique_types") as mock_types:
        mock_types.return_value = ["PAYMENT", "TRANSFER"]
        response = client.get("/api/transactions/types")
        assert response.status_code == 200
        assert "PAYMENT" in response.json()

def test_5_get_recent_transactions():
    """Route 5 : Transactions récentes [cite: 67]"""
    with patch("src.banking_api.services.transactions_service.TransactionsService.get_last_n") as mock_recent:
        mock_recent.return_value = {"count": 10, "transactions": []}
        response = client.get("/api/transactions/recent?n=10")
        assert response.status_code == 200

def test_6_delete_transaction():
    """Route 6 : Suppression (Mock) [cite: 69]"""
    with patch("src.banking_api.services.transactions_service.TransactionsService.delete_fictive") as mock_del:
        mock_del.return_value = {"status": "deleted", "id": "tx_999"}
        response = client.delete("/api/transactions/tx_999")
        assert response.status_code == 200
        assert response.json()["status"] == "deleted"

def test_7_get_transactions_by_customer():
    """Route 7 : Transactions par client (Origine) [cite: 71]"""
    with patch("src.banking_api.services.transactions_service.TransactionsService.get_by_origin") as mock_get:
        mock_get.return_value = {"customer_id": "C1", "sent": []}
        response = client.get("/api/transactions/by-customer/C1")
        assert response.status_code == 200

def test_8_get_transactions_to_customer():
    """Route 8 : Transactions vers client (Dest) [cite: 73]"""
    with patch("src.banking_api.services.transactions_service.TransactionsService.get_by_destination") as mock_get:
        mock_get.return_value = {"customer_id": "C1", "received": []}
        response = client.get("/api/transactions/to-customer/C1")
        assert response.status_code == 200

# --- CATÉGORIE 2 : STATISTIQUES (Routes 9-12) ---

def test_9_stats_overview():
    """Route 9 : Vue d'ensemble [cite: 75]"""
    with patch("src.banking_api.services.stats_service.StatsService.get_global_stats") as mock_stats:
        mock_stats.return_value = MOCK_STATS
        response = client.get("/api/stats/overview")
        assert response.status_code == 200
        assert "fraud_rate" in response.json()

def test_10_amount_distribution():
    """Route 10 : Histogramme [cite: 83]"""
    with patch("src.banking_api.services.stats_service.StatsService.get_histogram") as mock_hist:
        mock_hist.return_value = {"bins": ["0-100"], "counts": [50]}
        response = client.get("/api/stats/amount-distribution")
        assert response.status_code == 200

def test_11_stats_by_type():
    """Route 11 : Stats par type [cite: 93]"""
    with patch("src.banking_api.services.stats_service.StatsService.get_stats_per_type") as mock_type:
        mock_type.return_value = [{"type": "PAYMENT", "count": 10}]
        response = client.get("/api/stats/by-type")
        assert response.status_code == 200

def test_12_stats_daily():
    """Route 12 : Stats par jour [cite: 99]"""
    with patch("src.banking_api.services.stats_service.StatsService.get_daily_volume") as mock_daily:
        mock_daily.return_value = {"days": [], "volumes": []}
        response = client.get("/api/stats/daily")
        assert response.status_code == 200

# --- CATÉGORIE 3 : FRAUDE (Routes 13-15) ---

def test_13_fraud_summary():
    """Route 13 : Résumé fraude [cite: 104]"""
    with patch("src.banking_api.services.fraud_service.FraudService.get_summary") as mock_sum:
        mock_sum.return_value = {"total_frauds": 10}
        response = client.get("/api/fraud/summary")
        assert response.status_code == 200

def test_14_fraud_by_type():
    """Route 14 : Fraude par type [cite: 109]"""
    with patch("src.banking_api.services.fraud_service.FraudService.get_rate_by_type") as mock_rate:
        mock_rate.return_value = {"TRANSFER": 0.8}
        response = client.get("/api/fraud/by-type")
        assert response.status_code == 200

def test_15_fraud_predict():
    """Route 15 : Prédiction (Scoring) [cite: 111]"""
    payload = {
        "type": "CASH_OUT", 
        "amount": 50000.0, 
        "oldbalanceOrg": 50000.0, 
        "newbalanceOrig": 0.0
    }
    with patch("src.banking_api.services.fraud_service.FraudService.predict") as mock_pred:
        mock_pred.return_value = MOCK_FRAUD_PRED
        response = client.post("/api/fraud/predict", json=payload)
        assert response.status_code == 200
        assert response.json()["isFraud"] is True

# --- CATÉGORIE 4 : CLIENTS (Routes 16-18) ---

def test_16_get_customers():
    """Route 16 : Liste des clients (Source users_data.csv) [cite: 117]"""
    with patch("src.banking_api.services.customer_service.CustomerService.get_paginated_names") as mock_cust:
        mock_cust.return_value = {"customers": [{"id": 1, "name": "User 1"}]}
        response = client.get("/api/customers")
        assert response.status_code == 200

def test_17_get_customer_profile():
    """Route 17 : Profil client (Source users_data + cards_data) [cite: 119]"""
    with patch("src.banking_api.services.customer_service.CustomerService.get_profile") as mock_prof:
        mock_prof.return_value = MOCK_CUSTOMER
        response = client.get("/api/customers/1")
        assert response.status_code == 200
        assert response.json()["id"] == "1"

def test_18_get_top_customers():
    """Route 18 : Top clients [cite: 128]"""
    with patch("src.banking_api.services.customer_service.CustomerService.get_top_by_volume") as mock_top:
        mock_top.return_value = {"top": []}
        response = client.get("/api/customers/top")
        assert response.status_code == 200

# --- CATÉGORIE 5 : ADMINISTRATION (Routes 19-20) ---

def test_19_system_health():
    """Route 19 : Health Check [cite: 130]"""
    with patch("src.banking_api.services.system_service.SystemService.get_health") as mock_health:
        mock_health.return_value = {"status": "ok", "dataset_loaded": True}
        response = client.get("/api/system/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"

def test_20_system_metadata():
    """Route 20 : Métadonnées [cite: 134]"""
    with patch("src.banking_api.services.system_service.SystemService.get_metadata") as mock_meta:
        mock_meta.return_value = {"version": "1.0.0"}
        response = client.get("/api/system/metadata")
        assert response.status_code == 200

