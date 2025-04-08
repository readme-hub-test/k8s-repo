#!/usr/bin/env python3
import os
import sys
import requests
import yaml

ORG = sys.argv[1] if len(sys.argv) > 1 else None
if not ORG:
    print("Usage: fetch_docs.py <organization-name>")
    sys.exit(1)

# Load additional documentation mapping
DOC_MAP_PATH = sys.argv[2] if len(sys.argv) > 2 else "doc_map.yaml"
if os.path.exists(DOC_MAP_PATH):
    with open(DOC_MAP_PATH, "r") as f:
        doc_map = yaml.safe_load(f)
    additional_docs = doc_map.get("additional_docs", {})
else:
    additional_docs = {}

# Prepare folders
os.makedirs("docs/readmes", exist_ok=True)

# Start building index.md
index_path = "docs/index.md"
with open(index_path, "w") as index_file:
    index_file.write("# my test Repositories\n")
    index_file.write(f"Here are the README files from all the repositories in the {ORG} organization:\n\n")

README_NAV = ["  - my test Repositories:", "    - Home: index.md"]
ADDITIONAL_FILES_NAV = ["  - Additional Documentation Files:"]
README_LINKS = []
ADDITIONAL_FILES_SECTION = ["\n## Additional Documentation\nAdditional documentation files:\n"]

# Fetch repos
repos_url = f"https://api.github.com/orgs/{ORG}/repos?per_page=100"
repos = requests.get(repos_url).json()

for repo in repos:
    name = repo["name"]
    readme_url = f"https://raw.githubusercontent.com/{ORG}/{name}/main/README.md"
    repo_md_path = f"docs/{name}.md"

    response = requests.get(readme_url)
    with open(repo_md_path, "w") as f:
        f.write(f"# {name}\n\n")
        if response.status_code == 200:
            f.write(response.text)
        else:
            f.write("*README.md not found.*")

    README_NAV.append(f"    - {name}: {name}.md")
    README_LINKS.append(f"- [{name}]({name}.md)")

    # Fetch additional files if defined
    extra_files = additional_docs.get(name, [])
    for file_path in extra_files:
        file_url = f"https://raw.githubusercontent.com/{ORG}/{name}/main/{file_path}"
        file_response = requests.get(file_url)

        if file_response.status_code == 200:
            dest_name = f"{name}_{os.path.basename(file_path)}"
            dest_path = f"docs/{dest_name}"
            with open(dest_path, "w") as extra_file:
                extra_file.write(f"# {name} - {file_path}\n\n")
                extra_file.write(file_response.text)

            ADDITIONAL_FILES_SECTION.append(f"- [{name} - {file_path}]({dest_name})")
            ADDITIONAL_FILES_NAV.append(f"    - {name} - {file_path}: {dest_name}")

# Finalize index.md
with open(index_path, "a") as index_file:
    index_file.write("\n".join(README_LINKS) + "\n")
    index_file.write("\n".join(ADDITIONAL_FILES_SECTION) + "\n")

# Generate mkdocs.yml
with open("mkdocs.yml", "w") as mkdocs:
    mkdocs.write("site_name: my Documentation\n")
    mkdocs.write("theme:\n  name: readthedocs\n")
    mkdocs.write("nav:\n")

    if len(README_NAV) > 1:  # has entries besides the header
        mkdocs.write("\n".join(README_NAV) + "\n")
    else:
        mkdocs.write("  - Home: index.md\n")

    if len(ADDITIONAL_FILES_NAV) > 1:
        mkdocs.write("\n".join(ADDITIONAL_FILES_NAV) + "\n")

