import requests
import json
import re
from datetime import datetime

# Fetch all public repos
response = requests.get('https://api.github.com/users/ShabaniMagawila/repos')
repos = response.json()

# Read current README
with open('README.md', 'r', encoding='utf-8') as f:
    readme = f.read()

# Find existing repo names in README (both personal and org)
existing_personal = re.findall(r'https://github.com/ShabaniMagawila/([^)]+)', readme)
existing_org = re.findall(r'https://github.com/OpenGeoCity-Tanzania/([^)]+)', readme)
existing = set(existing_personal + existing_org)

# Filter new repos: created in 2026 or later, have description, not archived, not in existing
current_year = datetime.now().year
new_repos = [
    repo for repo in repos
    if (repo['created_at'].startswith(str(current_year)) or repo['updated_at'].startswith(str(current_year)))  # Recent
    and repo['description']  # Has description
    and not repo['archived']  # Not archived
    and repo['name'] not in existing  # Not already in README
    and repo['name'] not in ['ShabaniMagawila', 'shabanimagawila.github.io']  # Skip profile and pages
]

if not new_repos:
    print("No new projects to add.")
    exit(0)

# Categorize new repos (simple heuristic)
web_apps = []
gis = []
tools = []
design = []

for repo in new_repos:
    name = repo['name']
    desc = repo['description'] or ""
    lang = repo['language'] or "Unknown"
    created = repo['created_at'][:10]  # YYYY-MM-DD

    # Simple categorization based on keywords
    if any(keyword in desc.lower() or keyword in name.lower() for keyword in ['web', 'app', 'platform', 'portal', 'website', 'dashboard']):
        web_apps.append((name, desc, lang, created))
    elif any(keyword in desc.lower() or keyword in name.lower() for keyword in ['gis', 'map', 'spatial', 'geospatial', 'osm']):
        gis.append((name, desc, lang, created))
    elif any(keyword in desc.lower() or keyword in name.lower() for keyword in ['tool', 'utility', 'converter', 'cleaning']):
        tools.append((name, desc, lang, created))
    elif any(keyword in desc.lower() or keyword in name.lower() for keyword in ['logo', 'design', 'branding']):
        design.append((name, desc, lang, created))
    else:
        tools.append((name, desc, lang, created))  # Default to tools

# Function to add to section
def add_to_section(readme, section_header, new_projects):
    if not new_projects:
        return readme

    # Find the section
    pattern = rf'(### {section_header}.*?)(---)'
    match = re.search(pattern, readme, re.DOTALL)
    if not match:
        return readme

    section_start = match.start(1)
    section_end = match.end(1)

    # Find the last project in the section
    last_project_pattern = r'#### \[\*\*.*?\]\(https://github\.com/.*?\)\n> .*?\n>\s*\*\*.*?\*\*'
    last_matches = list(re.finditer(last_project_pattern, readme[section_start:section_end], re.DOTALL))
    if not last_matches:
        return readme

    last_match = last_matches[-1]
    insert_pos = section_start + last_match.end()

    # Build new projects text
    new_text = ""
    for name, desc, lang, created in new_projects:
        new_text += f"\n#### [**{name.replace('-', ' ').title()}**](https://github.com/ShabaniMagawila/{name})\n> {desc}\n>\n> **Tech Stack:** {lang} | **Created:** {created}\n"

    # Insert
    return readme[:insert_pos] + new_text + readme[insert_pos:]

# Add to sections
readme = add_to_section(readme, "🌐 Web Applications & Platforms", web_apps)
readme = add_to_section(readme, "🗺️ GIS & Geospatial Solutions", gis)
readme = add_to_section(readme, "💻 Tools & Utilities", tools)
readme = add_to_section(readme, "🎨 Design & Branding", design)

# Write back
with open('README.md', 'w', encoding='utf-8') as f:
    f.write(readme)

print(f"Added {len(new_repos)} new projects to README.")