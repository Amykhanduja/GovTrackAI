import json
import logging
import os

logger = logging.getLogger('app.registry')

class OrganizationRegistry:
    def __init__(self, config_path="config/organizations.json"):
        self.config_path = config_path
        self.organizations = []
        self.load()

    def load(self):
        if not os.path.exists(self.config_path):
            return
        with open(self.config_path, 'r') as f:
            data = json.load(f)
            self.organizations = data.get('organizations', [])
            
    def get_by_category(self, category: str):
        return [org for org in self.organizations if org.get('category') == category]

    def get_by_domain(self, domain_id: str):
        return [org for org in self.organizations if domain_id in org.get('career_domain', [])]
        
    def generate_markdown_report(self, output_path="docs/Supported_Organizations.md"):
        stats = {}
        for org in self.organizations:
            cat = org.get('category', 'UNCATEGORIZED')
            stats[cat] = stats.get(cat, 0) + 1
            
        lines = ["# Supported Government Organizations\n"]
        lines.append("## Coverage Statistics")
        for cat, count in stats.items():
            lines.append(f"- **{cat}**: {count} organizations")
            
        lines.append("\n## Organization Registry")
        for org in self.organizations:
            lines.append(f"### {org.get('name')}")
            lines.append(f"- **Category**: {org.get('category')}")
            lines.append(f"- **Parent Ministry**: {org.get('parent_ministry')}")
            lines.append(f"- **Career Domains**: {', '.join(org.get('career_domain', []))}")
            lines.append(f"- **Recruitment URL**: {org.get('recruitment_url')}")
            lines.append(f"- **Preferred Method**: {org.get('preferred_method')}")
            lines.append("")
            
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w') as f:
            f.write("\n".join(lines))
