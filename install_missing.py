import pkg_resources
import subprocess

# Read the requirements.txt content
with open("requirements.txt", "r") as file:
    requirements = file.readlines()

# Parse requirements to get package names (including those with exact versions)
required_packages = [
    pkg.strip()
    for pkg in requirements
    if pkg.strip() and not pkg.strip().startswith("#")
]

# Get the set of installed package keys
installed_packages = {pkg.key for pkg in pkg_resources.working_set}

# Identify missing packages by name (ignoring versions)
missing_packages = []
for req in required_packages:
    pkg_name = req.split("==")[0].lower() if "==" in req else req.split(">=")[0].lower()
    if pkg_name not in installed_packages:
        missing_packages.append(req)

# Install only missing packages
if missing_packages:
    subprocess.check_call(["pip", "install"] + missing_packages)
else:
    print("All required packages are already installed.")
