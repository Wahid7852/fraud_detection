from typing import List, Dict, Any
from sqlalchemy.orm import Session
from app.models.models import Transaction, Rule

class RulesEngine:
    def __init__(self, db: Session):
        self.db = db
        self.rules = self.db.query(Rule).filter(Rule.is_active == True).order_by(Rule.priority).all()

    def evaluate(self, transaction: Transaction) -> Dict[str, Any]:
        triggered_rules = []
        total_score = 0
        
        for rule in self.rules:
            if self._check_condition(transaction, rule.conditions):
                triggered_rules.append({
                    "name": rule.name,
                    "description": rule.description,
                    "score_impact": rule.score_impact
                })
                total_score += rule.score_impact
                
        return {
            "total_rule_score": min(total_score, 100),
            "triggered_rules": triggered_rules
        }

    def _check_condition(self, transaction: Transaction, conditions: Dict[str, Any]) -> bool:
        # Simplified condition checker
        for field, operators in conditions.items():
            val = getattr(transaction, field, None)
            if val is None:
                continue
                
            for op, threshold in operators.items():
                if op == ">" and not (val > threshold):
                    return False
                elif op == "<" and not (val < threshold):
                    return False
                elif op == "==" and not (val == threshold):
                    return False
                elif op == "!=" and not (val != threshold):
                    return False
        return True
