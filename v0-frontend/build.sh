#!/bin/bash

# Build script for Render deployment
echo "🔧 Starting v0 frontend build..."

# Install dependencies
echo "📦 Installing dependencies..."
npm ci --production=false

# Build the application
echo "🏗️ Building Next.js application..."
npm run build

echo "✅ Build completed successfully!"