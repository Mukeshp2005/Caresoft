# 📦 Poetry Migration Guide

## Overview

We have migrated the project dependency management from `pip/requirements.txt` to **Poetry**.

Benefits:
- ✅ **Reproducible Builds**: `poetry.lock` ensures all developers use exact same versions.
- ✅ **Simplified Management**: Add/remove packages easily.
- ✅ **Dependency Resolution**: Better conflict handling.
- ✅ **Project Metadata**: Centralized in `pyproject.toml`.

---

## 🛠️ Updated Files

1. **Dockerfile**: Updated to install Poetry and use `pyproject.toml`.
2. **docker-compose.yaml**: Verified (uses auto-detected environment).
3. **pyproject.toml**: New configuration file defining dependencies.
4. **Docs**: Updated all documentation (README, setup guides, checklists).
5. **requirements.txt**: REMOVED (no longer needed).

---

## 🚀 One-Time Setup Step

Since `poetry.lock` is new, you need to generate it inside the container and bring it to your host machine so you can commit it.

**Run this command to generate the lock file:**

```bash
docker compose run --rm web poetry lock
```

This will:
1. Start a temporary container.
2. Resolve all dependencies.
3. Generate `poetry.lock` in your project directory (thanks to volume mounts).

---

## 📝 Committing Changes

After generating the lock file, run:

```bash
git add pyproject.toml poetry.lock Dockerfile docker-compose.yaml
git add README.md TEAM_SETUP_GUIDE.md PRE_PUSH_CHECKLIST.md READY_FOR_TEAM.md
git rm requirements.txt
git commit -m "chore: Migrate to Poetry for dependency management"
```

---

## 🔧 Managing Dependencies

### Add a Package

To add a new package (e.g., requests):

```bash
docker compose run --rm web poetry add requests
```

### Remove a Package

```bash
docker compose run --rm web poetry remove requests
```

### Update All Packages

```bash
docker compose run --rm web poetry update
```

---

## 🕵️ Troubleshooting

### Build Fails?

If `docker compose build` takes too long or fails:

1. **Check Network**: Poetry installation requires internet.
2. **Clear Cache**: `docker builder prune`
3. **Retry**: `docker compose build --no-cache`

### Lock File Issues?

If you see integrity errors:
- Delete `poetry.lock`
- Run `docker compose run --rm web poetry lock` again.

---

**You're all set with a modern dependency management system!** 🚀
