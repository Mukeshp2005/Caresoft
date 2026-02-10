# CareSoft - Automotive Cost Estimation Platform

A comprehensive web-based application for automotive cost estimation and teardown analysis with PostgreSQL database integration.

![Status](https://img.shields.io/badge/status-production--ready-brightgreen)
![Docker](https://img.shields.io/badge/docker-required-blue)
![Python](https://img.shields.io/badge/python-3.9+-blue)
![PostgreSQL](https://img.shields.io/badge/postgresql-15-blue)

---

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Git
- Poetry (optional, for local development)

### Setup (3 commands!)

```bash
# 1. Clone the repository
git clone <your-repo-url>
cd Caresoft

# 2. Create environment file
cp .env.example .env

# 3. Start the application
docker compose up --build -d
```

### Access the Application

```
http://localhost:8000
```

**That's it!** 🎉 The database will be created automatically.

---

## ✨ Features

### ✅ Cost Tree Builder
- Hierarchical cost breakdown structure
- Multi-level component tracking (Vehicle → System → Subsystem → Component → Part)
- Real-time cost calculations
- Material-based cost indexing

### ✅ Database Integration
- **PostgreSQL** for persistent data storage
- Automatic schema creation
- CRUD operations (Create, Read, Update, Delete)
- Cascade deletion for data integrity
- Real-time synchronization

### ✅ Project Management
- Create multiple vehicle projects
- Track different configurations (EV, Petrol, Diesel, Hybrid)
- Project status management (Active/Completed)
- Historical data retention

### ✅ Interactive UI
- Modern glassmorphism design
- Drag-and-drop tree navigation
- Real-time updates
- Responsive layout
- Error handling with user-friendly messages

### ✅ Reporting & Analytics
- Material mix analysis
- Cost breakdown charts
- CO2 footprint calculation
- Export capabilities

---

## 📋 Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **SQLAlchemy** - ORM for database operations
- **PostgreSQL** - Production-grade database
- **Uvicorn** - ASGI server with auto-reload

### Frontend
- **HTML5** - Semantic markup
- **CSS3** - Modern styling with glassmorphism
- **JavaScript** - Interactive functionality
- **Bootstrap 4** - Responsive grid system
- **Chart.js** - Data visualization

### DevOps
- **Docker** - Containerization
- **Docker Compose** - Multi-container orchestration
- **Poetry** - Dependency Management
- **Git** - Version control

---

## 📁 Project Structure

```
Caresoft/
├── app/
│   ├── main.py           # FastAPI application & routes
│   ├── database.py       # Database connection & session
│   ├── models.py         # SQLAlchemy ORM models
│   └── crud.py           # Database CRUD operations
├── static/
│   ├── css/
│   │   └── styles.css    # Application styles
│   ├── js/
│   │   └── app.js        # Frontend JavaScript
│   └── img/              # Images and assets
├── templates/
│   └── index.html        # Main HTML template
├── docker-compose.yaml   # Docker services configuration
├── Dockerfile            # Web app container definition
├── pyproject.toml        # Poetry dependencies
├── poetry.lock           # Locked dependencies
├── .env.example          # Environment variables template
├── .gitignore           # Git ignore rules
└── README.md            # This file
```

---

## 🛠️ Common Commands

### Start Application
```bash
docker compose up -d
```

### Stop Application
```bash
docker compose down
```

### View Logs
```bash
docker compose logs -f
```

### Restart Services
```bash
docker compose restart
```

### Access Database
```bash
docker exec -it caresoft_postgres psql -U caresoft_user -d caresoft_db
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

## 📚 Documentation

- **[Team Setup Guide](TEAM_SETUP_GUIDE.md)** - Complete setup instructions for new team members
- **[Database Guide](README_DATABASE.md)** - Database schema and operations
- **[Quick Reference](QUICK_REFERENCE.md)** - Common tasks and commands
- **[All Features](ALL_FEATURES_FIXED.md)** - Complete feature list and testing

---

## 🔧 Configuration

### Environment Variables

Copy `.env.example` to `.env` and configure:

```env
# Database Configuration
DATABASE_URL=postgresql://caresoft_user:caresoft_password@db:5432/caresoft_db

# Application Settings
APP_ENV=development
SECRET_KEY=your-secret-key-change-in-production
```

### Docker Compose Services

- **db** - PostgreSQL 15 database (port 5432)
- **web** - FastAPI application (port 8000)

---

## 🧪 Testing

### Test All CRUD Operations
```bash
python3 test_crud_operations.py
```

### Test Database Integration
```bash
python3 test_db_integration.py
```

### Test Delete Functionality
```bash
python3 test_delete_node.py
```

### Manual Testing
1. Create a project
2. Add nodes to the tree
3. Edit node properties
4. Delete nodes
5. Verify data persists after restart

---

## 🔍 Troubleshooting

### Port Already in Use
```bash
# Change port in docker-compose.yaml
ports:
  - "8001:8000"  # Use 8001 instead of 8000
```

### Database Connection Failed
```bash
# Check container status
docker compose ps

# Restart database
docker compose restart db
```

### Changes Not Reflecting
```bash
# Clear browser cache
Ctrl + Shift + R  # Windows/Linux
Cmd + Shift + R   # Mac

# Or use incognito mode
```

### Start Fresh (⚠️ Deletes all data!)
```bash
docker compose down -v
docker compose up --build -d
```

---

## 🔐 Security

### Development
- Default credentials are safe for local development
- Database is only accessible on localhost

### Production
1. Change database credentials in `.env` and `docker-compose.yaml`
2. Update `SECRET_KEY` in `.env`
3. Use environment-specific configuration
4. Enable HTTPS
5. Implement authentication

---

## 📊 Database Schema

### Projects Table
- Stores vehicle project metadata
- Tracks project status and configuration
- Timestamps for audit trail

### Nodes Table
- Hierarchical cost breakdown structure
- Parent-child relationships
- Cascade deletion for data integrity
- Material and cost tracking

See [README_DATABASE.md](README_DATABASE.md) for detailed schema.

---

## 🎯 Features Overview

| Feature | Status | Description |
|---------|--------|-------------|
| Project Creation | ✅ | Create vehicle projects with configurations |
| Cost Tree Builder | ✅ | Hierarchical cost breakdown |
| Add Nodes | ✅ | Add child nodes to tree |
| Edit Nodes | ✅ | Update cost, weight, material |
| Delete Nodes | ✅ | Remove nodes with cascade |
| Database Sync | ✅ | Real-time PostgreSQL updates |
| Data Persistence | ✅ | All changes saved to database |
| Material Indexing | ✅ | Material-based cost calculation |
| CO2 Tracking | ✅ | Environmental impact analysis |
| Reporting | ✅ | Charts and data export |

---

## 🤝 Contributing

### Setup Development Environment

```bash
# Clone repository
git clone <your-repo-url>
cd Caresoft

# Create environment file
cp .env.example .env

# Start services
docker compose up --build -d

# View logs
docker compose logs -f
```

### Making Changes

1. Make your changes to the code
2. Test locally with `docker compose up --build -d`
3. Run tests: `python3 test_crud_operations.py`
4. Commit and push changes
5. Create pull request

### Code Style

- Python: Follow PEP 8
- JavaScript: Use ES6+ features
- HTML/CSS: Semantic markup, BEM naming

---

## 📝 License

[Add your license here]

---

## 👥 Team

[Add your team members here]

---

## 🆘 Support

### Getting Help

1. Check [TEAM_SETUP_GUIDE.md](TEAM_SETUP_GUIDE.md)
2. Review [Troubleshooting](#-troubleshooting) section
3. Check container logs: `docker compose logs -f`
4. Verify database: `docker exec -it caresoft_postgres psql -U caresoft_user -d caresoft_db`

### Common Issues

- **Port conflicts**: Change port in docker-compose.yaml
- **Database errors**: Check logs with `docker compose logs db`
- **UI not updating**: Clear browser cache (Ctrl+Shift+R)
- **Container won't start**: Run `docker compose down -v && docker compose up --build -d`

---

## 🎉 Success!

Your CareSoft application is now running with:

✅ FastAPI backend  
✅ PostgreSQL database  
✅ Interactive UI  
✅ Real-time updates  
✅ Data persistence  
✅ Production-ready architecture  

**Start building cost estimates!** 🚀

---

**Built with ❤️ using FastAPI, PostgreSQL, SQLAlchemy, and Docker**
