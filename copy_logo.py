import shutil
import os

source_path = r"C:\Users\Admin\.gemini\antigravity\brain\07d7a5fe-1c2e-4b6e-a27f-b62ec8ed55a6\diagno_amicus_stylish_logo_1777734013192.png"
dest_path = os.path.join(os.path.dirname(__file__), "components", "logo.png")

try:
    shutil.copyfile(source_path, dest_path)
    print(f"Successfully copied the new stylish logo to: {dest_path}")
    print("You can now safely delete this script.")
except Exception as e:
    print(f"Failed to copy logo: {e}")
