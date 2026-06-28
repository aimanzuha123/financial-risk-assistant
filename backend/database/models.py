"""
SQLAlchemy ORM Models
Defines the relational schema for datasets, predictions, audit logs,
and collection actions.
"""
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Float, Text, DateTime, Boolean, JSON, ForeignKey
)
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()


class Dataset(Base):
    """Uploaded CSV dataset metadata and column analysis results."""
    __tablename__ = "datasets"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    rows = Column(Integer, default=0)
    columns = Column(Integer, default=0)
    numerical_columns = Column(JSON, default=list)
    categorical_columns = Column(JSON, default=list)
    target_column = Column(String(255), nullable=True)
    column_types = Column(JSON, default=dict)
    upload_date = Column(DateTime, default=datetime.utcnow)
    status = Column(String(50), default="uploaded")  # uploaded, analyzed, predicted
    summary = Column(JSON, default=dict)

    # Relationships
    predictions = relationship("Prediction", back_populates="dataset", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="dataset", cascade="all, delete-orphan")
    collection_actions = relationship("CollectionAction", back_populates="dataset", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Dataset(id={self.id}, name='{self.name}', rows={self.rows})>"


class Prediction(Base):
    """Model prediction results and performance metrics."""
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    dataset_id = Column(Integer, ForeignKey("datasets.id"), nullable=False)
    model_name = Column(String(100), nullable=False)
    accuracy = Column(Float, nullable=True)
    precision = Column(Float, nullable=True)
    recall = Column(Float, nullable=True)
    f1_score = Column(Float, nullable=True)
    roc_auc = Column(Float, nullable=True)
    confusion_matrix = Column(JSON, default=list)
    feature_importance = Column(JSON, default=dict)
    classification_report = Column(JSON, default=dict)
    prediction_probabilities = Column(JSON, default=list)
    explanations = Column(JSON, default=list)
    is_best_model = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    parameters = Column(JSON, default=dict)

    # Relationships
    dataset = relationship("Dataset", back_populates="predictions")

    def __repr__(self):
        return f"<Prediction(model='{self.model_name}', accuracy={self.accuracy})>"


class AuditLog(Base):
    """Responsible AI audit trail — logs every significant system action."""
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    dataset_id = Column(Integer, ForeignKey("datasets.id"), nullable=True)
    action = Column(String(100), nullable=False)
    category = Column(String(50), nullable=False)  # fairness, bias, explainability, privacy, approval
    details = Column(JSON, default=dict)
    user = Column(String(100), default="system")
    timestamp = Column(DateTime, default=datetime.utcnow)
    severity = Column(String(20), default="info")  # info, warning, critical

    # Relationships
    dataset = relationship("Dataset", back_populates="audit_logs")

    def __repr__(self):
        return f"<AuditLog(action='{self.action}', category='{self.category}')>"


class CollectionAction(Base):
    """AI-generated collection strategy actions for individual customers."""
    __tablename__ = "collection_actions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    dataset_id = Column(Integer, ForeignKey("datasets.id"), nullable=False)
    customer_id = Column(String(100), nullable=True)
    risk_level = Column(String(20), nullable=False)  # low, medium, high, critical
    risk_score = Column(Float, nullable=True)
    recommended_action = Column(String(50), nullable=False)  # email, sms, phone_call, payment_plan, escalation, human_review
    action_details = Column(JSON, default=dict)
    priority = Column(Integer, default=0)
    status = Column(String(20), default="pending")  # pending, approved, executed, completed
    requires_human_approval = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    dataset = relationship("Dataset", back_populates="collection_actions")

    def __repr__(self):
        return f"<CollectionAction(customer='{self.customer_id}', action='{self.recommended_action}')>"
