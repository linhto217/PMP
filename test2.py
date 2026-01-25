import unittest
from fastapi.testclient import TestClient
from unittest.mock import patch
from src.banking_api.main import app

class TestFraudAnalysisScenario(unittest.TestCase):
    """
    Test de feature (scénario métier) utilisant unittest standard.
    Scénario : Un analyste vérifie le système, recherche une transaction suspecte et lance un scoring.
    """

    def setUp(self):
        """Initialisation du client de test avant chaque test."""
        self.client = TestClient(app)

    def test_full_fraud_detection_flow(self):
        """
        Scénario :
        1. Vérifier que l'API est en bonne santé (Health Check).
        2. Rechercher une transaction spécifique (gros montant).
        3. Lancer une prédiction de fraude sur cette transaction.
        """
        
        # ÉTAPE 1 : Vérification du système
        with patch("src.banking_api.services.system_service.SystemService.get_health") as mock_health:
            mock_health.return_value = {"status": "ok", "dataset_loaded": True}
            
            response_health = self.client.get("/api/system/health")
            self.assertEqual(response_health.status_code, 200)
            self.assertEqual(response_health.json()["status"], "ok")
            print("\n[Feature] Système opérationnel ✅")

        # ÉTAPE 2 : Recherche de transactions suspectes (TRANSFER > 1000)
        # On simule que le service trouve une transaction
        mock_transaction = {
            "id": "TX_999",
            "type": "TRANSFER",
            "amount": 500000.0,
            "oldbalanceOrg": 500000.0,
            "newbalanceOrig": 0.0,
            "isFraud": 1
        }
        
        with patch("src.banking_api.services.transactions_service.TransactionsService.search") as mock_search:
            mock_search.return_value = {"results": [mock_transaction]}
            
            payload_search = {
                "type": "TRANSFER",
                "amount_range": [100000, 1000000]
            }
            response_search = self.client.post("/api/transactions/search", json=payload_search)
            self.assertEqual(response_search.status_code, 200)
            results = response_search.json()["results"]
            self.assertTrue(len(results) > 0)
            target_tx = results[0]
            print(f"[Feature] Transaction suspecte trouvée : {target_tx['id']} ({target_tx['amount']}€) ✅")

        # ÉTAPE 3 : Scoring de fraude sur la transaction trouvée
        # On utilise les données de l'étape 2 pour interroger l'endpoint de prédiction
        with patch("src.banking_api.services.fraud_service.FraudService.predict") as mock_predict:
            mock_predict.return_value = {"isFraud": True, "probability": 0.98}
            
            payload_predict = {
                "type": target_tx["type"],
                "amount": target_tx["amount"],
                "oldbalanceOrg": target_tx["oldbalanceOrg"],
                "newbalanceOrig": target_tx["newbalanceOrig"]
            }
            
            response_predict = self.client.post("/api/fraud/predict", json=payload_predict)
            self.assertEqual(response_predict.status_code, 200)
            prediction = response_predict.json()
            
            self.assertTrue(prediction["isFraud"])
            self.assertGreater(prediction["probability"], 0.8)
            print(f"[Feature] Risque confirmé : {prediction['probability']*100}% ✅")

if __name__ == '__main__':
    unittest.main()  

