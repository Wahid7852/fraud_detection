from app.models.models import Transaction, Alert, Case, Rule, SAR, AnalysisResult, AnalysisTrend, Report
from app.services.llm_service import llm_service
from datetime import datetime, timedelta, timezone
import random
import json

async def seed_data():
    # 1. Seed Transactions if empty
    trans_count = await Transaction.count()
    if trans_count == 0:
        print("Seeding sample transactions...")
        categories = ["W", "H", "R", "S", "O"]
        types = ["debit", "credit"]
        for i in range(20):
            amount = round(random.uniform(50.0, 6000.0), 2)  # Ensure minimum amount of 50
            trans = Transaction(
                transaction_id=f"TX{1000+i}",
                amount=amount,
                customer_id=random.randint(10000, 99999),
                merchant_id=random.randint(1000, 9999),
                category=random.choice(categories),
                transaction_type=random.choice(types),
                timestamp=datetime.now(timezone.utc) - timedelta(days=random.randint(0, 7))
            )
            await trans.insert()

    # 2. Seed Alerts if empty
    alert_count = await Alert.count()
    if alert_count == 0:
        print("Seeding sample alerts...")
        transactions = await Transaction.find_all().to_list()
        for i in range(5):
            trans = transactions[i]
            risk_score = random.randint(75, 99)
            risk_level = "High" if risk_score > 85 else "Medium"
            alert = Alert(
                transaction=trans,
                risk_score=risk_score,
                risk_level=risk_level,
                status="Pending",
                assigned_queue=random.choice(["High Profile", "High Velocity", "New Accounts"]),
                created_at=datetime.now(timezone.utc) - timedelta(hours=random.randint(1, 24))
            )
            await alert.insert()

    # 3. Seed Cases if empty
    case_count = await Case.count()
    if case_count == 0:
        print("Seeding sample cases...")
        alerts = await Alert.find_all().to_list()
        for i in range(min(3, len(alerts))):
            alert = alerts[i]
            case = Case(
                alert=alert,
                status=random.choice(["Open", "In Progress"]),
                analyst_id=random.randint(1, 5),
                created_at=datetime.now(timezone.utc) - timedelta(hours=random.randint(1, 12)),
                updated_at=datetime.now(timezone.utc)
            )
            await case.insert()
            # Update alert status if it's in a case
            alert.status = "Reviewed"
            await alert.save()

    # 4. Seed Analysis Results if empty
    analysis_count = await AnalysisResult.count()
    if analysis_count == 0:
        print("Seeding ML analysis results and AI insights...")
        models = ["decision_tree", "naive_bayes", "knn", "ann"]
        for model in models:
            res = AnalysisResult(
                model_name=model,
                accuracy=random.uniform(0.85, 0.98),
                feature_importance={
                    "TransactionAmt": random.uniform(0.2, 0.4),
                    "card1": random.uniform(0.1, 0.2),
                    "addr1": random.uniform(0.05, 0.15)
                }
            )
            await res.insert()
        
        # Seed AI Trends
        print("Generating and seeding AI fraud trends...")
        metrics = {
            "total_processed": 500000,
            "fraud_detected": 1500,
            "best_model": "decision_tree",
            "top_features": ["TransactionAmt", "card1", "dist1"]
        }
        
        # Use LLM to generate insights once at seed time
        try:
            logic_insights = await llm_service.generate_fraud_insights(metrics)
        except:
            # Fallback if LLM fails
            logic_insights = [
                {"title": "High Value Risk", "content": "Transactions over $500 show 3x higher fraud probability.", "pros": ["Catch large thefts"], "cons": ["High False Positives"]}
            ]

        trend = AnalysisTrend(
            categories=["W", "H", "R", "S", "O"],
            fraud_by_category=[0.02, 0.05, 0.04, 0.06, 0.03],
            top_features=[
                {"name": "TransactionAmt", "importance": 0.25, "reason": "High amounts are statistically more likely to be fraudulent."},
                {"name": "card1", "importance": 0.18, "reason": "Specific card issuer clusters show higher fraud rates."}
            ],
            risk_distribution=[
                {"score_range": "0-20", "count": 150000},
                {"score_range": "21-40", "count": 45000},
                {"score_range": "41-60", "count": 12000},
                {"score_range": "61-80", "count": 5000},
                {"score_range": "81-100", "count": 1200}
            ],
            logic_insights=logic_insights
        )
        await trend.insert()

    # 5. Seed Rules if empty
    rule_count = await Rule.count()
    if rule_count == 0:
        print("Seeding sample rules...")
        rules_data = [
            {
                "name": "High Amount Transaction",
                "description": "Flag transactions exceeding $5,000",
                "score_impact": 25,
                "action": "Review",
                "priority": 1,
                "is_active": True,
                "conditions": {"field": "amount", "operator": ">", "value": 5000}
            },
            {
                "name": "Rapid Succession Transactions",
                "description": "Multiple transactions from same customer within 1 hour",
                "score_impact": 20,
                "action": "Review",
                "priority": 2,
                "is_active": True,
                "conditions": {"field": "velocity", "operator": ">", "value": 5}
            },
            {
                "name": "Unusual Merchant Category",
                "description": "Transaction in high-risk merchant category",
                "score_impact": 15,
                "action": "Review",
                "priority": 3,
                "is_active": True,
                "conditions": {"field": "category", "operator": "in", "value": ["Service", "Other"]}
            },
            {
                "name": "New Account High Value",
                "description": "High-value transaction from account less than 30 days old",
                "score_impact": 30,
                "action": "Deny",
                "priority": 1,
                "is_active": True,
                "conditions": {"field": "account_age", "operator": "<", "value": 30, "and": {"amount": ">", "value": 1000}}
            },
            {
                "name": "Geographic Anomaly",
                "description": "Transaction from unusual location for customer",
                "score_impact": 18,
                "action": "Review",
                "priority": 4,
                "is_active": True,
                "conditions": {"field": "location_mismatch", "operator": "==", "value": True}
            }
        ]
        for rule_data in rules_data:
            rule = Rule(**rule_data)
            await rule.insert()

if __name__ == "__main__":
    import asyncio
    from app.db.session import init_db
    
    async def run_seed():
        await init_db()
        await seed_data()
        print("Seeding completed!")
        
    asyncio.run(run_seed())

    # 5. Seed SARs if empty or less than 3
    sar_count = await SAR.count()
    if sar_count < 3:
        print("Seeding sample SARs...")
        cases = await Case.find_all().to_list()
        sar_created = 0
        
        # Create SARs for cases that have valid transactions
        for i, case in enumerate(cases):
            if sar_created >= 3:
                break
            try:
                # Manually fetch alert and transaction
                if case.alert:
                    alert = await Alert.get(case.alert.ref.id)
                    if alert and alert.transaction:
                        transaction = await Transaction.get(alert.transaction.ref.id)
                        if transaction and transaction.amount > 0:
                            # Check if SAR already exists for this case
                            existing_sar = await SAR.find(SAR.case.id == case.id).first_or_none()
                            if not existing_sar:
                                sar = SAR(
                                    case=case,
                                    sar_id=f"SAR-{datetime.now().year}-{1000+sar_count+sar_created:04d}",
                                    customer_name=f"Customer {transaction.customer_id}",
                                    amount=transaction.amount,
                                    status="Filed" if sar_created == 0 else "Pending" if sar_created == 1 else "Draft",
                                    filing_date=datetime.now(timezone.utc) - timedelta(days=sar_created) if sar_created == 0 else None,
                                    description=f"Suspicious activity detected in transaction {transaction.transaction_id}",
                                    created_at=datetime.now(timezone.utc) - timedelta(days=sar_created+1)
                                )
                                await sar.insert()
                                sar_created += 1
            except Exception as e:
                print(f"Error creating SAR for case {case.id}: {e}")
                continue
        
        # If we still don't have enough SARs, create some from high-risk alerts directly
        if sar_created < 3:
            alerts = await Alert.find(Alert.risk_score >= 85).sort(-Alert.risk_score).limit(3 - sar_created).to_list()
            for i, alert in enumerate(alerts):
                if alert.transaction:
                    try:
                        transaction = await Transaction.get(alert.transaction.ref.id)
                        if transaction and transaction.amount > 0:
                            # Create a case for this alert if it doesn't exist
                            existing_case = await Case.find(Case.alert.id == alert.id).first_or_none()
                            if not existing_case:
                                case = Case(
                                    alert=alert,
                                    status="Open",
                                    analyst_id=None,
                                    created_at=datetime.now(timezone.utc) - timedelta(days=i+2)
                                )
                                await case.insert()
                            else:
                                case = existing_case
                            
                            # Create SAR for this case
                            sar = SAR(
                                case=case,
                                sar_id=f"SAR-{datetime.now().year}-{1000+sar_count+sar_created:04d}",
                                customer_name=f"Customer {transaction.customer_id}",
                                amount=transaction.amount,
                                status="Draft",
                                description=f"High-risk transaction {transaction.transaction_id} flagged for review",
                                created_at=datetime.now(timezone.utc) - timedelta(days=sar_created+1)
                            )
                            await sar.insert()
                            sar_created += 1
                    except Exception as e:
                        print(f"Error creating SAR from alert {alert.id}: {e}")
                        continue

    # 6. Seed Analysis Results if empty
    res_count = await AnalysisResult.count()
    if res_count == 0:
        print("Seeding analysis results...")
        results_data = [
            {
                "model_name": "decision_tree",
                "accuracy": 0.9744,
                "feature_importance": {
                    "TransactionAmt": 0.2603,
                    "card1": 0.1193,
                    "addr1": 0.1069,
                    "P_emaildomain": 0.0780
                }
            },
            {
                "model_name": "naive_bayes",
                "accuracy": 0.9002
            },
            {
                "model_name": "knn",
                "accuracy": 0.9734
            },
            {
                "model_name": "ann",
                "accuracy": 0.9730
            }
        ]
        for data in results_data:
            await AnalysisResult(**data).insert()

    # 7. Seed Analysis Trends if empty
    trend_count = await AnalysisTrend.count()
    if trend_count == 0:
        print("Seeding analysis trends...")
        trend = AnalysisTrend(
            categories=["W", "H", "R", "S", "O"],
            fraud_by_category=[0.02, 0.05, 0.04, 0.06, 0.03],
            top_features=[
                {"name": "TransactionAmt", "importance": 0.25, "reason": "High amounts are statistically more likely to be fraudulent in specific categories."},
                {"name": "card1", "importance": 0.18, "reason": "Specific card issuer clusters show higher fraud rates due to compromised batches."},
                {"name": "addr1", "importance": 0.12, "reason": "Geographical distance between shipping and billing addresses is a strong indicator."},
                {"name": "P_emaildomain", "importance": 0.10, "reason": "Disposable email providers are frequently used by bad actors."}
            ],
            risk_distribution=[
                {"score_range": "0-20", "count": 150000},
                {"score_range": "21-40", "count": 35000},
                {"score_range": "41-60", "count": 12000},
                {"score_range": "61-80", "count": 5000},
                {"score_range": "81-100", "count": 1200}
            ],
            logic_insights=[
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
        )
        await trend.insert()

    print("Data seeding completed successfully.")
