from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from typing import List, Optional, Dict
import uuid
import time

from app.database import engine, get_db, Base
from app import crud
from app.crud import Node, ConfigState
from app.models import NodeModel

app = FastAPI(title="CareSoft Hardcore VAVE Hub - Pure Engineering")

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


# Create database tables on startup
Base.metadata.create_all(bind=engine)

# GLOBAL STATE (for current session only)
current_project_id = None

def get_active_project(db: Session) -> Optional[Node]:
    global current_project_id
    if not current_project_id:
        # Get the first project if none is selected
        projects = crud.get_all_projects(db)
        if projects:
            current_project_id = projects[0].id
    
    if current_project_id:
        return crud.get_project_tree(db, current_project_id)
    return None


# MATERIAL & CO2 MASTER (Local Economics)
MATERIAL_MASTER = {
    "Steel (HSS)": 120.0,
    "Aluminum 6061": 320.0,
    "Polypropylene": 180.0,
    "Cast Iron": 95.0,
    "Copper": 850.0,
    "Lithium-Ion": 1200.0,
    "Rubber (EPDM)": 210.0,
    "Composite": 450.0
}
CO2_FACTORS = {"Steel (HSS)": 2.5, "Aluminum 6061": 12.0, "Polypropylene": 1.8, "Cast Iron": 3.2, "Copper": 4.5, "Lithium-Ion": 15.0, "Rubber (EPDM)": 2.3, "Composite": 3.5}

# --- THE EXHAUSTIVE TEARDOWN ENGINE ---

def build_full_tree(cfg: ConfigState):
    METALS = ["Steel (HSS)", "Aluminum 6061", "Cast Iron", "Copper"]
    root = Node(id="v-root", name=f"PROJECT: {cfg.fuel_type} {cfg.body_style} {cfg.drive_type} {cfg.steering_side}", level=0, material_calc_enabled=False)
    systems = []

    # 1.0 POWER UNIT
    if cfg.fuel_type != "EV":
        engine = Node(id="s-1", name="1.0 Internal Combustion Engine", level=1, children=[
            Node(id="ss-1-1", name="1.1 Block & Heads", level=2, children=[
                Node(id="p-1-1-1", name="Engine Block Core", level=3, own_cost=45000, weight=42000, material="Cast Iron"),
                Node(id="p-1-1-2", name="Reluctor Ring (Crank)", level=3, own_cost=850, weight=120, material="Steel (HSS)"),
                Node(id="p-1-1-3", name="Balance Shafts Assy", level=3, children=[
                    Node(id="p-1-1-3-1", name="Balance Gears", level=4, weight=800, material="Cast Iron"),
                    Node(id="p-1-1-3-2", name="Shaft Bearings", level=4, quantity=4, weight=50)
                ]),
                Node(id="f-1-1-4", name="Block Dowel Pins", level=4, quantity=6, weight=15),
                Node(id="f-1-1-5", name="Oil Gallery Plugs", level=4, quantity=8, weight=10),
                Node(id="f-1-1-6", name="Baffle Plates", level=4, quantity=2, weight=1200, material="Steel (HSS)")
            ]),
            Node(id="ss-1-2", name="1.2 Pistons & Connecting Rods", level=2, children=[
                Node(id="c-1-2-1", name="Piston Sets", level=3, quantity=4, children=[
                    Node(id="p-1-2-1-1", name="Piston Body", level=4, own_cost=1500, weight=450, material="Aluminum 6061"),
                    Node(id="f-1-2-1-2", name="Oil Ring Expander", level=5, weight=8),
                    Node(id="p-1-2-1-3", name="Compression Ring", level=5, quantity=2, weight=12)
                ]),
                Node(id="c-1-2-2", name="Connecting Rods", level=3, quantity=4, children=[
                    Node(id="p-1-2-2-1", name="Rod Body", level=4, weight=600, material="Steel (HSS)"),
                    Node(id="f-1-2-2-2", name="Alignment Sleeves", level=5, quantity=2),
                    Node(id="f-1-2-2-3", name="Rod Bearing Tabs", level=5)
                ])
            ]),
            Node(id="ss-1-3", name="1.3 Valvetrain Detail", level=2, children=[
                Node(id="p-1-3-1", name="Cylinder Head Casting", level=3, own_cost=28000, weight=18000, material="Aluminum 6061"),
                Node(id="p-1-3-2", name="Hydraulic Lash Adjusters", level=3, quantity=16, own_cost=450, weight=120),
                Node(id="p-1-3-3", name="Roller Lifters", level=3, quantity=16, weight=85),
                Node(id="f-1-3-4", name="Valve Stem Seals", level=5, quantity=16, material="Rubber (EPDM)"),
                Node(id="f-1-3-5", name="Valve Tip Caps", level=5, quantity=16, material="Steel (HSS)"),
                Node(id="f-1-3-6", name="Valve Spring Seats", level=5, quantity=16)
            ]),
            Node(id="ss-1-4", name="1.4 Timing Logic", level=2, children=[
                Node(id="p-1-4-1", name="Timing Chain Dampers", level=3, weight=450),
                Node(id="p-1-4-2", name="Chain Guide Rails", level=3, quantity=2, weight=600),
                Node(id="p-1-4-3", name="VVT Cam Actuator", level=3, own_cost=8500, weight=1800),
                Node(id="p-1-4-4", name="VVT Solenoid", level=3, weight=300),
                Node(id="f-1-4-5", name="Timing Inspection Plug", level=4)
            ])
        ])
    else:
        engine = Node(id="s-1", name="1.0 EV Motor & Power", level=1, children=[
            Node(id="ss-1-1", name="traction Motor", level=2, children=[
                Node(id="p-1-1-1", name="Stator Core", level=3, weight=25000, material="Steel (HSS)"),
                Node(id="p-1-1-2", name="Copper Hairpins", level=3, weight=12000, material="Copper"),
                Node(id="p-1-1-3", name="Rotor Assy", level=3, weight=15000)
            ]),
            Node(id="ss-1-2", name="80kWh Battery Pack", level=2, children=[
                Node(id="p-1-2-1", name="Battery Cells (2170)", level=3, quantity=4000, weight=68, material="Lithium-Ion"),
                Node(id="p-1-2-2", name="BMS Module", level=3, own_cost=12000)
            ])
        ])
    systems.append(engine)

    # 2.0 INTAKE / FUEL
    if cfg.fuel_type != "EV":
        intake_fuel = Node(id="s-2", name="2.0 Intake & Fuel", level=1, children=[
            Node(id="ss-2-1", name="Air Induction", level=2, children=[
                Node(id="p-2-1-1", name="Intake Resonator", level=3, material="Polypropylene"),
                Node(id="p-2-1-2", name="Helmholtz Chamber", level=3, weight=400),
                Node(id="p-2-1-3", name="IMRC Valve", level=3, own_cost=3200)
            ]),
            Node(id="ss-2-2", name="Fuel Distribution", level=2, children=[
                Node(id="p-2-2-1", name="Fuel Pulsation Damper", level=3),
                Node(id="f-2-2-2", name="Injector Heat Insulators", level=4, quantity=4),
                Node(id="p-2-2-3", name="Purge Solenoid", level=3)
            ])
        ])
        systems.append(intake_fuel)

    # 3.0 EXHAUST
    if cfg.fuel_type != "EV":
        exhaust = Node(id="s-3", name="3.0 Exhaust System", level=1, children=[
            Node(id="ss-3-1", name="3.1 Manifold & Turbo", level=2, children=[
                Node(id="p-3-1-1", name="Exhaust Manifold", level=3, weight=8500, material="Cast Iron"),
                Node(id="p-3-1-2", name="Turbocharger Assy", level=3, own_cost=42000, material_calc_enabled=False)
            ]),
            Node(id="ss-3-2", name="3.2 Aftertreatment", level=2, children=[
                Node(id="p-3-2-1", name="Catalytic Converter", level=3, weight=4500, material="Steel (HSS)"),
                Node(id="p-3-2-2", name="Oxygen Sensors", level=3, quantity=2, own_cost=1800, material_calc_enabled=False)
            ])
        ])
        systems.append(exhaust)

    # 4.0 COOLING
    cooling = Node(id="s-4", name="4.0 Cooling System", level=1, children=[
        Node(id="ss-4-1", name="Heat Exchangers", level=2, children=[
            Node(id="p-4-1-1", name="Main Radiator", level=3, weight=6200, material="Aluminum 6061"),
            Node(id="p-4-1-2", name="Expansion Tank", level=3, material="Polypropylene")
        ]),
        Node(id="ss-4-2", name="Coolant Management", level=2, children=[
            Node(id="p-4-2-1", name="Electric Water Pump", level=3, own_cost=8500),
            Node(id="p-4-2-2", name="Coolant Hoses (Main)", level=3, material="Rubber (EPDM)")
        ])
    ])
    systems.append(cooling)

    # 5.0 LUBRICATION
    if cfg.fuel_type != "EV":
        lubrication = Node(id="s-5", name="5.0 Lubrication System", level=1, children=[
            Node(id="p-5-1", name="Oil Pump Assy", level=2, own_cost=5500),
            Node(id="p-5-2", name="Oil Cooler", level=2, material="Aluminum 6061"),
            Node(id="p-5-3", name="Oil Pan", level=2, weight=2800, material="Steel (HSS)")
        ])
        systems.append(lubrication)

    # 6.0 ELECTRICAL & ELECTRONICS
    electrical = Node(id="s-6", name="6.0 Electrical & Wire Harness", level=1, children=[
        Node(id="ss-6-1", name="Main Harness", level=2, children=[
            Node(id="p-6-1-1", name="Engine Harness", level=3, weight=4500, material="Copper"),
            Node(id="p-6-1-2", name="Body Harness", level=3, weight=12000, material="Copper")
        ]),
        Node(id="ss-6-2", name="Control Modules", level=2, children=[
            Node(id="p-6-2-1", name="ECU/VCU", level=3, own_cost=25000, material_calc_enabled=False),
            Node(id="p-6-2-2", name="Fuse Box Assy", level=3, own_cost=4500)
        ])
    ])
    systems.append(electrical)

    # 7.0 TRANSMISSION
    trans = Node(id="s-7", name="7.0 Transmission Assy", level=1)
    if cfg.trans_type == "Manual":
        trans.children = [Node(id="ss-7-1", name="Manual Internals", level=2, children=[
            Node(id="p-7-1-1", name="Shift Fork Pads", level=3, quantity=3),
            Node(id="f-7-1-2", name="Synchronizer Keys", level=4, quantity=12),
            Node(id="f-7-1-3", name="Detent Ball & Spring", level=4, quantity=6)
        ])]
    else:
        trans.children = [Node(id="ss-7-2", name="Auto Valve Body", level=2, children=[
            Node(id="p-7-2-1", name="Planetary Gear Set", level=3, weight=22000),
            Node(id="p-7-2-2", name="Accumulator Pistons", level=3, quantity=5)
        ])]
    systems.append(trans)

    # 8.0 AWD
    if cfg.drive_type == "AWD":
        drive = Node(id="s-8", name="8.0 Drivetrain (AWD)", level=1, children=[
            Node(id="p-8-1", name="Active Transfer Case", level=2, own_cost=38000),
            Node(id="p-8-2", name="Rear Differential", level=2, own_cost=32000, weight=25000),
            Node(id="f-8-3", name="Differential Shims", level=4, quantity=8)
        ])
        systems.append(drive)

    # 12.0 WHEELS & TIRES
    wheels = Node(id="s-12", name="12.0 Wheels & Tires", level=1, children=[
        Node(id="p-12-1", name="Alloy Wheels", level=2, quantity=4, weight=11500, material="Aluminum 6061"),
        Node(id="p-12-2", name="Rubber Tires", level=2, quantity=4, weight=9500, material="Rubber (EPDM)")
    ])
    systems.append(wheels)

    # 10.0 SUSPENSION & AXLES
    suspension = Node(id="s-10", name="10.0 Chassis & Suspension", level=1, children=[
        Node(id="ss-10-1", name="Front Suspension", level=2, children=[
            Node(id="p-10-1-1", name="MacPherson Struts", level=3, quantity=2, own_cost=8500),
            Node(id="p-10-1-2", name="Control Arms", level=3, quantity=2, material="Steel (HSS)")
        ]),
        Node(id="ss-10-2", name="Rear Suspension", level=2, children=[
            Node(id="p-10-2-1", name="Multi-link Subframe", level=3, material="Steel (HSS)"),
            Node(id="p-10-2-2", name="Anti-roll Bar", level=3, weight=4500)
        ])
    ])
    systems.append(suspension)

    # 9.0 STEERING (Mirror Logic)
    steering = Node(id="s-9", name=f"9.0 Steering ({cfg.steering_side})", level=1, children=[
        Node(id="ss-9-1", name="Steering Rack Detail", level=2, children=[
            Node(id="p-9-1-1", name="Rack Guide Spring", level=3),
            Node(id="p-9-1-2", name="Rack Adjuster Plug", level=3)
        ]),
        Node(id="ss-9-2", name="Column Assembly", level=2, children=[
            Node(id="p-9-2-1", name="Spiral Cable (Clockspring)", level=3),
            Node(id="f-9-2-2", name="Collapse Capsule", level=4)
        ])
    ])
    systems.append(steering)

    # 11.0 BRAKES
    brakes = Node(id="s-11", name="11.0 Performance Brakes", level=1, children=[
        Node(id="ss-11-1", name="Caliper Hardware", level=2, children=[
            Node(id="f-11-1-1", name="Anti-rattle Clips", level=4, quantity=8),
            Node(id="f-11-1-2", name="Caliper Dust Seals", level=4, quantity=8)
        ]),
        Node(id="p-11-2", name="Proportioning Valve", level=2)
    ])
    systems.append(brakes)

    # 13.0 BODY
    body = Node(id="s-13", name=f"13.0 Body System ({cfg.body_style})", level=1, children=[
        Node(id="p-13-1", name="Body Structure BIW", level=2, weight=350000 if cfg.body_style=="Sedan" else 520000, material="Steel (HSS)"),
        Node(id="p-13-2", name="Sound Deadening Pads", level=2, quantity=12, material="Composite")
    ])
    systems.append(body)

    # 15.0 FASTENERS
    fasteners = Node(id="s-15", name="15.0 Fastener Library", level=1, children=[
        Node(id="fb-1", name="E-Torx Bolt M10", level=4, quantity=180, own_cost=45, weight=35, material="Steel (HSS)"),
        Node(id="fb-2", name="Rivnut M8 Insert", level=4, quantity=450, own_cost=12, weight=8, material="Steel (HSS)")
    ])
    systems.append(fasteners)

    root.children = systems
    
    # Second pass to enable metal logic only for metal materials
    def enable_metal_logic(node: Node):
        if node.material in ["Steel (HSS)", "Aluminum 6061", "Cast Iron", "Copper"]:
            node.material_calc_enabled = True
        else:
            node.material_calc_enabled = False
        for c in node.children:
            enable_metal_logic(c)
            
    enable_metal_logic(root)
    return root

# --- CALC ENGINE ---

def calculate_totals(node: Node, prefix: str = ""):
    node.display_id = prefix
    agg_cost = 0.0
    agg_weight = 0.0
    agg_co2 = 0.0
    
    mat_rate = MATERIAL_MASTER.get(node.material, 0.0) if node.material_calc_enabled else 0.0
    self_part_cost = node.own_cost * node.quantity
    
    if node.material_calc_enabled:
        self_co2 = (node.weight / 1000.0) * CO2_FACTORS.get(node.material, 0.0) * node.quantity
    else:
        self_co2 = 0.0 # or some other logic for non-metal parts
    
    for i, child in enumerate(node.children, 1):
        new_prefix = f"{prefix}.{i}" if prefix else str(i)
        res_cost, res_weight, res_co2 = calculate_totals(child, new_prefix)
        agg_cost += res_cost
        agg_weight += res_weight
        agg_co2 += res_co2
        
    node.total_cost = self_part_cost + agg_cost
    node.total_weight = (node.weight * node.quantity) + agg_weight
    node.co2_footprint = self_co2 + agg_co2
    return node.total_cost, node.total_weight, node.co2_footprint

def find_node(node: Node, target_id: str) -> Optional[Node]:
    if node.id == target_id: return node
    for child in node.children:
        f = find_node(child, target_id)
        if f: return f
    return None

# --- API ROUTES ---

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/cache-test", response_class=HTMLResponse)
async def cache_test(request: Request):
    return templates.TemplateResponse("cache_test.html", {"request": request})

@app.get("/api/tree")
async def get_tree(db: Session = Depends(get_db)):
    root = get_active_project(db)
    if root:
        calculate_totals(root)
    return root

@app.get("/api/projects")
async def list_projects(db: Session = Depends(get_db)):
    # Get all projects from database
    projects = crud.get_all_projects(db)
    summary = []
    for project in projects:
        # Get the tree for calculation
        tree = crud.get_project_tree(db, project.id)
        if tree:
            calculate_totals(tree)
            summary.append({
                "id": project.id, 
                "name": project.name, 
                "total_cost": tree.total_cost, 
                "total_weight": tree.total_weight,
                "config": project.config,
                "status": project.status,
                "part_count": count_nodes(tree),
                "tracked_parts": count_tracked_parts(tree)
            })
    return summary

def count_nodes(node: Node) -> int:
    return 1 + sum(count_nodes(c) for c in node.children)

def count_tracked_parts(node: Node) -> int:
    # A part is 'tracked' if it has a non-zero own_cost or if it's a leaf node with cost? 
    # USER: "if i enter an cost for two part it should increment +2"
    count = 1 if node.own_cost > 0 else 0
    return count + sum(count_tracked_parts(c) for c in node.children)

@app.post("/api/project/select")
async def select_project(req: dict):
    global current_project_id
    current_project_id = req.get("id")
    return {"status": "success"}

def reset_costs(node: Node):
    node.own_cost = 0.0
    for child in node.children:
        reset_costs(child)

@app.post("/api/project/new")
async def new_project(req: ConfigState, db: Session = Depends(get_db)):
    global current_project_id
    
    # Build the tree structure
    new_tree = build_full_tree(req)
    project_name = f"{req.brand} {req.model} ({req.year})"
    
    # Create project in database
    project = crud.create_project(db, project_name, req)
    
    # Reset costs and save tree to database
    reset_costs(new_tree)
    new_tree.id = project.id
    crud.save_tree_to_db(db, new_tree, project.id)
    
    current_project_id = project.id
    return {"status": "success", "id": project.id}

@app.post("/api/config")
async def update_config(config: ConfigState):
    # This endpoint might not be needed anymore with DB
    return {"status": "success"}

@app.get("/api/materials")
async def get_materials():
    return MATERIAL_MASTER

@app.post("/api/materials/update")
async def update_materials(req: Dict[str, float]):
    global MATERIAL_MASTER
    MATERIAL_MASTER.update(req)
    return {"status": "success"}

@app.post("/api/node/update")
async def update_node(req: dict, db: Session = Depends(get_db)):
    global current_project_id
    if not current_project_id:
        return {"status": "error", "message": "No active project"}
    
    # Update the node in database
    updates = {}
    if 'own_cost' in req: updates['own_cost'] = req['own_cost']
    if 'weight' in req: updates['weight'] = req['weight']
    if 'quantity' in req: updates['quantity'] = req['quantity']
    if 'material' in req: updates['material'] = req['material']
    if 'material_calc_enabled' in req: updates['material_calc_enabled'] = req['material_calc_enabled']
    
    node = crud.update_node(db, req['id'], updates)
    if node:
        return {"status": "success"}
    return {"status": "error"}

@app.post("/api/node/add")
async def add_node(req: dict, db: Session = Depends(get_db)):
    global current_project_id
    if not current_project_id:
        return {"status": "error", "message": "No active project"}
    
    # Get parent node to determine new node details
    parent = crud.get_node(db, req['parent_id'])
    if not parent:
        return {"status": "error", "message": "Parent node not found"}
    
    # Get children count for unique ID
    children_count = db.query(NodeModel).filter(
        NodeModel.parent_id == parent.id
    ).count()
    
    new_id = f"{parent.id}-n-{children_count}"
    new_node = Node(
        id=new_id,
        name=req.get('name', 'New Branch/Part'),
        level=parent.level + 1,
        material_calc_enabled=req.get('material_calc_enabled', True)
    )
    
    # Save to database
    db_node = crud.create_node(db, new_node, current_project_id, parent.id)
    if db_node:
        return {"status": "success", "new_id": new_id}
    return {"status": "error", "message": "Failed to create node"}


def delete_from_tree(node: Node, target_id: str):
    for i, child in enumerate(node.children):
        if child.id == target_id:
            node.children.pop(i)
            return True
        if delete_from_tree(child, target_id):
            return True
    return False

@app.post("/api/project/complete")
async def complete_project(req: dict, db: Session = Depends(get_db)):
    project_id = req.get("id") or current_project_id
    if project_id:
        project = crud.update_project_status(db, project_id, "Completed")
        if project:
            return {"status": "success"}
    return {"status": "error"}

@app.post("/api/project/delete")
async def delete_project(req: dict, db: Session = Depends(get_db)):
    global current_project_id
    p_id = req.get("id")
    if crud.delete_project(db, p_id):
        if current_project_id == p_id:
            current_project_id = None
        return {"status": "success"}
    return {"status": "error"}

@app.post("/api/node/delete")
async def delete_node_api(req: dict, db: Session = Depends(get_db)):
    node_id = req.get('id')
    if not node_id:
        return {"status": "error", "message": "No node ID provided"}
    
    # Get the node to check if it's a root node
    node = crud.get_node(db, node_id)
    if not node:
        return {"status": "error", "message": "Node not found"}
    
    # Check if this is a root node (no parent)
    if node.parent_id is None:
        return {"status": "error", "message": "Cannot delete root node"}
    
    success = crud.delete_node(db, node_id)
    return {"status": "success" if success else "error"}



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
