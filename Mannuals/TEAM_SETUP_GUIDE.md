# 🚀 CareSoft - Team Setup Guide

## Complete Setup Instructions for New Team Members

This guide will help your team clone and run the CareSoft project with PostgreSQL database integration.

---

## 📋 Prerequisites

Before starting, ensure you have:

- ✅ **Git** installed
- ✅ **Docker** installed (version 20.10 or higher)
- ✅ **Docker Compose** installed (or Docker Desktop which includes it)
- ✅ **Poetry** installed (optional, for local development outside Docker)

### Check Prerequisites

```bash
# Check Git
git --version

# Check Docker
docker --version

# Check Docker Compose
docker compose version
```

---

## 🔧 Step-by-Step Setup

### **Step 1: Clone the Repository**

```bash
# Clone the repository
git clone <your-repo-url>

# Navigate to project directory
cd Caresoft
```

---

### **Step 2: Set Up Environment Variables**

```bash
# Copy the example environment file
cp .env.example .env
```

**Optional:** Edit `.env` if you want to change database credentials:

```bash
# Open .env in your editor
nano .env
# or
code .env
```

**Default values (already configured):**
```env
DATABASE_URL=postgresql://caresoft_user:caresoft_password@db:5432/caresoft_db
APP_ENV=development
SECRET_KEY=your-secret-key-change-in-production
```

⚠️ **Note:** For production, change `SECRET_KEY` and database credentials!

---

### **Step 3: Build and Start the Application**

```bash
# Build and start all services (database + web app)
docker compose up --build -d
```

**What this does:**
- 🐳 Builds the Docker image for the web application
- 🗄️ Pulls PostgreSQL 15 image
- 🚀 Starts both containers in detached mode
- 📊 Creates database tables automatically
- ✅ Sets up health checks

**Expected output:**
```
[+] Building ...
[+] Running 3/3
 ✔ Network caresoft_default        Created
 ✔ Container caresoft_postgres     Started
 ✔ Container caresoft_web          Started
```

---

### **Step 4: Verify Everything is Running**

```bash
# Check container status
docker compose ps
```

**Expected output:**
```
NAME                IMAGE              STATUS         PORTS
caresoft_postgres   postgres:15-alpine Up (healthy)   0.0.0.0:5432->5432/tcp
caresoft_web        caresoft-web       Up             0.0.0.0:8000->8000/tcp
```

Both containers should show **"Up"** status.

---

### **Step 5: Check Application Logs**

```bash
# View logs from both services
docker compose logs -f

# Or view logs from specific service
docker compose logs web -f
docker compose logs db -f
```db

**Look for:**
```
caresoft_web  | INFO:     Uvicorn running on http://0.0.0.0:8000
caresoft_web  | INFO:     Application startup complete.
```

Press `Ctrl+C` to stop viewing logs.

---

### **Step 6: Access the Application**

Open your browser and go to:

```
http://localhost:8000
```

**You should see:**
- ✅ CareSoft homepage with Module Hub
- ✅ Cost Tree Builder card
- ✅ No errors in browser console

---

### **Step 7: Verify Database Connection**

#### **Option A: Using the Application**

1. Click **"+ Create New Project"**
2. Fill in vehicle details
3. Click **"Start Building Tree"**
4. ✅ Project should be created and saved to database

#### **Option B: Using Database CLI**

```bash
# Connect to PostgreSQL
docker exec -it caresoft_postgres psql -U caresoft_user -d caresoft_db

# List tables
\dt

# View projects
SELECT * FROM projects;

# View nodes count
SELECT COUNT(*) FROM nodes;

# Exit
\q
```

---

## 🧪 Test the Application

### **Test 1: Create a Project**

1. Go to http://localhost:8000
2. Click **"+ Create New Project"**
3. Enter:
   - Brand: `Tata`
   - Model: `Nexon`
   - Year: `2024`
   - Fuel: `EV`
   - Other details as needed
4. Click **"Start Building Tree"**
5. ✅ Should see the cost tree editor

### **Test 2: Add a Node**

1. In the tree view, click the **+ icon** next to any node
2. Enter a name: `Test Component`
3. Choose material calculation option
4. ✅ Node should be added to tree

### **Test 3: Edit a Node**

1. Click on any node in the tree
2. Edit the cost, weight, or material
3. ✅ Changes should save automatically

### **Test 4: Delete a Node**

1. Select a non-root node
2. Click **"DELETE NODE"** button
3. Confirm deletion
4. ✅ Node should be removed

### **Test 5: Verify Database Persistence**

```bash
# Stop the application
docker compose down

# Start it again
docker compose up -d

# Open http://localhost:8000
# Your projects should still be there! ✅
```

---

## 🛠️ Common Commands

### **Start the Application**

```bash
docker compose up -d
```

### **Stop the Application**

```bash
docker compose down
```

### **Stop and Remove All Data** (⚠️ Deletes database!)

```bash
docker compose down -v
```

### **View Logs**

```bash
# All services
docker compose logs -f

# Web service only
docker compose logs web -f

# Last 50 lines
docker compose logs web --tail=50
```

### **Restart Services**

```bash
# Restart all
docker compose restart

# Restart web only
docker compose restart web
```

### **Rebuild After Code Changes**

```bash
# Rebuild and restart
docker compose up --build -d
```

### **Access Database**

```bash
# PostgreSQL CLI
docker exec -it caresoft_postgres psql -U caresoft_user -d caresoft_db

# Run SQL query directly
docker exec caresoft_postgres psql -U caresoft_user -d caresoft_db -c "SELECT * FROM projects;"
```

---

## 📁 Project Structure

```
Caresoft/
├── app/
│   ├── main.py           # FastAPI application
│   ├── database.py       # Database connection
│   ├── models.py         # SQLAlchemy models
│   └── crud.py           # Database operations
├── static/
│   ├── css/
│   │   └── styles.css    # Application styles
│   └── js/
│       └── app.js        # Frontend JavaScript
├── templates/
│   └── index.html        # Main HTML template
├── docker-compose.yaml   # Docker services configuration
├── Dockerfile            # Web app container definition
├── pyproject.toml        # Poetry dependencies
├── poetry.lock           # Locked dependency versions
├── .env                  # Environment variables (create from .env.example)
├── .env.example          # Environment template
└── .gitignore           # Git ignore rules
```

---

## 🔍 Troubleshooting

### **Problem: Port Already in Use**

**Error:** `Bind for 0.0.0.0:8000 failed: port is already allocated`

**Solution:**
```bash
# Find what's using port 8000
lsof -i :8000  # Mac/Linux
netstat -ano | findstr :8000  # Windows

# Kill the process or change port in docker-compose.yaml
ports:
  - "8001:8000"  # Use port 8001 instead
```

### **Problem: Database Connection Failed**

**Error:** `could not connect to server`

**Solution:**
```bash
# Check if database is healthy
docker compose ps

# View database logs
docker compose logs db

# Restart database
docker compose restart db
```

### **Problem: Container Won't Start**

**Solution:**
```bash
# Remove all containers and volumes
docker compose down -v

# Rebuild from scratch
docker compose up --build -d

# Check logs for errors
docker compose logs -f
```

### **Problem: Changes Not Reflecting**

**Solution:**
```bash
# Hard refresh browser (clear cache)
Ctrl + Shift + R  # Windows/Linux
Cmd + Shift + R   # Mac

# Or rebuild containers
docker compose up --build -d
```

### **Problem: Database Tables Not Created**

**Solution:**
```bash
# Run the initialization script
docker exec caresoft_web python init_db.py

# Or restart the web service
docker compose restart web
```

---

## 🔐 Security Notes

### **For Development:**
- ✅ Default credentials are fine
- ✅ Database is only accessible on localhost

### **For Production:**
1. **Change database credentials** in `.env`:
   ```env
   DATABASE_URL=postgresql://prod_user:strong_password@db:5432/caresoft_db
   ```

2. **Update docker-compose.yaml** with new credentials:
   ```yaml
   environment:
     POSTGRES_USER: prod_user
     POSTGRES_PASSWORD: strong_password
   ```

3. **Change SECRET_KEY** in `.env`:
   ```env
   SECRET_KEY=generate-a-strong-random-key-here
   ```

4. **Don't commit `.env`** to Git (already in `.gitignore`)

---

## 💾 Database Backup & Restore

### **Backup Database**

```bash
# Create backup
docker exec caresoft_postgres pg_dump -U caresoft_user caresoft_db > backup_$(date +%Y%m%d).sql

# Backup with compression
docker exec caresoft_postgres pg_dump -U caresoft_user caresoft_db | gzip > backup_$(date +%Y%m%d).sql.gz
```

### **Restore Database**

```bash
# Restore from backup
docker exec -i caresoft_postgres psql -U caresoft_user caresoft_db < backup_20260210.sql

# Restore from compressed backup
gunzip -c backup_20260210.sql.gz | docker exec -i caresoft_postgres psql -U caresoft_user caresoft_db
```

---

## 📊 Database Schema

### **Projects Table**
```sql
CREATE TABLE projects (
    id VARCHAR PRIMARY KEY,
    name VARCHAR NOT NULL,
    status VARCHAR,
    config JSON NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP
);
```

### **Nodes Table**
```sql
CREATE TABLE nodes (
    id VARCHAR PRIMARY KEY,
    project_id VARCHAR REFERENCES projects(id) ON DELETE CASCADE,
    parent_id VARCHAR REFERENCES nodes(id) ON DELETE CASCADE,
    name VARCHAR NOT NULL,
    level INTEGER NOT NULL,
    own_cost FLOAT DEFAULT 0.0,
    weight FLOAT DEFAULT 0.0,
    quantity INTEGER DEFAULT 1,
    material VARCHAR DEFAULT 'Unassigned',
    material_calc_enabled BOOLEAN DEFAULT TRUE,
    total_cost FLOAT DEFAULT 0.0,
    total_weight FLOAT DEFAULT 0.0,
    co2_footprint FLOAT DEFAULT 0.0,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP
);
```

---

## 🎯 Quick Start Checklist

- [ ] Clone repository
- [ ] Copy `.env.example` to `.env`
- [ ] Run `docker compose up --build -d`
- [ ] Check `docker compose ps` (both containers "Up")
- [ ] Open http://localhost:8000
- [ ] Create a test project
- [ ] Verify data persists after restart

---

## 🆘 Getting Help

### **Check Logs**
```bash
docker compose logs -f
```

### **Check Container Status**
```bash
docker compose ps
```

### **Access Database**
```bash
docker exec -it caresoft_postgres psql -U caresoft_user -d caresoft_db
```

### **Restart Everything**
```bash
docker compose restart
```

### **Start Fresh** (⚠️ Deletes all data!)
```bash
docker compose down -v
docker compose up --build -d
```

---

## ✅ Success Indicators

You'll know everything is working when:

✅ `docker compose ps` shows both containers as "Up"  
✅ http://localhost:8000 loads without errors  
✅ You can create a new project  
✅ You can add/edit/delete nodes  
✅ Data persists after `docker compose restart`  
✅ Database queries return data  

---

## 🎉 You're All Set!

Your team can now:

1. **Clone the repository**
2. **Run `docker compose up --build -d`**
3. **Start developing!**

All database operations are handled automatically. No manual setup required!

---

## 📚 Additional Documentation

- **Database Guide**: `README_DATABASE.md`
- **Quick Reference**: `QUICK_REFERENCE.md`
- **All Features**: `ALL_FEATURES_FIXED.md`
- **Cache Instructions**: `CLEAR_CACHE_INSTRUCTIONS.md`

---

**Happy Coding! 🚀**
