from sqlalchemy.orm import Session
from typing import List, Optional, Dict
from app.models import Project, NodeModel
from pydantic import BaseModel
import time

# --- PYDANTIC SCHEMAS ---

class Node(BaseModel):
    id: str
    name: str
    display_id: str = ""
    level: int
    own_cost: float = 0.0
    weight: float = 0.0
    quantity: int = 1
    material_calc_enabled: bool = True
    material: str = "Unassigned"
    children: List['Node'] = []
    config: Dict = {}
    status: str = "In-Progress"
    
    total_cost: float = 0.0
    total_weight: float = 0.0
    co2_footprint: float = 0.0
    
    class Config:
        from_attributes = True

Node.model_rebuild()

class ConfigState(BaseModel):
    brand: str = "TATA"
    model: str = "Punch"
    year: int = 2024
    fuel_type: str = "Petrol"
    trans_type: str = "Automatic"
    drive_type: str = "FWD"
    body_style: str = "Sedan"
    steering_side: str = "RHD"

# --- CRUD OPERATIONS ---

def create_project(db: Session, name: str, config: ConfigState) -> Project:
    """Create a new project in the database"""
    project = Project(
        id=f"prog_{int(time.time())}",
        name=name,
        config=config.dict(),
        status="In-Progress"
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


def get_project(db: Session, project_id: str) -> Optional[Project]:
    """Get a project by ID"""
    return db.query(Project).filter(Project.id == project_id).first()


def get_all_projects(db: Session) -> List[Project]:
    """Get all projects"""
    return db.query(Project).all()


def update_project_status(db: Session, project_id: str, status: str) -> Optional[Project]:
    """Update project status"""
    project = get_project(db, project_id)
    if project:
        project.status = status
        db.commit()
        db.refresh(project)
    return project


def delete_project(db: Session, project_id: str) -> bool:
    """Delete a project and all its nodes"""
    project = get_project(db, project_id)
    if project:
        db.delete(project)
        db.commit()
        return True
    return False


def create_node(db: Session, node_data: Node, project_id: str, parent_id: Optional[str] = None) -> NodeModel:
    """Create a new node in the database"""
    node = NodeModel(
        id=node_data.id,
        project_id=project_id,
        parent_id=parent_id,
        name=node_data.name,
        display_id=node_data.display_id,
        level=node_data.level,
        own_cost=node_data.own_cost,
        weight=node_data.weight,
        quantity=node_data.quantity,
        material_calc_enabled=node_data.material_calc_enabled,
        material=node_data.material,
        config=node_data.config,
        status=node_data.status,
        total_cost=node_data.total_cost,
        total_weight=node_data.total_weight,
        co2_footprint=node_data.co2_footprint
    )
    db.add(node)
    db.commit()
    db.refresh(node)
    return node


def save_tree_to_db(db: Session, node: Node, project_id: str, parent_id: Optional[str] = None):
    """Recursively save a tree structure to the database"""
    # Create the current node
    db_node = create_node(db, node, project_id, parent_id)
    
    # Recursively save children
    for child in node.children:
        save_tree_to_db(db, child, project_id, db_node.id)


def get_node(db: Session, node_id: str) -> Optional[NodeModel]:
    """Get a node by ID"""
    return db.query(NodeModel).filter(NodeModel.id == node_id).first()


def get_project_nodes(db: Session, project_id: str) -> List[NodeModel]:
    """Get all nodes for a project"""
    return db.query(NodeModel).filter(NodeModel.project_id == project_id).all()


def get_root_node(db: Session, project_id: str) -> Optional[NodeModel]:
    """Get the root node of a project (node with no parent)"""
    return db.query(NodeModel).filter(
        NodeModel.project_id == project_id,
        NodeModel.parent_id == None
    ).first()


def update_node(db: Session, node_id: str, updates: Dict) -> Optional[NodeModel]:
    """Update a node with given fields"""
    node = get_node(db, node_id)
    if node:
        for key, value in updates.items():
            if hasattr(node, key):
                setattr(node, key, value)
        db.commit()
        db.refresh(node)
    return node


def delete_node(db: Session, node_id: str) -> bool:
    """Delete a node and all its children (cascade)"""
    node = get_node(db, node_id)
    if node:
        db.delete(node)
        db.commit()
        return True
    return False


def build_tree_from_db(db_node: NodeModel, db: Session) -> Node:
    """Recursively build a Node tree from database NodeModel"""
    # Get all children of this node
    children_db = db.query(NodeModel).filter(NodeModel.parent_id == db_node.id).all()
    
    # Recursively build children
    children = [build_tree_from_db(child, db) for child in children_db]
    
    # Create the Node object
    return Node(
        id=db_node.id,
        name=db_node.name,
        display_id=db_node.display_id,
        level=db_node.level,
        own_cost=db_node.own_cost,
        weight=db_node.weight,
        quantity=db_node.quantity,
        material_calc_enabled=db_node.material_calc_enabled,
        material=db_node.material,
        children=children,
        config=db_node.config,
        status=db_node.status,
        total_cost=db_node.total_cost,
        total_weight=db_node.total_weight,
        co2_footprint=db_node.co2_footprint
    )


def get_project_tree(db: Session, project_id: str) -> Optional[Node]:
    """Get the complete tree structure for a project"""
    root = get_root_node(db, project_id)
    if root:
        return build_tree_from_db(root, db)
    return None


def update_tree_in_db(db: Session, node: Node, project_id: str):
    """Update the entire tree in the database (delete old, insert new)"""
    # Delete all existing nodes for this project
    db.query(NodeModel).filter(NodeModel.project_id == project_id).delete()
    db.commit()
    
    # Save the new tree
    save_tree_to_db(db, node, project_id)
