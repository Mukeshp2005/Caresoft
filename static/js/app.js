/**
 * CARESOFT PROJECT ESTIMATION MANAGER - HUB & EDITOR ENGINE
 */

const LevelNames = ["Vehicle", "System", "Subsystem", "Component", "Part", "Sub-Part", "Fastener/Seal"];
const LevelColors = ["#2D3436", "#6C5CE7", "#0984E3", "#00B894", "#E17055", "#D63031", "#636E72"];
const Metals = ["Steel (HSS)", "Aluminum 6061", "Cast Iron", "Copper"];
let MATERIAL_MASTER = {};
let currentTreeData = null;
const ActivityLogs = [];
let charts = {};

// --- VIEW MANAGEMENT ---
function toggleSidebar() {
    $('.main-container').toggleClass('sidebar-collapsed');
}

function goHome() {
    showView('hub');
}

function showView(viewName) {
    $('main').hide();
    $(`#view-${viewName}`).show();
    window.scrollTo(0, 0); // Reset window scroll for the long page
    $('.nav-item').removeClass('active');

    if (viewName === 'hub') {
        loadProjectsForHub();
    } else if (viewName === 'editor') {
        loadTree();
    } else if (viewName === 'review') {
        renderReview();
    } else if (viewName === 'reporting') {
        renderReporting();
    }
}

// --- CSV EXPORT ---
function exportToCSV() {
    if (!currentTreeData) return alert("No active project to export.");
    const flat = [];
    function flatten(node) {
        flat.push({
            ID: node.display_id,
            Name: node.name,
            Level: LevelNames[node.level],
            Material: node.material,
            Weight_g: node.weight,
            Qty: node.quantity,
            Own_Cost: node.own_cost,
            Total_Cost: node.total_cost,
            CO2_kg: node.co2_footprint.toFixed(2)
        });
        if (node.children) node.children.forEach(flatten);
    }
    flatten(currentTreeData);

    let csv = "ID,Name,Level,Material,Weight(g),Qty,Own Cost,Total Cost,CO2 Footprint(kg)\n";
    flat.forEach(row => {
        csv += `"${row.ID}","${row.Name}","${row.Level}","${row.Material}",${row.Weight_g},${row.Qty},${row.Own_Cost},${row.Total_Cost},${row.CO2_kg}\n`;
    });

    const blob = new Blob([csv], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.setAttribute('href', url);
    a.setAttribute('download', `BOM_Export_${currentTreeData.name.replace(/\s+/g, '_')}.csv`);
    a.click();
}

// --- HIERARCHY NAVIGATION ---
function findParentInTree(root, targetId) {
    if (!root || !root.children) return null;
    for (const child of root.children) {
        if (child.id === targetId) return root;
        const parent = findParentInTree(child, targetId);
        if (parent) return parent;
    }
    return null;
}

function goBackToParent(currentId) {
    if (!currentTreeData) return;
    if (currentId === currentTreeData.id) {
        goHome();
        return;
    }
    const parent = findParentInTree(currentTreeData, currentId);
    if (parent) {
        selectNode(parent.id);
    } else {
        selectNode(currentTreeData.id);
    }
}

// --- ACTIVITY FEED ---
function addActivity(msg) {
    ActivityLogs.unshift({ time: new Date().toLocaleTimeString(), msg: msg });
    if (ActivityLogs.length > 5) ActivityLogs.pop();
    renderActivity();
}

function renderActivity() {
    const $feed = $('#activity-feed');
    if (!$feed.length) return;
    $feed.empty();
    ActivityLogs.forEach(a => {
        $feed.append(`
            <div class="p-3 border-bottom d-flex align-items-center animate__animated animate__fadeIn">
                <i class="fa fa-clock text-muted mr-3 small"></i>
                <div class="flex-grow-1 small font-weight-bold">${a.msg}</div>
                <div class="text-muted" style="font-size: 9px;">${a.time}</div>
            </div>
        `);
    });
}

// --- CORE LOGIC ---
async function loadMaterials() {
    const res = await fetch('/api/materials');
    MATERIAL_MASTER = await res.json();
    renderMaterialEditor();
}

function renderMaterialEditor() {
    const $container = $('#materialList');
    if (!$container.length) return;
    $container.empty();
    Object.keys(MATERIAL_MASTER).forEach(mat => {
        $container.append(`
            <div class="d-flex justify-content-between align-items-center mb-2 p-2 bg-white rounded border small">
                <span class="font-weight-bold" style="font-size: 10px;">${mat}</span>
                <div class="input-group input-group-sm" style="width: 80px;">
                    <input type="number" class="form-control mat-price-input" data-mat="${mat}" value="${MATERIAL_MASTER[mat]}">
                </div>
            </div>
        `);
    });
}

async function saveMaterialPrices() {
    const updates = {};
    $('.mat-price-input').each(function () { updates[$(this).data('mat')] = parseFloat($(this).val()) || 0; });
    await fetch('/api/materials/update', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(updates) });
    await loadMaterials();
    await loadTree();
    $('#materialCollapse').slideUp();
}

async function loadTree() {
    const response = await fetch('/api/tree');
    const data = await response.json();
    currentTreeData = data;
    if (data) {
        renderTree(data);
        if (!$('.node-row.active').length) selectNode(data.id);
    } else {
        $('#treeView').html('<div class="text-center p-5 text-muted">No Project Selected</div>');
    }
}

function renderTree(root) {
    const $container = $('#treeView');
    $container.empty();
    $container.append(buildNodeHtml(root));
}

function buildNodeHtml(node, isReadOnly = false) {
    const hasChildren = node.children && node.children.length > 0;
    const color = LevelColors[node.level] || "#ccc";
    const displayNum = node.display_id ? `<span class="mr-2 text-muted" style="font-family: monospace; font-size: 10px;">${node.display_id}</span>` : '';

    const clickAction = isReadOnly ? `selectReadOnlyNode('${node.id}')` : `selectNode('${node.id}')`;

    return `
        <div class="tree-node">
            <div class="node-row d-flex align-items-center ${isReadOnly ? 'readonly-row' : ''}" data-id="${node.id}" onclick="${clickAction}">
                <span class="lvl-indicator" style="background: ${color}"></span>
                <span class="node-name flex-grow-1">${displayNum}${node.name}</span>
                <span class="node-price mx-2">₹${Math.round(node.total_cost).toLocaleString()}</span>
                ${!isReadOnly ? `
                <button class="btn btn-sm text-primary p-0 mr-2" onclick="event.stopPropagation(); createNewBranch(event, '${node.id}')">
                    <i class="fa fa-plus-circle"></i>
                </button>
                ` : ''}
                <span class="expander text-muted" onclick="toggleChildren(event, '${node.id}')">${hasChildren ? '▼' : '•'}</span>
            </div>
            ${hasChildren ? `<div class="node-children" id="children-${node.id}">${node.children.map(c => buildNodeHtml(c, isReadOnly)).join('')}</div>` : ''}
        </div>
    `;
}

function toggleChildren(e, id) { e.stopPropagation(); $(`#children-${id}`).toggle(); }

async function selectNode(id) {
    // Only remove active class from nodes in the CURRENT visible view
    if ($('#view-editor').is(':visible')) {
        $('#view-editor .node-row').removeClass('active');
        $('#view-editor .node-row[data-id="' + id + '"]').addClass('active');
    }
    const node = findInTree(currentTreeData, id);
    if (node) renderEditor(node);
}

function findInTree(root, id) {
    if (!root) return null;
    if (root.id === id) return root;
    if (root.children) {
        for (const child of root.children) {
            const found = findInTree(child, id);
            if (found) return found;
        }
    }
    return null;
}

function renderEditor(node) {
    const $area = $('#editorArea');
    const color = LevelColors[node.level] || "#ccc";
    const matOptions = Object.keys(MATERIAL_MASTER).map(m => `<option value="${m}" ${node.material === m ? 'selected' : ''}>${m}</option>`).join('');

    const matRate = node.material_calc_enabled ? (MATERIAL_MASTER[node.material] || 0) : 0;
    const valueShouldCost = (node.weight / 1000) * matRate;
    const variance = node.own_cost - valueShouldCost;
    const efficiency = node.own_cost > 0 ? Math.max(0, Math.min(100, (valueShouldCost / node.own_cost) * 100)) : 100;

    $area.html(`
        <div class="calc-card animate__animated animate__fadeIn border-top" style="border-top-width: 8px !important; border-top-color: ${color} !important;">
            <div class="d-flex justify-content-between mb-4 pb-3 border-bottom">
                <div class="d-flex align-items-center">
                    <button class="btn btn-sm btn-outline-secondary mr-2 rounded-lg" onclick="goHome()" title="Return to Home Hub">
                        <i class="fa fa-home mr-1"></i> HOME
                    </button>
                    <button class="btn btn-sm btn-outline-secondary mr-4 rounded-lg" onclick="goBackToParent('${node.id}')" title="Go back to Parent level">
                        <i class="fa fa-arrow-left"></i>
                    </button>
                    <div class="mr-3">
                        <span class="badge px-3 py-2 mb-1 d-block" style="background: ${color}; color: white; font-weight: 800; font-size: 10px; border-radius: 6px; letter-spacing: 1px;">
                            ${(LevelNames[node.level] || 'NODE').toUpperCase()} ${node.display_id || ''}
                        </span>
                        <h1 class="mb-0 font-weight-bold h3" style="color: #1a1a1a; letter-spacing: -0.5px;">${node.name}</h1>
                    </div>
                </div>
                <div class="header-actions text-right">
                    ${(node.level === 0) ? `
                        <button class="btn btn-primary btn-sm font-weight-bold px-4 rounded-pill mb-2 shadow" onclick="markEstimationComplete()">
                            <i class="fa fa-check-circle mr-1"></i> SAVE & COMPLETE ESTIMATION
                        </button>
                    ` : ''}
                    <div class="text-success font-weight-bold small"><i class="fa fa-leaf mr-1"></i> CO2: ${node.co2_footprint.toFixed(2)} KG</div>
                </div>
            </div>
            
            <div class="row mb-5">
                <div class="col-md-4">
                    <div class="glass-card p-4">
                        <label class="input-label">UNIT COST (PROPOSED)</label>
                        <div class="input-group input-group-lg">
                            <div class="input-group-prepend"><span class="input-group-text border-0 bg-transparent">₹</span></div>
                            <input type="number" id="own-cost-input" class="form-control font-weight-bold text-primary border-0 bg-transparent" value="${node.own_cost}" onchange="updateNodeAll('${node.id}')">
                        </div>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="glass-card p-4">
                        <label class="input-label">WEIGHT (GRAMS)</label>
                        <div class="input-group input-group-lg">
                            <input type="number" id="weight-input" class="form-control font-weight-bold border-0 bg-transparent text-center" value="${node.weight}" onchange="updateNodeAll('${node.id}')">
                            <div class="input-group-append"><span class="input-group-text border-0 bg-transparent small">G</span></div>
                        </div>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="glass-card p-4 text-center">
                        <label class="input-label">BENCHMARK VALUE</label>
                        <div class="h2 font-weight-bold text-success mb-0" style="font-family: 'JetBrains Mono';">₹${valueShouldCost.toFixed(0)}</div>
                        <small class="text-muted font-weight-bold" style="font-size: 9px;">LME MARKET RATE</small>
                    </div>
                </div>
            </div>

            <div class="row mb-5">
                <div class="col-md-6 border-right">
                    <div class="p-4 bg-light rounded-lg">
                        <label class="input-label text-center d-block">VALUE EFFICIENCY</label>
                        <div class="h1 text-center mb-2 font-weight-bold ${efficiency > 80 ? 'text-success' : 'text-warning'}">${efficiency.toFixed(1)}%</div>
                        <div class="progress" style="height: 10px; border-radius: 10px; background: rgba(0,0,0,0.05);">
                            <div class="progress-bar ${efficiency > 80 ? 'bg-success' : 'bg-warning'}" style="width: ${efficiency}%"></div>
                        </div>
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="p-4 bg-dark text-white rounded-lg">
                        <label class="input-label text-white-50 text-center d-block">VARIANCE GAP</label>
                        <div class="h1 text-center mb-1 font-weight-bold ${variance > (node.own_cost * 0.4) ? 'text-danger' : 'text-white'}">₹${Math.abs(variance).toLocaleString()}</div>
                        <p class="text-center text-info small mb-0 font-weight-bold" style="font-size: 10px;">POTENTIAL COST REDUCTION</p>
                    </div>
                </div>
            </div>

            <div class="p-4 border rounded-lg bg-white mb-5 shadow-sm border-left" style="border-left-width: 6px !important; border-left-color: var(--primary) !important;">
                <label class="input-label mb-3">MATERIAL ANALYTICS ASSOCIATION</label>
                <select id="material-select" class="form-control form-control-lg border-0 bg-light mb-3" onchange="updateNodeAll('${node.id}')" style="border-radius: 12px; font-weight: 700;">
                    <option value="Unassigned">Select Commodity Grade...</option>
                    ${matOptions}
                </select>

                ${Metals.includes(node.material) ? `
                    <div class="custom-control custom-switch">
                        <input type="checkbox" class="custom-control-input" id="mat-calc-toggle" ${node.material_calc_enabled ? 'checked' : ''} onchange="updateNodeAll('${node.id}')">
                        <label class="custom-control-label font-weight-bold" for="mat-calc-toggle" style="cursor: pointer;">Enable Real-time LME Market Indexing</label>
                    </div>
                ` : `
                    <div class="small text-muted font-italic"><i class="fa fa-info-circle mr-1"></i> Indexing unavailable for non-metal grades.</div>
                `}
            </div>

            <div class="d-flex justify-content-between align-items-center mb-3">
                <h6 class="input-label mb-0">SUB-ASSEMBLIES / CHILD NODES</h6>
                <button class="btn btn-danger btn-sm font-weight-bold px-3 rounded-lg" onclick="deleteNode('${node.id}')">
                    <i class="fa fa-trash-alt mr-1"></i> DELETE NODE
                </button>
            </div>
            
            <div class="branch-grid">
                ${node.children.map(c => `
                    <div class="btn btn-outline-light text-left p-3 border shadow-sm glass-card" onclick="selectNode('${c.id}')" style="position: relative; overflow: hidden; height: auto;">
                        <div style="position: absolute; left: 0; top: 0; bottom: 0; width: 4px; background: ${LevelColors[c.level] || '#ccc'};"></div>
                        <small class="d-block text-muted font-weight-bold mb-1" style="font-size: 9px;">${(LevelNames[c.level] || 'SUB').toUpperCase()}</small>
                        <div class="font-weight-bold text-dark" style="font-size: 0.9rem; line-height: 1.2;">${c.name}</div>
                        <div class="text-primary mt-2 font-weight-bold">₹${Math.round(c.total_cost).toLocaleString()}</div>
                    </div>
                `).join('')}
                
                <button class="btn btn-outline-primary p-3 d-flex flex-column justify-content-center align-items-center" 
                     style="border: 2px dashed var(--primary); background: rgba(108, 92, 231, 0.03); border-radius: 15px; min-height: 100px; transition: all 0.2s;" 
                     onclick="createNewBranch(null, '${node.id}')">
                    <i class="fa fa-plus-circle mb-2" style="font-size: 1.5rem;"></i>
                    <div class="font-weight-bold small">ADD CHILD NODE</div>
                </button>
            </div>
        </div>
    `);
}

async function markEstimationComplete() {
    if (!confirm("Are you sure you want to mark this project as complete? It will move to Cost Review archives.")) return;
    await fetch('/api/project/complete', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ id: currentTreeData.id })
    });
    addActivity(`Finalized Program: ${currentTreeData.name}`);
    showView('hub');
}

async function createNewBranch(event, parentId) {
    if (event) event.stopPropagation();
    const name = prompt("Enter Name for new Branch:");
    if (!name) return;
    const isMetal = confirm("Enable metal calculation logic for this part?");

    const response = await fetch('/api/node/add', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            parent_id: parentId,
            name: name,
            material_calc_enabled: isMetal
        })
    });

    const result = await response.json();

    if (result.status === "error") {
        alert(result.message || "Failed to create node");
        return;
    }

    await loadTree();
    selectNode(parentId);
}


async function deleteNode(id) {
    if (!confirm("Remove this branch and all its costs?")) return;

    const response = await fetch('/api/node/delete', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ id: id })
    });

    const result = await response.json();

    if (result.status === "error") {
        alert(result.message || "Cannot delete this node");
        return;
    }

    await loadTree();
    selectNode(currentTreeData.id);
}


async function startNewProject() {
    $('#projectModal').modal('show');
}

async function confirmCreateProject() {
    const config = {
        brand: $('#cfg-brand').val() || "Unknown",
        model: $('#cfg-model').val() || "Model",
        year: parseInt($('#cfg-year').val()) || 2024,
        fuel_type: $('#cfg-fuel').val(),
        trans_type: $('#cfg-trans').val(),
        drive_type: $('#cfg-drive').val(),
        body_style: $('#cfg-body').val(),
        steering_side: $('#cfg-steer').val()
    };
    await fetch('/api/project/new', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(config)
    });
    addActivity(`Created new project: ${config.brand} ${config.model}`);
    $('#projectModal').modal('hide');
    showView('editor');
}

async function updateNodeAll(id) {
    const payload = {
        id: id,
        own_cost: parseFloat($('#own-cost-input').val()) || 0,
        weight: parseFloat($('#weight-input').val()) || 0,
        material: $('#material-select').val(),
        material_calc_enabled: $('#mat-calc-toggle').is(':checked')
    };
    await fetch('/api/node/update', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) });
    await loadTree();
    const node = findInTree(currentTreeData, id);
    if (node) renderEditor(node);
}

function renderSpecs(project) {
    if (!project || !project.config) return;
    $('#active-specs-panel').show();
    const $grid = $('#specs-grid');
    $grid.empty();
    const config = project.config;
    const specs = [
        { l: "FUEL", v: config.fuel_type, i: "fa-gas-pump" },
        { l: "TRANS", v: config.trans_type, i: "fa-cog" },
        { l: "DRIVE", v: config.drive_type, i: "fa-crosshairs" },
        { l: "BODY", v: config.body_style, i: "fa-car" }
    ];
    specs.forEach(s => {
        $grid.append(`
            <div class="col-6 mb-2">
                <div class="d-flex align-items-center">
                    <i class="fa ${s.i} text-muted mr-2" style="font-size: 10px;"></i>
                    <div style="line-height:1;">
                        <small class="text-muted d-block" style="font-size: 7px; font-weight:700;">${s.l}</small>
                        <span class="font-weight-bold" style="font-size: 10px; color: #34495e;">${s.v}</span>
                    </div>
                </div>
            </div>
        `);
    });
}

async function deleteProject(id, event) {
    if (event) event.stopPropagation();
    if (!confirm("Delete this entire project? This cannot be undone.")) return;
    await fetch('/api/project/delete', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ id: id })
    });
    addActivity(`Deleted project: ${id}`);
    loadProjectsForHub();
}

async function selectAndPulse(id, targetView = 'editor') {
    await fetch('/api/project/select', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ id: id })
    });
    addActivity(`Loaded project: ${id}`);

    // Fetch fresh tree data before showing view
    const res = await fetch('/api/tree');
    currentTreeData = await res.json();

    showView(targetView);
}

async function viewCompletedProject(id) {
    await selectAndPulse(id, 'review');
}

async function loadProjectsForHub() {
    const res = await fetch('/api/projects');
    const projects = await res.json();

    let activeProject = projects.length > 0 ? projects[projects.length - 1] : null;
    $('#stat-veh-count').text(projects.length);

    if (activeProject) {
        $('#stat-part-count').text(activeProject.tracked_parts || 0);
        const progress = activeProject.part_count > 0 ? Math.round((activeProject.tracked_parts / activeProject.part_count) * 100) : 0;
        $('#stat-accuracy').text(progress + '%');
        renderSpecs(activeProject);
    } else {
        $('#stat-part-count').text(0);
        $('#stat-accuracy').text('0%');
        $('#active-specs-panel').hide();
    }

    const $activeList = $('.active-projects-list');
    const $completedList = $('#completed-projects-list');
    $activeList.empty();
    $completedList.empty();

    projects.forEach(p => {
        const isCompleted = p.status === 'Completed';
        // Active projects in Builder go to 'editor', Completed in Review go to 'review'
        const clickAction = isCompleted ? `selectAndPulse('${p.id}', 'review')` : `selectAndPulse('${p.id}', 'editor')`;
        const html = `
            <div class="project-item p-3 border rounded d-flex align-items-center mb-3 glass-card" style="cursor: pointer;" onclick="if (!event.target.closest('button')) ${clickAction}">
                <div class="p-icon bg-light text-primary p-2 rounded-lg mr-3 shadow-sm" style="width: 45px; text-align: center;">
                    <i class="fa fa-car"></i>
                </div>
                <div class="flex-grow-1">
                    <div class="font-weight-bold" style="font-size: 1.1rem;">${p.name}</div>
                    <div class="text-muted" style="font-size: 13px;">Cost: <span class="text-dark font-weight-bold">₹${Math.round(p.total_cost).toLocaleString()}</span> | BOM: ${p.tracked_parts}/${p.part_count}</div>
                </div>
                <!-- Action buttons -->
                <div class="d-flex">
                    <button class="btn btn-sm btn-outline-danger border-0 p-2 ml-2" onclick="deleteProject('${p.id}', event)" title="Delete Project">
                        <i class="fa fa-trash-alt"></i>
                    </button>
                </div>
            </div>
        `;
        if (p.status === 'In-Progress') {
            $activeList.append(html);
        } else {
            $completedList.append(html);
        }
    });

    if ($completedList.is(':empty')) {
        $completedList.html('<div class="text-center py-4 text-muted small border rounded dashed">No finalized reports.</div>');
        $('#review-expand-icon').hide();
    } else {
        $('#review-expand-icon').show();
    }
}

async function renderReview() {
    const res = await fetch('/api/tree');
    const root = await res.json();
    currentTreeData = root;
    const $container = $('#review-content');
    $container.empty();

    if (!root) {
        $container.html('<div class="text-center py-5">No active project to review.</div>');
        return;
    }

    $container.append(`
        <div class="d-flex flex-column h-100">
            <!-- REVIEW HEADER -->
            <div class="p-4 bg-white border-bottom d-flex justify-content-between align-items-center shadow-sm">
                <div>
                    <h2 class="font-weight-bold mb-0" style="letter-spacing: -1.5px; color: #1a1a1a;">Cost Review & Analysis</h2>
                    <p class="text-muted mb-0 small uppercase font-weight-bold">Program: ${root.name} | Status: <span class="text-success">${root.status || 'Active'}</span></p>
                </div>
                <div class="d-flex align-items-center">
                    <button class="btn btn-outline-primary btn-sm px-4 mr-2 rounded-pill font-weight-bold" onclick="exportToCSV()">
                        <i class="fa fa-file-csv mr-2"></i> EXCEL EXPORT
                    </button>
                    <button class="btn btn-dark btn-sm px-4 rounded-pill font-weight-bold" onclick="showView('hub')">
                        <i class="fa fa-home mr-2"></i> BACK TO HUB
                    </button>
                </div>
            </div>

            <div class="d-flex flex-grow-1 overflow-hidden">
                <!-- LEFT: TREE LIST (400px) -->
                <div class="glass-card m-3 d-flex flex-column shadow-lg" style="width: 400px; border-radius: 15px;">
                    <div class="p-3 border-bottom bg-light d-flex justify-content-between align-items-center">
                        <h6 class="mb-0 font-weight-bold small"><i class="fa fa-sitemap mr-2"></i>B.O.M. ARCHITECTURE</h6>
                    </div>
                    <div class="p-2 overflow-auto flex-grow-1">
                        <div id="reviewTreeView"></div>
                    </div>
                </div>

                <!-- RIGHT: ANALYTICS AREA (Flexible) -->
                <div id="reviewDetailArea" class="flex-grow-1 m-3 overflow-auto">
                    <div class="glass-card p-5 text-center text-muted h-100 d-flex flex-column justify-content-center shadow-lg" style="border-radius: 15px;">
                        <i class="fa fa-microchip mb-4 text-primary" style="font-size: 5rem; opacity: 0.1;"></i>
                        <h3 class="font-weight-bold text-dark">Intelligence Hub</h3>
                        <p>Select any node from the BOM architecture on the left to activate teardown intelligence and raw material indexing for this component.</p>
                    </div>
                </div>
            </div>
        </div>
    `);

    $('#reviewTreeView').html(buildNodeHtml(root, true));
}

function selectReadOnlyNode(id) {
    const node = findInTree(currentTreeData, id);
    if (!node) return;

    $('.node-row').removeClass('active');
    $(`.node-row[data-id="${id}"]`).addClass('active');

    const color = LevelColors[node.level] || "#ccc";
    const matRate = node.material_calc_enabled ? (MATERIAL_MASTER[node.material] || 0) : 0;
    const benchmarkValue = (node.weight / 1000) * matRate;
    const efficiency = node.own_cost > 0 ? (benchmarkValue / node.own_cost) * 100 : 100;

    $('#reviewDetailArea').html(`
        <div class="glass-card p-4 animate__animated animate__fadeIn border-top" style="border-top: 6px solid ${color} !important;">
            <div class="d-flex justify-content-between align-items-center mb-4 border-bottom pb-3">
                <div>
                    <span class="badge badge-secondary mb-1">${LevelNames[node.level].toUpperCase()} Report</span>
                    <h3 class="font-weight-bold mb-0">${node.name}</h3>
                </div>
                <div class="text-right">
                    <div class="h3 font-weight-bold text-primary mb-0">₹${node.total_cost.toLocaleString()}</div>
                    <small class="text-muted font-weight-bold">TOTAL ROLLUP COST</small>
                </div>
            </div>

            <div class="row mb-4">
                <div class="col-md-6">
                    <div class="p-3 bg-light rounded-lg border text-center">
                        <label class="input-label mb-1">Teardown Unit Cost</label>
                        <div class="h4 font-weight-bold text-dark">₹${node.own_cost.toLocaleString()}</div>
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="p-3 bg-light rounded-lg border text-center">
                        <label class="input-label mb-1">LME Benchmark</label>
                        <div class="h4 font-weight-bold text-success">₹${benchmarkValue.toFixed(2)}</div>
                    </div>
                </div>
            </div>

            <div class="glass-card p-4 bg-dark text-white mb-4">
                <div class="d-flex justify-content-between align-items-center">
                    <div>
                        <label class="input-label text-white-50 mb-1">Value Efficiency Rating</label>
                        <div class="h2 font-weight-bold ${efficiency > 80 ? 'text-success' : 'text-warning'}">${efficiency.toFixed(1)}%</div>
                    </div>
                    <div style="width: 100px; height: 10px; background: rgba(255,255,255,0.1); border-radius: 10px; position: relative;">
                        <div style="width: ${efficiency}%; height: 100%; background: ${efficiency > 80 ? '#00b894' : '#fbc531'}; border-radius: 10px;"></div>
                    </div>
                </div>
            </div>

            <div class="mb-4">
                <h6 class="input-label mb-3">Material & Sustainability Specs</h6>
                <div class="row">
                    <div class="col-6 mb-2">
                        <div class="small text-muted">MATERIAL GRADE</div>
                        <div class="font-weight-bold">${node.material}</div>
                    </div>
                    <div class="col-6 mb-2">
                        <div class="small text-muted">MASS WEIGHT</div>
                        <div class="font-weight-bold">${node.weight} G</div>
                    </div>
                    <div class="col-6 mb-2">
                        <div class="small text-muted">CO2 FOOTPRINT</div>
                        <div class="font-weight-bold">${node.co2_footprint.toFixed(2)} KG</div>
                    </div>
                    <div class="col-6 mb-2">
                        <div class="small text-muted">TRACKING LOGIC</div>
                        <div class="font-weight-bold text-info">${node.material_calc_enabled ? 'MARKET INDEXED' : 'FIXED COST'}</div>
                    </div>
                </div>
            </div>
            
            ${node.children.length > 0 ? `
                <h6 class="input-label mb-3">Rollup Subcomponents (${node.children.length})</h6>
                <div class="subcomponent-list border rounded p-2 bg-light" style="max-height: 200px; overflow-y: auto;">
                    ${node.children.map(c => `
                        <div class="d-flex justify-content-between align-items-center p-2 border-bottom last-child-border-0">
                            <span class="small font-weight-bold">${c.name}</span>
                            <span class="small text-primary font-weight-bold">₹${Math.round(c.total_cost).toLocaleString()}</span>
                        </div>
                    `).join('')}
                </div>
            ` : ''}
        </div>
    `);
}

function getFlattenedParts(node, list = []) {
    if (node.level >= 2) list.push(node);
    if (node.children) node.children.forEach(c => getFlattenedParts(c, list));
    return list;
}

async function renderReporting() {
    const res = await fetch('/api/tree');
    const root = await res.json();
    currentTreeData = root;
    if (!root) return;

    // MATERIAL MIX CHART
    const matWeights = {};
    function collectWeights(n) {
        if (n.material !== "Unassigned") {
            matWeights[n.material] = (matWeights[n.material] || 0) + (n.weight * n.quantity);
        }
        n.children.forEach(collectWeights);
    }
    collectWeights(root);

    if (charts.materials) charts.materials.destroy();
    charts.materials = new Chart(document.getElementById('materialMixChart'), {
        type: 'doughnut',
        data: {
            labels: Object.keys(matWeights),
            datasets: [{
                data: Object.values(matWeights),
                backgroundColor: ['#6C5CE7', '#00CEC9', '#E17055', '#FDCB6E', '#00B894', '#636E72']
            }]
        },
        options: { responsive: true, maintainAspectRatio: false }
    });

    // COST BY LEVEL CHART
    const levelCosts = [0, 0, 0, 0, 0, 0];
    function collectLevelCosts(n) {
        if (n.level < 6) levelCosts[n.level] += n.own_cost;
        n.children.forEach(collectLevelCosts);
    }
    collectLevelCosts(root);

    if (charts.levels) charts.levels.destroy();
    charts.levels = new Chart(document.getElementById('costBreakdownChart'), {
        type: 'polarArea',
        data: {
            labels: LevelNames.slice(0, 6),
            datasets: [{
                data: levelCosts,
                backgroundColor: ['#2D3436', '#6C5CE7', '#0984E3', '#00B894', '#E17055', '#D63031']
            }]
        },
        options: { responsive: true, maintainAspectRatio: false }
    });

    const $container = $('#report-grid');
    $container.empty();

    const cards = [
        { title: "Executive Summary", icon: "fa-project-diagram", color: "text-primary", desc: "View a visual, printable summary of the entire project teardown.", action: "renderProjectReport()" },
        { title: "BOM Export (CSV)", icon: "fa-file-csv", color: "text-info", desc: "Download full Bill of Materials in raw CSV format for Excel.", action: "exportToCSV()" },
        { title: "Material Benchmark", icon: "fa-balance-scale", color: "text-warning", desc: "Detailed comparison of current costs against LME indices.", action: "alert('Advanced Benchmark module loading...')" },
        { title: "Sustainability Report", icon: "fa-leaf", color: "text-success", desc: "Environmental impact analysis based on global CO2 standards.", action: "alert('CO2 module loading...')" }
    ];

    cards.forEach(c => {
        $container.append(`
            <div class="col-md-6 mb-4">
                <div class="glass-card p-5 text-center h-100 animate__animated animate__fadeInUp">
                    <i class="fa ${c.icon} ${c.color} mb-4" style="font-size: 3rem; opacity: 0.8;"></i>
                    <h4 class="font-weight-bold">${c.title}</h4>
                    <p class="text-muted small">${c.desc}</p>
                    <button class="btn btn-outline-dark font-weight-bold mt-3 px-4 rounded-lg" onclick="${c.action}">GENERATE REPORT</button>
                </div>
            </div>
        `);
    });
}

function filterTree() {
    const val = $('#tree-search').val().toLowerCase();
    $('.tree-node').each(function () {
        const text = $(this).find('.node-name').first().text().toLowerCase();
        $(this).toggle(text.includes(val));
    });
}

async function renderProjectReport() {
    const res = await fetch('/api/tree');
    const root = await res.json();
    if (!root) return alert("No active project data.");

    const $container = $('#report-grid');
    $container.empty();
    $container.append(`
        <div class="col-12">
            <div class="glass-card p-5 animate__animated animate__fadeIn">
                <div class="d-flex justify-content-between align-items-start mb-5 pb-4 border-bottom">
                    <div>
                        <h1 class="font-weight-bold mb-1" style="letter-spacing: -2px;">EXECUTIVE B.O.M. REPORT</h1>
                        <p class="text-muted mb-0">Program: ${root.name} | Generated: ${new Date().toLocaleDateString()}</p>
                    </div>
                    <button class="btn btn-dark px-4" onclick="window.print()"><i class="fa fa-print mr-2"></i> PRINT REPORT</button>
                </div>

                <div class="row mb-5">
                    <div class="col-md-3 border-right">
                        <small class="text-muted font-weight-bold d-block mb-1">TOTAL PROJECT COST</small>
                        <div class="h2 font-weight-bold text-primary">₹${Math.round(root.total_cost).toLocaleString()}</div>
                    </div>
                    <div class="col-md-3 border-right">
                        <small class="text-muted font-weight-bold d-block mb-1">VEHICLE MASS</small>
                        <div class="h2 font-weight-bold text-dark">${(root.total_weight / 1000).toFixed(1)} KG</div>
                    </div>
                    <div class="col-md-3 border-right">
                        <small class="text-muted font-weight-bold d-block mb-1">CO2 FOOTPRINT</small>
                        <div class="h2 font-weight-bold text-success">${root.co2_footprint.toFixed(1)} KG</div>
                    </div>
                    <div class="col-md-3">
                        <small class="text-muted font-weight-bold d-block mb-1">COMPONENTS</small>
                        <div class="h2 font-weight-bold text-info">${getFlattenedParts(root).length}</div>
                    </div>
                </div>

                <div class="row mb-5">
                    <div class="col-md-6">
                        <h6 class="input-label mb-4">Cost Distribution by System</h6>
                        <div style="height: 300px;"><canvas id="reportCostChart"></canvas></div>
                    </div>
                    <div class="col-md-6">
                        <h6 class="input-label mb-4">Material Constitution</h6>
                        <div style="height: 300px;"><canvas id="reportMatChart"></canvas></div>
                    </div>
                </div>

                <h6 class="input-label mb-3">Top 10 High-Value Assemblies</h6>
                <table class="table table-sm border">
                    <thead class="bg-light">
                        <tr>
                            <th>ASSEMBLY NAME</th>
                            <th class="text-right">TOTAL ROLLUP COST</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${root.children.sort((a, b) => b.total_cost - a.total_cost).slice(0, 10).map(c => `
                            <tr>
                                <td class="font-weight-bold">${c.name}</td>
                                <td class="text-right font-weight-bold text-primary">₹${Math.round(c.total_cost).toLocaleString()}</td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
        </div>
    `);

    // Generate Charts for PDF/Print View
    setTimeout(() => {
        new Chart(document.getElementById('reportCostChart').getContext('2d'), {
            type: 'bar',
            data: {
                labels: root.children.map(c => c.name),
                datasets: [{ label: 'Cost ₹', data: root.children.map(c => c.total_cost), backgroundColor: '#6C5CE7' }]
            },
            options: { responsive: true, maintainAspectRatio: false }
        });

        const matWeights = {};
        function colW(n) { if (n.material !== "Unassigned") matWeights[n.material] = (matWeights[n.material] || 0) + (n.weight * n.quantity); n.children.forEach(colW); }
        colW(root);

        new Chart(document.getElementById('reportMatChart').getContext('2d'), {
            type: 'pie',
            data: {
                labels: Object.keys(matWeights),
                datasets: [{ data: Object.values(matWeights), backgroundColor: ['#00CEC9', '#6C5CE7', '#E17055', '#FDCB6E', '#00B894'] }]
            },
            options: { responsive: true, maintainAspectRatio: false }
        });
    }, 100);
}

$(document).ready(async () => {
    await loadMaterials();
    showView('hub');
});
function toggleReviewHeight(event) {
    if (event) event.stopPropagation();
    const $container = $('#completed-projects-list');
    const $icon = $('#review-expand-icon');

    // Switch between a standard view and fully expanded
    if ($container.css('max-height') === 'none' || $container.css('max-height') === '2000px') {
        $container.css('max-height', '500px');
        $icon.removeClass('active');
    } else {
        $container.css('max-height', 'none');
        $icon.addClass('active');
    }
}
