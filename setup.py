import subprocess
import sys
import os
from pathlib import Path

def run_command(command, description):
    """Run shell command with error handling"""
    print(f"[INFO] {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"[SUCCESS] {description} completed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] {description} failed")
        print(f"Command: {command}")
        print(f"Error: {e.stderr}")
        return False

def main():
    """Quick setup for Windows"""
    print("AI Meeting Summarizer - Quick Setup")
    print("=" * 40)
    
    # Check Python version
    if sys.version_info < (3, 8):
        print(f"[ERROR] Python 3.8+ required. Current: {sys.version}")
        return False
    
    print(f"[SUCCESS] Python {sys.version.split()[0]} detected")
    
    # Create directories
    print("[INFO] Creating project structure...")
    directories = ["sample_transcripts", "exports", ".vscode"]
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"   Created: {directory}/")
    
    # Create requirements.txt
    requirements = """streamlit==1.28.1
transformers==4.35.2
torch==2.1.0
nltk==3.8.1
spacy==3.7.2
pandas==2.1.3
numpy==1.25.2
scikit-learn==1.3.2"""
    
    with open("requirements.txt", "w", encoding="utf-8") as f:
        f.write(requirements)
    print("[SUCCESS] Created requirements.txt")
    
    # Create sample files
    samples = {
        "sales_meeting.txt": """John: Good morning everyone. Let's start with the Q4 sales review.
Sarah: Our revenue is up 15% compared to last quarter. The new product launch was successful.
Mike: I need to follow up with three key clients by Friday. The enterprise deals are progressing well.
Sarah: We should prepare the quarterly report by next Tuesday. 
John: Great. Mike, please schedule client calls this week. Sarah will handle the report.
Lisa: The marketing campaign needs approval by tomorrow for the holiday push.
John: Lisa, get that approved ASAP. Next meeting is scheduled for next Monday at 10 AM.""",
        
        "project_meeting.txt": """Alex: Let's discuss the new website redesign project timeline.
Emma: The design mockups are ready for review. We need client feedback by Wednesday.
Tom: I'll handle the backend development. Estimated completion is two weeks.
Emma: The user testing phase should start next Friday. Tom, can you have the staging environment ready?
Alex: Emma will coordinate with the client. Tom is responsible for development milestones.
Sam: We need to update the project documentation and notify stakeholders about the timeline.
Alex: Sam, please send updates to stakeholders by end of day. Critical that we meet the December deadline.""",
        
        "budget_meeting.txt": """Director: Our department budget for next year needs careful planning.
Manager1: The software licenses are increasing by 20%. We need to allocate more budget there.
Manager2: I recommend reducing travel expenses and focusing on virtual meetings.
Director: Good point. Manager1 will research alternative software solutions by next week.
Manager2: I'll prepare a cost analysis comparing virtual vs in-person events.
Director: Both reports are due before the board meeting on Friday. This is high priority.
Manager1: Should we also review the vendor contracts?
Director: Yes, Manager2 please audit all vendor agreements within the next two weeks."""
    }
    
    for filename, content in samples.items():
        with open(f"sample_transcripts/{filename}", "w", encoding="utf-8") as f:
            f.write(content)
    print(f"[SUCCESS] Created {len(samples)} sample files")
    
    # Create VS Code launch configuration
    launch_config = """{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Run Streamlit App",
            "type": "python",
            "request": "launch",
            "module": "streamlit",
            "args": ["run", "app.py"],
            "console": "integratedTerminal",
            "cwd": "${workspaceFolder}"
        }
    ]
}"""
    
    with open(".vscode/launch.json", "w", encoding="utf-8") as f:
        f.write(launch_config)
    print("[SUCCESS] Created VS Code configuration")
    
    # Create virtual environment
    print("[INFO] Creating virtual environment...")
    if not run_command("python -m venv meeting_env", "Creating virtual environment"):
        print("[WARNING] Virtual environment creation failed, continuing with global Python")
        pip_command = "pip"
        python_command = "python"
    else:
        # Set up environment-specific commands
        if os.name == 'nt':  # Windows
            pip_command = "meeting_env\\Scripts\\pip"
            python_command = "meeting_env\\Scripts\\python"
        else:
            pip_command = "meeting_env/bin/pip"
            python_command = "meeting_env/bin/python"
    
    # Install packages
    print("[INFO] Installing required packages...")
    install_commands = [
        f"{pip_command} install --upgrade pip",
        f"{pip_command} install streamlit",
        f"{pip_command} install transformers torch",
        f"{pip_command} install nltk spacy",
        f"{pip_command} install pandas numpy scikit-learn"
    ]
    
    for cmd in install_commands:
        if not run_command(cmd, f"Running: {cmd.split()[-1]}"):
            print(f"[WARNING] Failed to install {cmd.split()[-1]}")
    
    # Download models
    print("[INFO] Downloading AI models...")
    model_commands = [
        f'{python_command} -m spacy download en_core_web_sm',
        f'{python_command} -c "import nltk; nltk.download(\'punkt\')"'
    ]
    
    for cmd in model_commands:
        if not run_command(cmd, "Downloading model"):
            print("[WARNING] Model download failed - you may need to download manually")
    
    # Final instructions
    print("\n" + "=" * 50)
    print("SETUP COMPLETED!")
    print("=" * 50)
    print("\nNext steps:")
    print("1. Make sure you have the app.py file in this directory")
    print("2. Activate virtual environment:")
    if os.name == 'nt':
        print("   meeting_env\\Scripts\\activate")
    else:
        print("   source meeting_env/bin/activate")
    print("3. Run the application:")
    print("   streamlit run app.py")
    print("4. Open browser: http://localhost:8501")
    
    print("\nIf you encounter issues:")
    print("- Make sure app.py is in the current directory")
    print("- Try: pip install --upgrade streamlit transformers")
    print("- For model issues: python -m spacy download en_core_web_sm")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        if success:
            input("\nPress Enter to continue...")
    except Exception as e:
        print(f"[ERROR] Setup failed: {e}")
        input("Press Enter to exit...")
        sys.exit(1)