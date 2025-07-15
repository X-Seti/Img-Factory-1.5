echo "🧹 Cleaning Python cache files..."
find . -type d -name "__pycache__" -exec rm -rf {} +
echo "✅ Done!"
