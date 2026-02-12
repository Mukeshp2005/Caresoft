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
    root = Node(id=f"root_{uuid.uuid4().hex[:8]}", name=f"PROJECT: {cfg.fuel_type} {cfg.body_style} {cfg.drive_type} {cfg.steering_side}", level=0, material_calc_enabled=False)
    systems = []

    # 1.0 POWER UNIT
    if cfg.fuel_type != "EV":
        engine = Node(id=f"s1_{uuid.uuid4().hex[:8]}", name="1.0 Internal Combustion Engine", level=1, children=[
            Node(id=f"ss11_{uuid.uuid4().hex[:8]}", name="1.1 Block & Heads", level=2, children=[
                Node(id=f"p111_{uuid.uuid4().hex[:8]}", name="Engine Block Core", level=3, own_cost=45000, weight=42000, material="Cast Iron"),
                Node(id=f"p112_{uuid.uuid4().hex[:8]}", name="Reluctor Ring (Crank)", level=3, own_cost=850, weight=120, material="Steel (HSS)"),
                Node(id=f"p113_{uuid.uuid4().hex[:8]}", name="Balance Shafts Assy", level=3, children=[
                    Node(id=f"p1131_{uuid.uuid4().hex[:8]}", name="Balance Gears", level=4, weight=800, material="Cast Iron"),
                    Node(id=f"p1132_{uuid.uuid4().hex[:8]}", name="Shaft Bearings", level=4, quantity=4, weight=50)
                ]),
                Node(id=f"f114_{uuid.uuid4().hex[:8]}", name="Block Dowel Pins", level=4, quantity=6, weight=15),
                Node(id=f"f115_{uuid.uuid4().hex[:8]}", name="Oil Gallery Plugs", level=4, quantity=8, weight=10),
                Node(id=f"f116_{uuid.uuid4().hex[:8]}", name="Baffle Plates", level=4, quantity=2, weight=1200, material="Steel (HSS)")
            ]),
            Node(id=f"ss12_{uuid.uuid4().hex[:8]}", name="1.2 Pistons & Connecting Rods", level=2, children=[
                Node(id=f"c121_{uuid.uuid4().hex[:8]}", name="Piston Sets", level=3, quantity=4, children=[
                    Node(id=f"p1211_{uuid.uuid4().hex[:8]}", name="Piston Body", level=4, own_cost=1500, weight=450, material="Aluminum 6061"),
                    Node(id=f"f1212_{uuid.uuid4().hex[:8]}", name="Oil Ring Expander", level=5, weight=8),
                    Node(id=f"p1213_{uuid.uuid4().hex[:8]}", name="Compression Ring", level=5, quantity=2, weight=12)
                ]),
                Node(id=f"c122_{uuid.uuid4().hex[:8]}", name="Connecting Rods", level=3, quantity=4, children=[
                    Node(id=f"p1221_{uuid.uuid4().hex[:8]}", name="Rod Body", level=4, weight=600, material="Steel (HSS)"),
                    Node(id=f"f1222_{uuid.uuid4().hex[:8]}", name="Alignment Sleeves", level=5, quantity=2),
                    Node(id=f"f1223_{uuid.uuid4().hex[:8]}", name="Rod Bearing Tabs", level=5)
                ])
            ]),
            Node(id=f"ss13_{uuid.uuid4().hex[:8]}", name="1.3 Valvetrain Detail", level=2, children=[
                Node(id=f"p131_{uuid.uuid4().hex[:8]}", name="Cylinder Head Casting", level=3, own_cost=28000, weight=18000, material="Aluminum 6061"),
                Node(id=f"p132_{uuid.uuid4().hex[:8]}", name="Hydraulic Lash Adjusters", level=3, quantity=16, own_cost=450, weight=120),
                Node(id=f"p133_{uuid.uuid4().hex[:8]}", name="Roller Lifters", level=3, quantity=16, weight=85),
                Node(id=f"f134_{uuid.uuid4().hex[:8]}", name="Valve Stem Seals", level=5, quantity=16, material="Rubber (EPDM)"),
                Node(id=f"f135_{uuid.uuid4().hex[:8]}", name="Valve Tip Caps", level=5, quantity=16, material="Steel (HSS)"),
                Node(id=f"f136_{uuid.uuid4().hex[:8]}", name="Valve Spring Seats", level=5, quantity=16)
            ]),
            Node(id=f"ss14_{uuid.uuid4().hex[:8]}", name="1.4 Timing Logic", level=2, children=[
                Node(id=f"p141_{uuid.uuid4().hex[:8]}", name="Timing Chain Dampers", level=3, weight=450),
                Node(id=f"p142_{uuid.uuid4().hex[:8]}", name="Chain Guide Rails", level=3, quantity=2, weight=600),
                Node(id=f"p143_{uuid.uuid4().hex[:8]}", name="VVT Cam Actuator", level=3, own_cost=8500, weight=1800),
                Node(id=f"p144_{uuid.uuid4().hex[:8]}", name="VVT Solenoid", level=3, weight=300),
                Node(id=f"f145_{uuid.uuid4().hex[:8]}", name="Timing Inspection Plug", level=4)
            ])
        ])
    else:
        engine = Node(id=f"s1_{uuid.uuid4().hex[:8]}", name="1.0 EV Motor & Power", level=1, children=[
            Node(id=f"ss11_{uuid.uuid4().hex[:8]}", name="1.1 traction Motor", level=2, children=[
                Node(id=f"p111_{uuid.uuid4().hex[:8]}", name="Stator Core", level=3, weight=25000, material="Steel (HSS)"),
                Node(id=f"p112_{uuid.uuid4().hex[:8]}", name="Copper Hairpins", level=3, weight=12000, material="Copper"),
                Node(id=f"p113_{uuid.uuid4().hex[:8]}", name="Rotor Assy", level=3, weight=15000)
            ]),
            Node(id=f"ss12_{uuid.uuid4().hex[:8]}", name="1.2 80kWh Battery Pack", level=2, children=[
                Node(id=f"p121_{uuid.uuid4().hex[:8]}", name="Battery Cells (2170)", level=3, quantity=4000, weight=68, material="Lithium-Ion"),
                Node(id=f"p122_{uuid.uuid4().hex[:8]}", name="BMS Module", level=3, own_cost=12000)
            ])
        ])
    systems.append(engine)

    # 2.0 INTAKE / FUEL
    if cfg.fuel_type != "EV":
        intake_fuel = Node(id=f"s2_{uuid.uuid4().hex[:8]}", name="2.0 Intake & Fuel", level=1, children=[
            Node(id=f"ss21_{uuid.uuid4().hex[:8]}", name="Air Induction", level=2, children=[
                Node(id=f"p211_{uuid.uuid4().hex[:8]}", name="Intake Resonator", level=3, material="Polypropylene"),
                Node(id=f"p212_{uuid.uuid4().hex[:8]}", name="Helmholtz Chamber", level=3, weight=400),
                Node(id=f"p213_{uuid.uuid4().hex[:8]}", name="IMRC Valve", level=3, own_cost=3200)
            ]),
            Node(id=f"ss22_{uuid.uuid4().hex[:8]}", name="Fuel Distribution", level=2, children=[
                Node(id=f"p221_{uuid.uuid4().hex[:8]}", name="Fuel Pulsation Damper", level=3),
                Node(id=f"f222_{uuid.uuid4().hex[:8]}", name="Injector Heat Insulators", level=4, quantity=4),
                Node(id=f"p223_{uuid.uuid4().hex[:8]}", name="Purge Solenoid", level=3)
            ])
        ])
        systems.append(intake_fuel)

    # 3.0 EXHAUST
    if cfg.fuel_type != "EV":
        exhaust = Node(id=f"s3_{uuid.uuid4().hex[:8]}", name="3.0 Exhaust System", level=1, children=[
            Node(id=f"ss31_{uuid.uuid4().hex[:8]}", name="3.1 Manifold & Turbo", level=2, children=[
                Node(id=f"p311_{uuid.uuid4().hex[:8]}", name="Exhaust Manifold", level=3, weight=8500, material="Cast Iron"),
                Node(id=f"p312_{uuid.uuid4().hex[:8]}", name="Turbocharger Assy", level=3, own_cost=42000, material_calc_enabled=False)
            ]),
            Node(id=f"ss32_{uuid.uuid4().hex[:8]}", name="3.2 Aftertreatment", level=2, children=[
                Node(id=f"p321_{uuid.uuid4().hex[:8]}", name="Catalytic Converter", level=3, weight=4500, material="Steel (HSS)"),
                Node(id=f"p322_{uuid.uuid4().hex[:8]}", name="Oxygen Sensors", level=3, quantity=2, own_cost=1800, material_calc_enabled=False)
            ])
        ])
        systems.append(exhaust)

    # 4.0 COOLING
    cooling = Node(id=f"s4_{uuid.uuid4().hex[:8]}", name="4.0 Cooling System", level=1, children=[
        Node(id=f"ss41_{uuid.uuid4().hex[:8]}", name="Heat Exchangers", level=2, children=[
            Node(id=f"p411_{uuid.uuid4().hex[:8]}", name="Main Radiator", level=3, weight=6200, material="Aluminum 6061"),
            Node(id=f"p412_{uuid.uuid4().hex[:8]}", name="Expansion Tank", level=3, material="Polypropylene")
        ]),
        Node(id=f"ss42_{uuid.uuid4().hex[:8]}", name="Coolant Management", level=2, children=[
            Node(id=f"p421_{uuid.uuid4().hex[:8]}", name="Electric Water Pump", level=3, own_cost=8500),
            Node(id=f"p422_{uuid.uuid4().hex[:8]}", name="Coolant Hoses (Main)", level=3, material="Rubber (EPDM)")
        ])
    ])
    systems.append(cooling)

    # 5.0 LUBRICATION
    if cfg.fuel_type != "EV":
        lubrication = Node(id=f"s5_{uuid.uuid4().hex[:8]}", name="5.0 Lubrication System", level=1, children=[
            Node(id=f"p51_{uuid.uuid4().hex[:8]}", name="Oil Pump Assy", level=2, own_cost=5500),
            Node(id=f"p52_{uuid.uuid4().hex[:8]}", name="Oil Cooler", level=2, material="Aluminum 6061"),
            Node(id=f"p53_{uuid.uuid4().hex[:8]}", name="Oil Pan", level=2, weight=2800, material="Steel (HSS)")
        ])
        systems.append(lubrication)

    # 6.0 ELECTRICAL & ELECTRONICS
    electrical = Node(id=f"s6_{uuid.uuid4().hex[:8]}", name="6.0 Electrical & Wire Harness", level=1, children=[
        Node(id=f"ss61_{uuid.uuid4().hex[:8]}", name="Main Harness", level=2, children=[
            Node(id=f"p611_{uuid.uuid4().hex[:8]}", name="Engine Harness", level=3, weight=4500, material="Copper"),
            Node(id=f"p612_{uuid.uuid4().hex[:8]}", name="Body Harness", level=3, weight=12000, material="Copper")
        ]),
        Node(id=f"ss62_{uuid.uuid4().hex[:8]}", name="Control Modules", level=2, children=[
            Node(id=f"p621_{uuid.uuid4().hex[:8]}", name="ECU/VCU", level=3, own_cost=25000, material_calc_enabled=False),
            Node(id=f"p622_{uuid.uuid4().hex[:8]}", name="Fuse Box Assy", level=3, own_cost=4500)
        ])
    ])
    systems.append(electrical)

    # 7.0 TRANSMISSION
    trans = Node(id=f"s7_{uuid.uuid4().hex[:8]}", name="7.0 Transmission Assy", level=1)
    if cfg.trans_type == "Manual":
        trans.children = [Node(id=f"ss71_{uuid.uuid4().hex[:8]}", name="Manual Internals", level=2, children=[
            Node(id=f"p711_{uuid.uuid4().hex[:8]}", name="Shift Fork Pads", level=3, quantity=3),
            Node(id=f"f712_{uuid.uuid4().hex[:8]}", name="Synchronizer Keys", level=4, quantity=12),
            Node(id=f"f713_{uuid.uuid4().hex[:8]}", name="Detent Ball & Spring", level=4, quantity=6)
        ])]
    else:
        trans.children = [Node(id=f"ss72_{uuid.uuid4().hex[:8]}", name="Auto Valve Body", level=2, children=[
            Node(id=f"p721_{uuid.uuid4().hex[:8]}", name="Planetary Gear Set", level=3, weight=22000),
            Node(id=f"p722_{uuid.uuid4().hex[:8]}", name="Accumulator Pistons", level=3, quantity=5)
        ])]
    systems.append(trans)

    # 8.0 AWD
    if cfg.drive_type == "AWD":
        drive = Node(id=f"s8_{uuid.uuid4().hex[:8]}", name="8.0 Drivetrain (AWD)", level=1, children=[
            Node(id=f"p81_{uuid.uuid4().hex[:8]}", name="Active Transfer Case", level=2, own_cost=38000),
            Node(id=f"p82_{uuid.uuid4().hex[:8]}", name="Rear Differential", level=2, own_cost=32000, weight=25000),
            Node(id=f"f83_{uuid.uuid4().hex[:8]}", name="Differential Shims", level=4, quantity=8)
        ])
        systems.append(drive)

    # 12.0 WHEELS & TIRES
    wheels = Node(id=f"s12_{uuid.uuid4().hex[:8]}", name="12.0 Wheels & Tires", level=1, children=[
        Node(id=f"p121_{uuid.uuid4().hex[:8]}", name="Alloy Wheels", level=2, quantity=4, weight=11500, material="Aluminum 6061"),
        Node(id=f"p122_{uuid.uuid4().hex[:8]}", name="Rubber Tires", level=2, quantity=4, weight=9500, material="Rubber (EPDM)")
    ])
    systems.append(wheels)

    # 10.0 SUSPENSION & AXLES
    suspension = Node(id=f"s10_{uuid.uuid4().hex[:8]}", name="10.0 Chassis & Suspension", level=1, children=[
        Node(id=f"ss101_{uuid.uuid4().hex[:8]}", name="Front Suspension", level=2, children=[
            Node(id=f"p1011_{uuid.uuid4().hex[:8]}", name="MacPherson Struts", level=3, quantity=2, own_cost=8500),
            Node(id=f"p1012_{uuid.uuid4().hex[:8]}", name="Control Arms", level=3, quantity=2, material="Steel (HSS)")
        ]),
        Node(id=f"ss102_{uuid.uuid4().hex[:8]}", name="Rear Suspension", level=2, children=[
            Node(id=f"p1021_{uuid.uuid4().hex[:8]}", name="Multi-link Subframe", level=3, material="Steel (HSS)"),
            Node(id=f"p1022_{uuid.uuid4().hex[:8]}", name="Anti-roll Bar", level=3, weight=4500)
        ])
    ])
    systems.append(suspension)

    # 9.0 STEERING (Mirror Logic)
    steering = Node(id=f"s9_{uuid.uuid4().hex[:8]}", name=f"9.0 Steering ({cfg.steering_side})", level=1, children=[
        Node(id=f"ss91_{uuid.uuid4().hex[:8]}", name="Steering Rack Detail", level=2, children=[
            Node(id=f"p911_{uuid.uuid4().hex[:8]}", name="Rack Guide Spring", level=3),
            Node(id=f"p912_{uuid.uuid4().hex[:8]}", name="Rack Adjuster Plug", level=3)
        ]),
        Node(id=f"ss92_{uuid.uuid4().hex[:8]}", name="Column Assembly", level=2, children=[
            Node(id=f"p921_{uuid.uuid4().hex[:8]}", name="Spiral Cable (Clockspring)", level=3),
            Node(id=f"f922_{uuid.uuid4().hex[:8]}", name="Collapse Capsule", level=4)
        ])
    ])
    systems.append(steering)

    # 11.0 BRAKES
    brakes = Node(id=f"s11_{uuid.uuid4().hex[:8]}", name="11.0 Performance Brakes", level=1, children=[
        Node(id=f"ss111_{uuid.uuid4().hex[:8]}", name="Caliper Hardware", level=2, children=[
            Node(id=f"f1111_{uuid.uuid4().hex[:8]}", name="Anti-rattle Clips", level=4, quantity=8),
            Node(id=f"f1112_{uuid.uuid4().hex[:8]}", name="Caliper Dust Seals", level=4, quantity=8)
        ]),
        Node(id=f"p112_{uuid.uuid4().hex[:8]}", name="Proportioning Valve", level=2)
    ])
    systems.append(brakes)

    # 13.0 BODY
    body = Node(id=f"s13_{uuid.uuid4().hex[:8]}", name=f"13.0 Body System ({cfg.body_style})", level=1, children=[
        Node(id=f"p131_{uuid.uuid4().hex[:8]}", name="Body Structure BIW", level=2, weight=350000 if cfg.body_style=="Sedan" else 520000, material="Steel (HSS)"),
        Node(id=f"p132_{uuid.uuid4().hex[:8]}", name="Sound Deadening Pads", level=2, quantity=12, material="Composite")
    ])
    systems.append(body)

    # 15.0 FASTENERS
    fasteners = Node(id=f"s15_{uuid.uuid4().hex[:8]}", name="15.0 Fastener Library", level=1, children=[
        Node(id=f"fb1_{uuid.uuid4().hex[:8]}", name="E-Torx Bolt M10", level=4, quantity=180, own_cost=45, weight=35, material="Steel (HSS)"),
        Node(id=f"fb2_{uuid.uuid4().hex[:8]}", name="Rivnut M8 Insert", level=4, quantity=450, own_cost=12, weight=8, material="Steel (HSS)")
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

@app.post("/api/auth/initialize")
async def initialize_user_space(req: dict, db: Session = Depends(get_db)):
    username = req.get("username", "anonymous")
    role = req.get("role", "viewer")
    
    # Simulation: Log the creation of user-specific assets
    print(f"--- SECURITY LOG: Initializing isolated workspace for {username} [{role}] ---")
    print(f"--- DATABASE: Simulation table 'user_data_{username}' ensured. ---")
    
    return {
        "status": "success", 
        "message": f"Workspace for {username} initialized.",
        "assets_created": ["audit_log", f"data_{role}"]
    }

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
