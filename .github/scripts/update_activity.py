import urllib.request
import json
import os
import re

USERNAME = "Sanath-Reddy"
MAX_LINES = 10

url = f"https://api.github.com/users/{USERNAME}/events/public"
headers = {'User-Agent': 'Mozilla/5.0'}
token = os.environ.get("GITHUB_TOKEN")
if token:
    headers['Authorization'] = f"token {token}"
req = urllib.request.Request(url, headers=headers)
try:
    with urllib.request.urlopen(req) as response:
        events = json.loads(response.read().decode())
except Exception as e:
    print(f"Error fetching events: {e}")
    exit(1)

activity_lines = []
for event in events:
    if len(activity_lines) >= MAX_LINES:
        break
    
    repo_name = event['repo']['name']
    if repo_name == "Sanath-Reddy/Sanath-Reddy":
        continue
        
    repo_url = f"https://github.com/{repo_name}"
    repo_link = f"<a href=\"{repo_url}\">{repo_name}</a>"
    
    if event['type'] == 'PushEvent':
        commits = event['payload'].get('size')
        if commits is None:
            c_list = event['payload'].get('commits')
            commits = len(c_list) if c_list is not None else 1
        activity_lines.append(f"📝 Pushed {commits} commit(s) to {repo_link}")
    elif event['type'] == 'CreateEvent':
        ref_type = event['payload']['ref_type']
        if ref_type in ['branch', 'tag']:
            ref = event['payload']['ref']
            activity_lines.append(f"🚀 Created {ref_type} <code>{ref}</code> in {repo_link}")
        else:
            activity_lines.append(f"🚀 Created {ref_type} in {repo_link}")
    elif event['type'] == 'IssuesEvent' and event['payload']['action'] == 'opened':
        issue_num = event['payload']['issue']['number']
        issue_url = event['payload']['issue']['html_url']
        activity_lines.append(f"❗️ Opened issue <a href=\"{issue_url}\">#{issue_num}</a> in {repo_link}")
    elif event['type'] == 'PullRequestEvent' and event['payload']['action'] == 'opened':
        pr_num = event['payload']['pull_request']['number']
        pr_url = event['payload']['pull_request']['html_url']
        activity_lines.append(f"💪 Opened PR <a href=\"{pr_url}\">#{pr_num}</a> in {repo_link}")
    elif event['type'] == 'ReleaseEvent':
        action = event['payload']['action']
        release_name = event['payload']['release']['name']
        release_url = event['payload']['release']['html_url']
        activity_lines.append(f"🎉 {action.capitalize()} release <a href=\"{release_url}\">{release_name}</a> in {repo_link}")

activity_html = "<br>\n".join(activity_lines) + "<br>\n"

with open("README.md", "r", encoding="utf-8") as f:
    readme = f.read()

new_readme = re.sub(
    r"(<!--RECENT_ACTIVITY:start-->\s*).*?(\s*<!--RECENT_ACTIVITY:end-->)",
    f"\\1\n{activity_html}\n\\2",
    readme,
    flags=re.DOTALL
)

with open("README.md", "w", encoding="utf-8") as f:
    f.write(new_readme)

print("Updated README.md")
