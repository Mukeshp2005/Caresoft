# CareSoft - PostgreSQL Database Integration

## 🚀 Quick Start with Docker

### 1. Start the Application with Database

```bash
# Build and start both PostgreSQL and the web application
docker-compose up --build
```

The application will be available at:
- **Web App**: http://localhost:8000
- **PostgreSQL**: localhost:5432

### 2. Stop the Application

```bash
docker-compose down
```

### 3. Stop and Remove All Data (including database)

```bash
docker-compose down -v
```

---

## 📦 Database Configuration

### Environment Variables

The application uses the following environment variables (defined in `.env`):

```env
DATABASE_URL=postgresql://caresoft_user:caresoft_password@db:5432/caresoft_db
APP_ENV=development
SECRET_KEY=your-secret-key-change-in-production
```

### Database Credentials

- **Database**: `caresoft_db`
- **User**: `caresoft_user`
- **Password**: `caresoft_password`
- **Host**: `db` (in Docker) or `localhost` (local development)
- **Port**: `5432`

---

## 🛠️ Local Development (without Docker)

### 1. Install Dependencies

You need **PostgreSQL**, **Python 3.9+**, and **Poetry** installed.

```bash
# Install dependencies with Poetry
poetry install
```

### 2. Configure Database

Make sure PostgreSQL is running locally and create a database/user as defined in your `.env`.

### 3. Run Application

```bash
# Run with Poetry
poetry run uvicorn app.main:app --reload
```

---

## 📊 Database Schema

### Tables

#### **projects**
- `id` (String, Primary Key)
- `name` (String)
- `status` (String) - "In-Progress" or "Completed"
- `config` (JSON) - Vehicle configuration
- `created_at` (DateTime)
- `updated_at` (DateTime)

#### **nodes**
- `id` (String, Primary Key)
- `project_id` (String, Foreign Key → projects.id)
- `parent_id` (String, Foreign Key → nodes.id, nullable)
- `name` (String)
- `display_id` (String)
- `level` (Integer)
- `own_cost` (Float)
- `weight` (Float)
- `quantity` (Integer)
- `material_calc_enabled` (Boolean)
- `material` (String)
- `config` (JSON)
- `status` (String)
- `total_cost` (Float)
- `total_weight` (Float)
- `co2_footprint` (Float)
- `created_at` (DateTime)
- `updated_at` (DateTime)

### Relationships

- **Project** → **Nodes** (One-to-Many, Cascade Delete)
- **Node** → **Children Nodes** (Self-referencing, Cascade Delete)

---

## 🔧 Database Management

### Access PostgreSQL in Docker

```bash
# Connect to PostgreSQL container
docker exec -it caresoft_postgres psql -U caresoft_user -d caresoft_db

# List tables
\dt

# View projects
SELECT * FROM projects;

# View nodes
SELECT * FROM nodes;

# Exit
\q
```

### Backup Database

```bash
docker exec caresoft_postgres pg_dump -U caresoft_user caresoft_db > backup.sql
```

### Restore Database

```bash
docker exec -i caresoft_postgres psql -U caresoft_user caresoft_db < backup.sql
```

---

## 🎯 Features

✅ **Persistent Storage** - All projects and data are saved to PostgreSQL  
✅ **Automatic Schema Creation** - Tables are created automatically on startup  
✅ **Cascade Deletion** - Deleting a project removes all associated nodes  
✅ **Hierarchical Data** - Tree structure with parent-child relationships  
✅ **Docker Integration** - Easy deployment with docker-compose  
✅ **Health Checks** - Database health monitoring in Docker  

---

## 📝 API Endpoints

All API endpoints now use the PostgreSQL database:

- `GET /api/tree` - Get current project tree
- `GET /api/projects` - List all projects
- `POST /api/project/new` - Create new project
- `POST /api/project/select` - Select active project
- `POST /api/project/complete` - Mark project as completed
- `POST /api/project/delete` - Delete project
- `POST /api/node/update` - Update node properties
- `POST /api/node/add` - Add new node
- `POST /api/node/delete` - Delete node

---

## 🐛 Troubleshooting

### Database Connection Issues

If you see connection errors:

1. **Check if PostgreSQL is running**:
   ```bash
   docker-compose ps
   ```

2. **Check database logs**:
   ```bash
   docker-compose logs db
   ```

3. **Restart services**:
   ```bash
   docker-compose restart
   ```

### Reset Database

```bash
# Stop and remove all containers and volumes
docker-compose down -v

# Start fresh
docker-compose up --build
```

---

## 🔐 Security Notes

⚠️ **Important**: Change the default database credentials in production!

Update the following in `docker-compose.yaml` and `.env`:
- `POSTGRES_PASSWORD`
- `DATABASE_URL`
- `SECRET_KEY`

---

## 📚 Technology Stack

- **Backend**: FastAPI (Python)
- **Database**: PostgreSQL 15
- **ORM**: SQLAlchemy
- **Containerization**: Docker & Docker Compose
- **Server**: Uvicorn (ASGI)

---

## 🎉 Success!

Your CareSoft application is now connected to PostgreSQL! All data will persist across restarts.
