import re
import sys
from pathlib import Path


def update_readme(usage_text: str) -> None:
    readme_path = Path('README.md')
    readme_content = readme_path.read_text()
    updated_content = re.sub(
        r'```usage\n.*?\n```',
        f'```usage\n{usage_text}\n```',
        readme_content,
        flags=re.DOTALL
    )
    readme_path.write_text(updated_content)


if __name__ == "__main__":
    usage_text = sys.stdin.read().strip()
    update_readme(usage_text)
