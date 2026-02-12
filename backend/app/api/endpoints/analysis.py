from fastapi import APIRouter, HTTPException
from typing import Dict, Any
import json
import os

router = APIRouter()

RESULTS_PATH = r'c:\Users\Wahid Khan\Desktop\g_project\backend\app\ml_models\results.json'

@router.get("/results")
async def get_ml_results():
    # Use relative path that works in different environments
    current_dir = os.path.dirname(os.path.abspath(__file__))
    results_path = os.path.join(current_dir, "..", "..", "ml_models", "results.json")
    
    if not os.path.exists(results_path):
        # Try absolute path as fallback
        results_path = RESULTS_PATH
        if not os.path.exists(results_path):
            return {
                "status": "training",
                "message": "Models are currently training or results not yet available."
            }
    
    try:
        with open(results_path, 'r') as f:
            results = json.load(f)
        
        # Determine best model dynamically
        best_model = None
        best_f1 = 0
        for model_name, model_data in results.items():
            if model_name in ['best_model', 'best_f1_score']:
                continue
            f1 = model_data.get('f1_score', 0)
            if f1 > best_f1:
                best_f1 = f1
                best_model = model_name
        
        if best_model:
            results['best_model'] = best_model
            results['best_f1_score'] = best_f1
        
        return {
            "status": "success",
            "data": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/trends")
async def get_trends():
    """Get trends and insights - try to use real data from results.json"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    results_path = os.path.join(current_dir, "..", "..", "ml_models", "results.json")
    
    top_features = []
    logic_insights = []
    
    # Try to load real feature importance from results
    if os.path.exists(results_path):
        try:
            with open(results_path, 'r') as f:
                results = json.load(f)
            
            # Get feature importance from decision tree if available
            if 'decision_tree' in results and 'top_features' in results['decision_tree']:
                top_features = results['decision_tree']['top_features'][:4]
            
            # Generate dynamic insights based on actual results
            best_model_name = results.get('best_model', 'decision_tree')
            best_f1 = results.get('best_f1_score', 0)
            best_data = results.get(best_model_name, {})
            
            model_names = {
                'decision_tree': 'Decision Tree',
                'naive_bayes': 'Naive Bayes',
                'knn': 'KNN',
                'ann': 'ANN (Deep Learning)'
            }
            
            best_model_display = model_names.get(best_model_name, best_model_name)
            accuracy = best_data.get('accuracy', 0) * 100
            f1_score = best_data.get('f1_score', 0) * 100
            
            logic_insights = [
                {
                    "title": f"Best Performing Model: {best_model_display}",
                    "content": f"The {best_model_display} model achieved the highest F1-score of {f1_score:.2f}% and accuracy of {accuracy:.2f}%. This model provides the best balance between precision and recall for fraud detection.",
                    "pros": [
                        f"F1-Score: {f1_score:.2f}%",
                        f"Accuracy: {accuracy:.2f}%",
                        "Best overall performance"
                    ],
                    "cons": [
                        "Requires regular retraining",
                        "Performance depends on data quality",
                        "May need hyperparameter tuning"
                    ]
                }
            ]
        except:
            pass
    
    # Default values if results not available
    if not top_features:
        top_features = [
            {"name": "TransactionAmt", "importance": 0.25, "reason": "High amounts are statistically more likely to be fraudulent in specific categories."},
            {"name": "card1", "importance": 0.18, "reason": "Specific card issuer clusters show higher fraud rates due to compromised batches."},
            {"name": "addr1", "importance": 0.12, "reason": "Geographical distance between shipping and billing addresses is a strong indicator."},
            {"name": "P_emaildomain", "importance": 0.10, "reason": "Disposable email providers are frequently used by bad actors."}
        ]
    
    if not logic_insights:
        logic_insights = [
            {
                "title": "Model Training Required",
                "content": "Please train the models first to see performance insights.",
                "pros": ["Run train_models.py to generate results"],
                "cons": []
            }
        ]
    
    return {
        "categories": ["W", "H", "R", "S", "O"],
        "fraud_by_category": [0.02, 0.05, 0.04, 0.06, 0.03],
        "top_features": top_features,
        "logic_insights": logic_insights
    }
