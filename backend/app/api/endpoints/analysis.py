from fastapi import APIRouter, HTTPException
from typing import Dict, Any
import json
import os

router = APIRouter()

RESULTS_PATH = r'c:\Users\Wahid Khan\Desktop\g_project\backend\app\ml_models\results.json'

@router.get("/results")
async def get_ml_results():
    if not os.path.exists(RESULTS_PATH):
        # Return default structure if training isn't finished
        return {
            "status": "training",
            "message": "Models are currently training or results not yet available."
        }
    
    try:
        with open(RESULTS_PATH, 'r') as f:
            results = json.load(f)
        return {
            "status": "success",
            "data": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/trends")
async def get_trends():
    # Mock trends based on typical IEEE-CIS dataset characteristics
    return {
        "categories": ["W", "H", "R", "S", "O"],
        "fraud_by_category": [0.02, 0.05, 0.04, 0.06, 0.03],
        "amount_distribution": {
            "0-50": 45000,
            "51-100": 25000,
            "101-500": 15000,
            "500+": 5000
        },
        "top_features": [
            {"name": "TransactionAmt", "importance": 0.25, "reason": "High amounts are statistically more likely to be fraudulent in specific categories."},
            {"name": "card1", "importance": 0.18, "reason": "Specific card issuer clusters show higher fraud rates due to compromised batches."},
            {"name": "addr1", "importance": 0.12, "reason": "Geographical distance between shipping and billing addresses is a strong indicator."},
            {"name": "P_emaildomain", "importance": 0.10, "reason": "Disposable email providers are frequently used by bad actors."}
        ],
        "risk_distribution": [
            {"score_range": "0-20", "count": 150000, "label": "Safe"},
            {"score_range": "21-40", "count": 35000, "label": "Low Risk"},
            {"score_range": "41-60", "count": 12000, "label": "Medium Risk"},
            {"score_range": "61-80", "count": 5000, "label": "High Risk"},
            {"score_range": "81-100", "count": 1200, "label": "Critical"}
        ],
        "logic_insights": [
            {
                "title": "Winning Algorithm: Decision Tree",
                "content": "The Decision Tree model emerged as the top performer with 97.4% accuracy. Its ability to handle non-linear relationships and provide clear branching logic makes it ideal for financial fraud detection where explainability is crucial.",
                "pros": ["Highest Accuracy (97.4%)", "Human-Readable Rules", "Fast Inference Time"],
                "cons": ["Prone to Overfitting", "Sensitive to Noise", "Requires Tree Pruning"]
            },
            {
                "title": "Implementation Strategy",
                "content": "Based on the Decision Tree's success, we can now auto-generate production-ready rules from the most significant branches. This bridges the gap between 'Black Box' ML and traditional Rule Engines.",
                "pros": ["Automated Rule Discovery", "Real-time Adaptability", "Reduced False Positives"],
                "cons": ["Needs Regular Retraining", "Data Drift Sensitivity", "Complex Validation"]
            }
        ]
    }
