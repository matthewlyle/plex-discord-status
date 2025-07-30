#!/usr/bin/env python3
"""
Build script for creating distributable packages
"""

import os
import shutil
import subprocess
import sys
import platform

def run_command(cmd):
    """Run a command and return success status"""
    try:
        subprocess.run(cmd, shell=True, check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {cmd}")
        print(f"Error: {e}")
        return False

def build_executable():
    """Build the executable using PyInstaller"""
    print("Building executable...")
    
    # Clean previous builds
    if os.path.exists("dist"):
        shutil.rmtree("dist")
    if os.path.exists("build"):
        shutil.rmtree("build")
    
    # Build command
    cmd = f"{sys.executable} -m PyInstaller --onefile --name=PlexDiscordStatus plex_discord_status.py"
    
    if not run_command(cmd):
        print("Failed to build executable")
        return False
    
    print("Executable built successfully!")
    return True

def create_distribution_package():
    """Create a distribution package with all necessary files"""
    print("Creating distribution package...")
    
    # Copy files to dist directory
    files_to_copy = [
        "README.md"
    ]
    
    for file in files_to_copy:
        if os.path.exists(file):
            shutil.copy2(file, "dist/")
            print(f"Copied {file} to dist/")
        else:
            print(f"Warning: {file} not found")
    
    # Copy config.ini for distribution
    if os.path.exists("config.ini"):
        shutil.copy2("config.ini", "dist/config.ini")
        print("Copied config.ini to dist/config.ini")
    else:
        print("Warning: config.ini not found")
    
    print("Distribution package created successfully!")
    return True

def create_zip_package():
    """Create a zip file for easy distribution"""
    import zipfile
    
    system = platform.system()
    arch = platform.machine()
    
    zip_name = f"PlexDiscordStatus-{system}-{arch}.zip"
    
    print(f"Creating zip package: {zip_name}")
    
    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk("dist"):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, "dist")
                zipf.write(file_path, arcname)
    
    print(f"Zip package created: {zip_name}")
    return zip_name

def main():
    """Main build process"""
    print("=== Plex Discord Status Build Script ===")
    
    # Check if PyInstaller is available
    try:
        import PyInstaller
        print(f"PyInstaller version: {PyInstaller.__version__}")
    except ImportError:
        print("PyInstaller not found. Installing...")
        if not run_command(f"{sys.executable} -m pip install pyinstaller"):
            print("Failed to install PyInstaller")
            return
    
    # Build the executable
    if not build_executable():
        return
    
    # Create distribution package
    if not create_distribution_package():
        return
    
    # Create zip package
    zip_name = create_zip_package()
    
    print("\n=== Build Complete ===")
    print(f"Executable: dist/PlexDiscordStatus")
    print(f"Distribution package: {zip_name}")
    print("\nYou can now distribute the zip file to others!")

if __name__ == "__main__":
    main() 