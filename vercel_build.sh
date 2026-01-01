cat > vercel_build.sh << 'EOF'
#!/bin/bash
set -e

echo "Installing dependencies..."
pip install -r requirements.txt

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Running migrations..."
python manage.py migrate
EOF

chmod +x vercel_build.sh