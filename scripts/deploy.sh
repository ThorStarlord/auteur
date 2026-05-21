#!/bin/bash
# Deployment automation script for Sensemaking Skills

set -e

echo "=== Sensemaking Skills Deployment ==="
echo "Target: Production"
echo "Date: $(date)"

# Verify prerequisites
echo "Checking prerequisites..."
which python > /dev/null || { echo "Python not found"; exit 1; }
which git > /dev/null || { echo "Git not found"; exit 1; }

# Install/update dependencies
echo "Installing dependencies..."
python -m pip install -q -r requirements.txt

# Run validation tests
echo "Running validation tests..."
python -m pytest tests/ -q --tb=short

# Verify installation
echo "Verifying installation..."
python scripts/orchestration-runner.py --list-workflows > /dev/null

# Run preflight check
echo "Running preflight check..."
python scripts/validate-repo.py --repo-root .

echo "=== Deployment Complete ==="
echo "System is ready for production use."
exit 0
