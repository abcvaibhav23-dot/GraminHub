.PHONY: clean clean-all clean-dry clean-generated db-reset db-seed-demo demo-ready db-backup e2e sanity count-files

MAX_FILES ?= 75

# Remove only generated caches/runtime artifacts. Keeps source, venv, and Docker data.
clean:
	@echo "Cleaning runtime artifacts..."
	@find backend -type d \( -name "__pycache__" -o -name ".pytest_cache" -o -name ".mypy_cache" \) -prune -exec rm -rf {} +
	@find backend -type f \( -name "*.pyc" -o -name "*.tmp" -o -name "*.temp" \) -delete
	@find backend/logs -type f ! -name ".gitkeep" -delete 2>/dev/null || true
	@echo "Done."

# Preview what clean would remove.
clean-dry:
	@echo "Dry-run: items that would be removed by clean"
	@find backend -type d \( -name "__pycache__" -o -name ".pytest_cache" -o -name ".mypy_cache" \) -print
	@find backend -type f \( -name "*.pyc" -o -name "*.tmp" -o -name "*.temp" \) -print
	@find backend/logs -type f ! -name ".gitkeep" -print 2>/dev/null || true

# Deeper cleanup, still non-destructive for source code.
clean-all: clean
	@echo "Cleaning extra local artifacts..."
	@rm -rf backend/.coverage backend/htmlcov
	@echo "Done."

# Remove generated local-only artifacts that should never be committed.
clean-generated: clean-all
	@echo "Cleaning generated local environments and backups..."
	@rm -rf backend/venv backend/.pytest_cache
	@rm -f backend/.env
	@find backups -type f ! -name ".gitkeep" -delete 2>/dev/null || true
	@echo "Done."

# Reset PostgreSQL app data (keeps DB/service), then re-seed default categories.
db-reset:
	@echo "Resetting PostgreSQL data..."
	@docker compose exec -T db psql -U marketplace -d marketplace -c "\
TRUNCATE TABLE call_logs, reviews, bookings, supplier_services, suppliers, users, categories RESTART IDENTITY CASCADE;\
INSERT INTO categories (name) VALUES ('Construction Materials'), ('Heavy Vehicles'), ('Transport Vehicles'), ('Equipment Rentals');"
	@echo "DB reset completed."

# Seed demo supplier/user/admin and sample business data.
db-seed-demo:
	@echo "Seeding demo data..."
	@docker compose exec -T db psql -U marketplace -d marketplace < scripts/seed_demo.sql
	@echo "Demo seed completed."

# Reset data and immediately seed demo accounts/data (recommended for demos).
demo-ready: db-reset db-seed-demo
	@echo "Demo data is ready."

# Export starter SQL backup using pg_dump.
db-backup:
	@mkdir -p backups
	@ts=$$(date +%Y%m%d_%H%M%S); \
	echo "Creating backup backups/starter_backup_$${ts}.sql ..."; \
	docker compose exec -T db pg_dump -U marketplace -d marketplace > backups/starter_backup_$${ts}.sql; \
	echo "Backup created: backups/starter_backup_$${ts}.sql"

# Run live end-to-end API scenario against running backend.
e2e:
	@./scripts/e2e.sh

# Count files that should matter for review/merge size.
count-files:
	@count=$$(git ls-files | wc -l | tr -d ' '); \
	echo "Tracked file count: $$count"; \
	if [ "$$count" -gt "$(MAX_FILES)" ]; then \
		echo "File count exceeds MAX_FILES=$(MAX_FILES)"; \
		exit 1; \
	fi

# Lightweight sanity checks before commit/merge.
sanity:
	@echo "Running compile sanity..."
	@PYTHONPYCACHEPREFIX=/tmp/pycache python3 -m compileall backend/app >/dev/null
	@echo "Compile sanity passed."
	@if [ -x backend/venv/bin/pytest ]; then \
		echo "Running pytest..."; \
		cd backend && ./venv/bin/pytest app/tests -q; \
	else \
		echo "Skipping pytest (backend/venv/bin/pytest not found)."; \
	fi
	@if curl -fsS http://localhost:8000/health >/dev/null 2>&1; then \
		echo "Backend health check OK. Running E2E..."; \
		./scripts/e2e.sh; \
	else \
		echo "Skipping E2E (backend not running on http://localhost:8000)."; \
	fi
	@$(MAKE) count-files
