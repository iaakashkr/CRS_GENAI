import yaml
from pathlib import Path

def load_prompt(filename: str, **kwargs) -> str:
    path = Path(__file__).resolve().parent.parent / "prompts" / filename
    with open(path, 'r', encoding="utf-8") as f:
        data = yaml.safe_load(f)

    parts = []
    
    if "system" in data:
        parts.append(data["system"])

    for ex in data.get("examples", []):
        parts.append(f"User: {ex['user']}")
        parts.append(f"Assistant: {ex['assistant']}")

    if "user" in data:
        parts.append(data["user"].format(**kwargs))  # <-- injects variables

    if "format" in data:
        parts.append("Output Format:\n" + data["format"])

    return "\n\n".join(parts)
