import requests
import re

USERNAME = "Omkar-109"  
API_URL = f"https://api.github.com/users/{USERNAME}/repos?per_page=100"

def get_readme_heading(repo_name):
    for branch in ["main", "master"]:
        url = f"https://raw.githubusercontent.com/{USERNAME}/{repo_name}/{branch}/README.md"
        response = requests.get(url)
        if response.status_code == 200:
            match = re.search(r'^# (.+)', response.text, re.MULTILINE)
            return match.group(1).strip() if match else repo_name
    return repo_name

def get_live_projects():
    repos = requests.get(API_URL).json()
    projects = []

    for repo in repos:
        if repo['fork'] or repo['private']:
            continue

        homepage = repo.get("homepage")
        if homepage and homepage.startswith("http"):
            heading = get_readme_heading(repo["name"])
            projects.append({
                "name": heading,
                "description": repo.get("description", "No description"),
                "repo_url": repo["html_url"],
                "live": homepage
            })
    return projects

def build_markdown_table(projects):
    table = "| Project Name | Description | 🌐 Live Link |\n"
    table += "|--------------|-------------|---------------|\n"
    for p in projects:
        project_link = f"[{p['name']}]({p['repo_url']})"
        live_link = f"[Visit]({p['live']})"
        table += f"| {project_link} | {p['description']} | {live_link} |\n"
    return table

def update_readme(table):
    with open("README.md", "r", encoding="utf-8") as f:
        content = f.read()

    start = "<!--LIVE_PROJECTS_START-->"
    end = "<!--LIVE_PROJECTS_END-->"
    if start not in content or end not in content:
        raise ValueError("README must contain <!--LIVE_PROJECTS_START--> and <!--LIVE_PROJECTS_END--> markers")

    updated_section = f"{start}\n{table}\n{end}"
    new_content = content.split(start)[0] + updated_section + content.split(end)[1]

    with open("README.md", "w", encoding="utf-8") as f:
        f.write(new_content)

if __name__ == "__main__":
    projects = get_live_projects()
    table = build_markdown_table(projects)
    update_readme(table)
