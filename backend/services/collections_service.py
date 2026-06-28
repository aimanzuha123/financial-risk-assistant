"""
Collections Service
Generates personalized collection strategies (Email, SMS, Phone Call, Payment Plan,
Escalation, Human Review) and implements an Agentic AI workflow to dynamically
update customer risk and actions when new payment or behavior data is received.
"""
from datetime import datetime
from typing import Dict, List, Any, Optional
import pandas as pd
from sqlalchemy.orm import Session
from database.models import CollectionAction, Dataset, AuditLog
from utils.helpers import safe_json_serialize

class CollectionsService:
    """Service to recommend, execute, and dynamically update collection strategies."""

    @staticmethod
    def generate_collections_strategy(
        df: pd.DataFrame,
        dataset_id: int,
        prediction_results: Optional[Dict],
        db: Session
    ) -> List[Dict]:
        """
        Generate default collection actions for all accounts in the dataset
        based on their risk level or model predictions.
        """
        # Clear existing actions for this dataset
        db.query(CollectionAction).filter(CollectionAction.dataset_id == dataset_id).delete()
        db.commit()

        # Check if we have prediction probabilities from the ML model
        predictions_map = {}
        if prediction_results and "prediction_probabilities" in prediction_results:
            for p in prediction_results["prediction_probabilities"]:
                # Map sample index to prediction info
                predictions_map[p["sample_index"]] = p

        actions_created = []

        # Find columns to identify customers
        id_col = next((c for c in df.columns if "id" in c.lower() or "customer" in c.lower()), None)
        target_col = next((c for c in df.columns if "default" in c.lower() or "delinquent" in c.lower() or "risk" in c.lower()), None)
        balance_col = next((c for c in df.columns if "balance" in c.lower() or "amount" in c.lower() or "due" in c.lower()), None)
        days_past_due_col = next((c for c in df.columns if "dpd" in c.lower() or "past_due" in c.lower() or "days" in c.lower()), None)

        for idx, row in df.iterrows():
            customer_id = str(row[id_col]) if id_col else f"CUST_{idx:05d}"
            balance = float(row[balance_col]) if balance_col else 1000.0
            dpd = int(row[days_past_due_col]) if days_past_due_col else 0

            # Determine risk level and risk score
            risk_score = 0.5
            pred_class = 0

            if idx in predictions_map:
                pred_info = predictions_map[idx]
                pred_class = pred_info["predicted_class"]
                # Get probability of class 1 (High Risk)
                risk_score = pred_info["probabilities"].get("1", 0.5)
            else:
                # Rule-based fallback if model results aren't mapped
                if target_col and target_col in df.columns:
                    pred_class = int(row[target_col])
                    risk_score = 0.9 if pred_class == 1 else 0.1
                else:
                    # Simple heuristic
                    if dpd > 60 or balance > 5000:
                        pred_class = 1
                        risk_score = 0.85
                    elif dpd > 30:
                        pred_class = 1
                        risk_score = 0.60
                    else:
                        pred_class = 0
                        risk_score = 0.15

            # Categorize Risk
            if risk_score >= 0.85 or dpd > 90:
                risk_level = "critical"
            elif risk_score >= 0.70 or pred_class == 1 or dpd > 60:
                risk_level = "high"
            elif risk_score >= 0.40 or dpd > 30:
                risk_level = "medium"
            else:
                risk_level = "low"

            # Recommend collections action
            strategy = CollectionsService.determine_action(risk_level, balance, dpd)

            action_details = {
                "balance_due": balance,
                "days_past_due": dpd,
                "suggested_channel": strategy["channel"],
                "message_template": strategy["template"],
                "suggested_discount_pct": strategy["discount_pct"],
                "reasoning": strategy["reasoning"]
            }

            action = CollectionAction(
                dataset_id=dataset_id,
                customer_id=customer_id,
                risk_level=risk_level,
                risk_score=float(risk_score),
                recommended_action=strategy["channel"],
                action_details=safe_json_serialize(action_details),
                priority=strategy["priority"],
                requires_human_approval=strategy["requires_approval"],
                status="pending"
            )

            db.add(action)
            actions_created.append(action)

        db.commit()

        # Audit Logging
        log = AuditLog(
            dataset_id=dataset_id,
            action="Generate Collections Strategy",
            category="collections",
            details={"actions_generated": len(actions_created)},
            severity="info"
        )
        db.add(log)
        db.commit()

        return [
            {
                "id": a.id,
                "customer_id": a.customer_id,
                "risk_level": a.risk_level,
                "risk_score": a.risk_score,
                "recommended_action": a.recommended_action,
                "action_details": a.action_details,
                "priority": a.priority,
                "status": a.status,
                "requires_approval": a.requires_human_approval
            }
            for a in actions_created
        ]

    @staticmethod
    def determine_action(risk_level: str, balance: float, dpd: int) -> Dict[str, Any]:
        """Core logic mapping risk metrics to specific channel interventions."""
        if risk_level == "critical":
            return {
                "channel": "escalation",
                "priority": 3,
                "requires_approval": True,
                "discount_pct": 20.0 if balance > 2000 else 0.0,
                "reasoning": f"Critical risk with {dpd} days past due and balance ${balance:,.2f}. Transferring to specialized recovery unit.",
                "template": f"FINAL NOTICE: Your account of ${balance:,.2f} is critically overdue by {dpd} days. Please contact our escalation desk immediately at 1-800-555-0199 to resolve this."
            }
        elif risk_level == "high":
            if balance > 3000:
                return {
                    "channel": "human_review",
                    "priority": 2,
                    "requires_approval": True,
                    "discount_pct": 15.0,
                    "reasoning": f"High risk and large balance of ${balance:,.2f}. Recommending human review for potential custom workout plans.",
                    "template": "A dedicated specialist is reviewing your account options. Please contact us to discuss hardship programs or customized repayment schedules."
                }
            else:
                return {
                    "channel": "phone_call",
                    "priority": 2,
                    "requires_approval": False,
                    "discount_pct": 10.0,
                    "reasoning": f"High risk with balance ${balance:,.2f}. Scheduling outbound collector phone call.",
                    "template": f"Hello, we are calling to discuss your outstanding balance of ${balance:,.2f}. We can offer a 10% settlement discount if paid today."
                }
        elif risk_level == "medium":
            if balance > 1000:
                return {
                    "channel": "payment_plan",
                    "priority": 1,
                    "requires_approval": False,
                    "discount_pct": 0.0,
                    "reasoning": f"Medium risk with moderate balance ${balance:,.2f}. Proposing installment options.",
                    "template": f"Avoid further late fees. Split your ${balance:,.2f} balance into 3 interest-free monthly payments. Log in to start your payment plan."
                }
            else:
                return {
                    "channel": "sms",
                    "priority": 1,
                    "requires_approval": False,
                    "discount_pct": 0.0,
                    "reasoning": f"Medium risk, small balance of ${balance:,.2f}. Prompting action via quick SMS link.",
                    "template": f"Reminder: Your payment of ${balance:,.2f} is overdue. Click here: pay.firm.com/quick to make a quick payment."
                }
        else:  # low
            return {
                "channel": "email",
                "priority": 0,
                "requires_approval": False,
                "discount_pct": 0.0,
                "reasoning": "Low risk account. Soft reminder via cost-effective automated email.",
                "template": f"Subject: Account Reminder - Payment Overdue\n\nDear Customer, this is a friendly reminder that your balance of ${balance:,.2f} is overdue. You can pay securely online."
            }

    @staticmethod
    def process_agentic_feedback(
        action_id: int,
        payment_amount: float,
        promise_to_pay: bool,
        notes: str,
        db: Session
    ) -> Dict[str, Any]:
        """
        Agentic Workflow.
        Triggered when a collector logs feedback, a payment arrives, or customer interacts.
        Recalculates risk score, updates action type, logs audit event.
        """
        action = db.query(CollectionAction).filter(CollectionAction.id == action_id).first()
        if not action:
            raise ValueError(f"Collection action {action_id} not found.")

        old_risk_level = action.risk_level
        old_action = action.recommended_action
        details = action.action_details or {}

        # 1. Update balance
        original_balance = details.get("balance_due", 1000.0)
        new_balance = max(0.0, original_balance - payment_amount)
        details["balance_due"] = new_balance
        details["payment_received"] = payment_amount
        details["last_payment_date"] = datetime.utcnow().isoformat()
        details["notes"] = notes

        # 2. Modify risk score based on feedback
        new_risk_score = action.risk_score
        if payment_amount >= original_balance:
            # Fully paid
            new_risk_score = 0.0
            action.status = "completed"
        elif payment_amount > 0:
            # Partial payment reduces risk
            new_risk_score = max(0.05, action.risk_score - 0.25)
        elif promise_to_pay:
            # Verbal agreement reduces risk slightly
            new_risk_score = max(0.10, action.risk_score - 0.15)
        else:
            # Broken promise or refusal increases risk
            new_risk_score = min(1.0, action.risk_score + 0.10)

        action.risk_score = float(new_risk_score)

        # 3. Recalculate Risk Level
        dpd = details.get("days_past_due", 0)
        if new_risk_score >= 0.85:
            new_risk_level = "critical"
        elif new_risk_score >= 0.70:
            new_risk_level = "high"
        elif new_risk_score >= 0.40:
            new_risk_level = "medium"
        else:
            new_risk_level = "low"

        action.risk_level = new_risk_level

        # 4. Recalculate recommended action
        strategy = CollectionsService.determine_action(new_risk_level, new_balance, dpd)
        action.recommended_action = strategy["channel"]
        action.priority = strategy["priority"]
        action.requires_human_approval = strategy["requires_approval"]
        details["suggested_channel"] = strategy["channel"]
        details["message_template"] = strategy["template"]
        details["reasoning"] = f"Dynamic update from agentic feedback. {strategy['reasoning']}"
        action.action_details = safe_json_serialize(details)
        action.updated_at = datetime.utcnow()

        db.commit()

        # Log responsible AI audit trail
        audit_log = AuditLog(
            dataset_id=action.dataset_id,
            action="Agentic Workflow Risk Recalculation",
            category="explainability",
            details={
                "customer_id": action.customer_id,
                "payment_amount": payment_amount,
                "promise_to_pay": promise_to_pay,
                "old_risk_level": old_risk_level,
                "new_risk_level": new_risk_level,
                "old_action": old_action,
                "new_action": action.recommended_action,
                "new_risk_score": new_risk_score,
            },
            severity="info"
        )
        db.add(audit_log)
        db.commit()

        return {
            "action_id": action.id,
            "customer_id": action.customer_id,
            "old_risk_level": old_risk_level,
            "new_risk_level": new_risk_level,
            "old_action": old_action,
            "new_action": action.recommended_action,
            "new_risk_score": action.risk_score,
            "status": action.status,
            "balance_due": new_balance,
        }

    @staticmethod
    def get_actions(dataset_id: int, db: Session) -> List[CollectionAction]:
        """Fetch all collections strategy actions for a dataset."""
        return db.query(CollectionAction).filter(CollectionAction.dataset_id == dataset_id).all()

    @staticmethod
    def approve_action(action_id: int, approved_by: str, db: Session) -> CollectionAction:
        """Approve a collection action that requires human intervention."""
        action = db.query(CollectionAction).filter(CollectionAction.id == action_id).first()
        if not action:
            raise ValueError(f"Collection action {action_id} not found.")

        action.status = "approved"
        action.updated_at = datetime.utcnow()

        # Audit Log
        audit = AuditLog(
            dataset_id=action.dataset_id,
            action="Human Approval Collection Action",
            category="approval",
            details={
                "action_id": action_id,
                "customer_id": action.customer_id,
                "approved_by": approved_by,
                "channel": action.recommended_action
            },
            severity="info"
        )
        db.add(audit)
        db.commit()

        return action
