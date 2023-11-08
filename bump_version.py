import re
import subprocess
import sys

# Read current version
version_file_path = "paperpilot_common/version"
with open(version_file_path, "r", encoding="utf-8") as version_file:
    current_version = version_file.read().strip()

print(f"Current version: {current_version}")

current_version = current_version.split(".")

# Ask for version part to update
print("Select the new version: ")
print(f"1. {current_version[0]}.{current_version[1]}.{int(current_version[2]) + 1}")
print(f"2. {current_version[0]}.{int(current_version[1]) + 1}.0")
print(f"3. {int(current_version[0]) + 1}.0.0")


choice = input("Enter your choice: ")

# Update version
if choice == "1":
    version_parts = current_version
    version_parts[-1] = str(int(version_parts[-1]) + 1)
elif choice == "2":
    version_parts = current_version
    version_parts[-2] = str(int(version_parts[-2]) + 1)
    version_parts[-1] = "0"
elif choice == "3":
    version_parts = current_version
    version_parts[-3] = str(int(version_parts[-3]) + 1)
    version_parts[-2] = "0"
    version_parts[-1] = "0"
else:
    print("Invalid choice")
    sys.exit(1)

new_version = ".".join(version_parts)
print(f"New version: {new_version}")

# Update the protobuf version file
with open(version_file_path, "w", encoding="utf-8") as version_file:
    version_file.writelines([new_version])

# Update pyproject.toml version
pyproject_toml_path = "paperpilot-common-python/pyproject.toml"
with open(pyproject_toml_path, "r", encoding="utf-8") as toml_file:
    toml_content = toml_file.read()

toml_content = re.sub(
    r'version = "\d+\.\d+\.\d+"', f'version = "{new_version}"', toml_content
)

with open(pyproject_toml_path, "w", encoding="utf-8") as toml_file:
    toml_file.write(toml_content)

# Update python __init__.py version
init_py_path = "paperpilot-common-python/paperpilot_common/__init__.py"
with open(init_py_path, "r", encoding="utf-8") as init_py_file:
    init_py_content = init_py_file.read()

init_py_content = re.sub(
    r'__version__ = "\d+\.\d+\.\d+"', f'__version__ = "{new_version}"', init_py_content
)

with open(init_py_path, "w", encoding="utf-8") as init_py_file:
    init_py_file.write(init_py_content)

# Create commit and tag
commit_message = f"feat: bump version to v{new_version}"
subprocess.run(["git", "add", version_file_path, pyproject_toml_path, init_py_path])
return_code = subprocess.run(["git", "commit", "-m", commit_message]).returncode
if return_code != 0:  # try again due to commit hook
    subprocess.run(["git", "add", version_file_path, pyproject_toml_path, init_py_path])
    subprocess.run(["git", "commit", "-m", commit_message])
subprocess.run(["git", "tag", f"v{new_version}"])

# Update CHANGELOG.md
with open("CHANGELOG.md", "r", encoding="utf-8") as changelog_file:
    changelog_content = changelog_file.read()

subprocess.run(["conventional-changelog", "-p", "angular", "-i", "CHANGELOG.md", "-s"])

with open("CHANGELOG.md", "r", encoding="utf-8") as changelog_file:
    new_changelog_content = changelog_file.read()

subprocess.run(["git", "add", "CHANGELOG.md"])
return_code = subprocess.run(
    ["git", "commit", "-m", f"docs: update CHANGELOG.md for version {new_version}"]
).returncode

if return_code != 0:  # try again due to commit hook
    subprocess.run(["git", "add", "CHANGELOG.md"])
    subprocess.run(
        ["git", "commit", "-m", f"docs: update CHANGELOG.md for version {new_version}"]
    )

update_changelog = new_changelog_content.replace(changelog_content, "")

# # Push commit and tag
# subprocess.run(["git", "push"])
# subprocess.run(["git", "push", "--tags"])
#
#
# # Create Github release
# subprocess.run(
#     [
#         "gh",
#         "release",
#         "create",
#         f"v{new_version}",
#         "--title",
#         f"v{new_version}",
#         "--notes",
#         update_changelog,
#     ]
# )


print(f"Successfully bumped version to {new_version}")
