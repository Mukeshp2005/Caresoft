from sqlalchemy import Column, String, Float, Integer, Boolean, JSON, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import uuid

class Project(Base):
    __tablename__ = "projects"
    
    id = Column(String, primary_key=True, default=lambda: f"prog_{uuid.uuid4().hex[:12]}")
    name = Column(String, nullable=False)
    status = Column(String, default="In-Progress")  # "In-Progress" or "Completed"
    config = Column(JSON, nullable=False)  # Store ConfigState as JSON
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationship to nodes
    nodes = relationship("NodeModel", back_populates="project", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Project(id={self.id}, name={self.name}, status={self.status})>"


class NodeModel(Base):
    __tablename__ = "nodes"
    
    id = Column(String, primary_key=True)
    project_id = Column(String, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    parent_id = Column(String, ForeignKey("nodes.id", ondelete="CASCADE"), nullable=True)
    
    name = Column(String, nullable=False)
    display_id = Column(String, default="")
    level = Column(Integer, nullable=False)
    own_cost = Column(Float, default=0.0)
    weight = Column(Float, default=0.0)
    quantity = Column(Integer, default=1)
    material_calc_enabled = Column(Boolean, default=True)
    material = Column(String, default="Unassigned")
    config = Column(JSON, default={})
    status = Column(String, default="In-Progress")
    
    # Computed fields (can be calculated on-the-fly)
    total_cost = Column(Float, default=0.0)
    total_weight = Column(Float, default=0.0)
    co2_footprint = Column(Float, default=0.0)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    project = relationship("Project", back_populates="nodes")
    children = relationship(
        "NodeModel",
        back_populates="parent",
        cascade="all, delete-orphan",
        foreign_keys=[parent_id]
    )
    parent = relationship("NodeModel", back_populates="children", remote_side=[id])
    
    def __repr__(self):
        return f"<NodeModel(id={self.id}, name={self.name}, level={self.level})>"
