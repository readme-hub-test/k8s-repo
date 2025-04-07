#!/bin/bash
set -e

# Check if organization name is provided
if [ -z "$1" ]; then
  echo "Usage: $0 <organization-name>"
  exit 1
fi

ORGANIZATION="$1"
REPOS_URL="https://api.github.com/orgs/$ORGANIZATION/repos?per_page=100"
REPOS=$(curl -s "$REPOS_URL" | jq -r '.[].name')

# Define additional markdown files to include (path within repo)
ADDITIONAL_FILES=("additional-documentation.md")

# Create docs directory
mkdir -p docs/readmes

# Start creating index.md
echo "# Organization Repositories" > docs/index.md
echo "Here are the README files from all the repositories in the organization:" >> docs/index.md
echo "" >> docs/index.md

README_NAV="  - Organization Repositories:\n    - Home: index.md\n"
ADDITIONAL_FILES_NAV="  - Additional Markdown Files:\n"

README_LINKS=""
ADDITIONAL_FILES_SECTION="\n## Additional Markdown Files\nAdditional documentation files:\n"

# Loop through repositories
for REPO in $REPOS; do
  REPO_FILE="docs/$REPO.md"

  # Fetch README
  README_URL="https://raw.githubusercontent.com/$ORGANIZATION/$REPO/main/README.md"
  echo "# $REPO" > "$REPO_FILE"
  curl -s "$README_URL" >> "$REPO_FILE"

  # Add to navigation and index
  README_NAV+="    - $REPO: $REPO.md\n"
  README_LINKS+="- [$REPO](/$REPO.md)\n"

  # Loop through additional markdown files
  for FILE in "${ADDITIONAL_FILES[@]}"; do
    FILE_NAME=$(basename "$FILE")
    DEST_FILE="docs/${REPO}_${FILE_NAME}"

    FILE_URL="https://raw.githubusercontent.com/$ORGANIZATION/$REPO/main/$FILE"
    HTTP_STATUS=$(curl -o /dev/null --silent --head --write-out '%{http_code}\n' "$FILE_URL")

    if [ "$HTTP_STATUS" -eq 200 ]; then
      echo "# $REPO - $FILE_NAME" > "$DEST_FILE"
      curl -s "$FILE_URL" >> "$DEST_FILE"
      ADDITIONAL_FILES_SECTION+="- [$REPO - $FILE_NAME](/${REPO}_${FILE_NAME})\n"
      ADDITIONAL_FILES_NAV+="    - $REPO - $FILE_NAME: ${REPO}_${FILE_NAME}\n"
    fi
  done
done

# Append sections to index.md
echo -e "$README_LINKS" >> docs/index.md
echo -e "$ADDITIONAL_FILES_SECTION" >> docs/index.md

# Generate mkdocs.yml dynamically
echo "site_name: Organization Documentation" > mkdocs.yml
echo "theme:" >> mkdocs.yml
echo "  name: readthedocs" >> mkdocs.yml
echo "nav:" >> mkdocs.yml
echo -e "$README_NAV" >> mkdocs.yml
echo -e "$ADDITIONAL_FILES_NAV" >> mkdocs.yml
