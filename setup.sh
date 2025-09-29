#!/bin/bash

echo "🚀 Setting up Stock Market News Summarizer..."

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install requirements
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cp .env.example .env
    echo "⚠️  Please edit .env file and add your Groq API key!"
fi

echo "✅ Setup complete!"
echo ""
echo "🔑 Next steps:"
echo "1. Get your Groq API key from https://console.groq.com/"
echo "2. Edit the .env file and add your API key"
echo "3. Run: source venv/bin/activate"
echo "4. Run: streamlit run app.py"
echo ""
echo "🎉 Enjoy your stock market news summarizer!"