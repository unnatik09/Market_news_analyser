"""
Setup script for Stock Market News Summarizer
Run this script to set up the application environment
"""

import os
import subprocess
import sys
import shutil
from pathlib import Path

def run_command(command, description):
    """Run a shell command with description"""
    print(f"📦 {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"❌ Error: {result.stderr}")
            return False
        print(f"✅ {description} completed successfully")
        return True
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8 or higher is required")
        return False
    print(f"✅ Python {version.major}.{version.minor} detected")
    return True

def setup_virtual_environment():
    """Set up virtual environment"""
    venv_path = Path("venv")
    
    if venv_path.exists():
        print("📁 Virtual environment already exists")
        return True
    
    return run_command(f"{sys.executable} -m venv venv", "Creating virtual environment")

def install_dependencies():
    """Install required dependencies"""
    # Determine the correct pip path based on OS
    if os.name == 'nt':  # Windows
        pip_path = "venv\\Scripts\\pip"
    else:  # macOS/Linux
        pip_path = "venv/bin/pip"
    
    return run_command(f"{pip_path} install -r requirements.txt", "Installing dependencies")

def create_env_file():
    """Create .env file from example"""
    env_path = Path(".env")
    env_example_path = Path(".env.example")
    
    if env_path.exists():
        print("📝 .env file already exists")
        return True
    
    if env_example_path.exists():
        shutil.copy(env_example_path, env_path)
        print("✅ Created .env file from example")
        return True
    else:
        # Create a basic .env file
        with open(".env", "w") as f:
            f.write("GROQ_API_KEY=your_groq_api_key_here\n")
        print("✅ Created basic .env file")
        return True

def print_next_steps():
    """Print next steps for the user"""
    print("\n🎉 Setup completed successfully!")
    print("\n🔑 Next steps:")
    print("1. Get your Groq API key from https://console.groq.com/")
    print("2. Edit the .env file and replace 'your_groq_api_key_here' with your actual API key")
    
    if os.name == 'nt':  # Windows
        print("3. Activate virtual environment: venv\\Scripts\\activate")
    else:  # macOS/Linux
        print("3. Activate virtual environment: source venv/bin/activate")
    
    print("4. Run the application: streamlit run app.py")
    print("\n📚 Additional notes:")
    print("- The app will scrape Economic Times market section")
    print("- AI summaries require a valid Groq API key")
    print("- The app runs on http://localhost:8501 by default")

def main():
    """Main setup function"""
    print("🚀 Stock Market News Summarizer - Setup")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Set up virtual environment
    if not setup_virtual_environment():
        print("❌ Failed to set up virtual environment")
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        print("❌ Failed to install dependencies")
        sys.exit(1)
    
    # Create .env file
    if not create_env_file():
        print("❌ Failed to create .env file")
        sys.exit(1)
    
    # Print next steps
    print_next_steps()

if __name__ == "__main__":
    main()