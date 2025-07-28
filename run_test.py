import json
import re
from playwright.sync_api import sync_playwright, expect

# Mapping of recognized verbs to internal actions
ACTION_MAP = {
    "click": "click",
    "clicca": "click",
    "press": "click",
    "premi": "click",
    "fill": "fill",
    "type": "fill",
    "enter": "fill",
    "inserisci": "fill",
    "digita": "fill",
    "select": "select",
    "seleziona": "select",
    "expect": "expect",
    "verify": "expect",
    "check": "expect",
    "verifica": "expect",
    "controlla": "expect",
    "go": "goto",
    "navigate": "goto",
    "vai": "goto",
    "apri": "goto",
    "wait": "waitFor",
    "aspetta": "waitFor",
}


def apply_variables(text: str, variables: dict) -> str:
    """Replace {{var}} in text with values from variables."""
    def repl(match):
        key = match.group(1)
        return str(variables.get(key, match.group(0)))
    return re.sub(r"{{\s*(\w+)\s*}}", repl, text)


def split_sentences(text: str):
    """Split a block of text into sentences."""
    return [s.strip() for s in re.split(r"[.!?]", text) if s.strip()]


def parse_step(step: str) -> dict:
    """Parse a single textual step into a structured representation."""
    tokens = step.split()
    if not tokens:
        return {"action": "TODO", "original": step}
    verb = tokens[0].lower()
    action = ACTION_MAP.get(verb)
    if not action:
        return {"action": "TODO", "original": step}
    rest = step[len(tokens[0]):].strip()

    if action == "click":
        m = re.search(r"(?:on the )?(.+) link", rest, re.IGNORECASE)
        if m:
            return {"action": "click", "target": {"role": "link", "name": m.group(1)}}
        m = re.search(r"the (.+) button", rest, re.IGNORECASE)
        if m:
            return {"action": "click", "target": {"role": "button", "name": m.group(1)}}
        return {"action": "click", "target": rest}

    if action == "fill":
        m = re.search(r"the (.+) field with (.+)", rest, re.IGNORECASE)
        if m:
            return {
                "action": "fill",
                "target": {"type": "input", "name": m.group(1)},
                "value": m.group(2),
            }
        m = re.search(r"the (.+) textarea with (.+)", rest, re.IGNORECASE)
        if m:
            return {
                "action": "fill",
                "target": {"type": "textarea", "name": m.group(1)},
                "value": m.group(2),
            }
        return {"action": "TODO", "original": step}

    if action == "select":
        m = re.search(r"(.+) from the (.+) dropdown", rest, re.IGNORECASE)
        if m:
            return {
                "action": "select",
                "target": {"name": m.group(2)},
                "value": m.group(1),
            }
        return {"action": "TODO", "original": step}

    if action == "expect":
        m = re.search(r"(?:that )?(.+?) contains '(.+)'", rest, re.IGNORECASE)
        if m:
            return {"action": "expect", "target": m.group(1), "value": m.group(2)}
        return {"action": "TODO", "original": step}

    if action == "goto":
        m = re.search(r"(?:to )?(.+)", rest, re.IGNORECASE)
        if m:
            return {"action": "goto", "target": m.group(1)}
        return {"action": "TODO", "original": step}

    if action == "waitFor":
        m = re.search(r"(\d+)", rest)
        if m:
            return {"action": "waitFor", "value": int(m.group(1))}
        return {"action": "TODO", "original": step}

    return {"action": "TODO", "original": step}


def parse_steps(description: str):
    """Parse the textual description into structured steps."""
    return [parse_step(s) for s in split_sentences(description)]


def execute_step(step: dict, page):
    """Execute a single structured step using Playwright."""
    action = step.get("action")
    if action == "TODO":
        print(f"TODO: {step['original']}")
        return

    if action == "click":
        target = step["target"]
        if isinstance(target, dict):
            page.get_by_role(target["role"], name=target["name"]).click()
        else:
            page.click(target)
        return

    if action == "fill":
        t = step["target"]
        if t["type"] == "input":
            selector = f"input[name='{t['name']}']"
        else:
            selector = f"textarea[name='{t['name']}']"
        page.fill(selector, step["value"])
        return

    if action == "select":
        selector = f"select[name='{step['target']['name']}']"
        page.select_option(selector, step["value"])
        return

    if action == "expect":
        expect(page.locator('body')).to_contain_text(step["value"])
        return

    if action == "goto":
        page.goto(step["target"])
        return

    if action == "waitFor":
        page.wait_for_timeout(step["value"] * 1000)
        return

    print(f"Unhandled action: {action}")


def run_test(test_config: dict):
    description = apply_variables(test_config["description"], test_config.get("variables", {}))
    steps = parse_steps(description)
    url = test_config["url"]
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(url)
        for step in steps:
            execute_step(step, page)
        browser.close()


def main(path: str):
    with open(path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    run_test(config)


if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python run_test.py <test_config.json>")
        sys.exit(1)
    main(sys.argv[1])
