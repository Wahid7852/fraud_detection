from app.fraud_engine.rules_engine.engine import RulesEngine
from app.fraud_engine.ml_engine.model import MLEngine
from app.models.models import Transaction

class Scorer:
    def __init__(self):
        self.rules_engine = RulesEngine()
        self.ml_engine = MLEngine()

    async def calculate_score(self, transaction: Transaction):
        await self.rules_engine.initialize()
        rule_result = self.rules_engine.evaluate(transaction)
        ml_prob = self.ml_engine.predict(transaction.amount, transaction.category)
        
        ml_score = int(ml_prob * 100)
        rule_score = rule_result["total_rule_score"]
        
        # Hybrid score (weighted average)
        # 40% Rules, 60% ML
        final_score = int((0.4 * rule_score) + (0.6 * ml_score))
        
        # Map to risk level
        risk_level = self._get_risk_level(final_score)
        
        return {
            "risk_score": final_score,
            "risk_level": risk_level,
            "rule_score": rule_score,
            "ml_score": ml_score,
            "triggered_rules": rule_result["triggered_rules"]
        }

    def _get_risk_level(self, score: int) -> str:
        if score >= 91: return "Very High"
        if score >= 71: return "High"
        if score >= 51: return "Medium"
        if score >= 11: return "Low"
        return "Very Low"
