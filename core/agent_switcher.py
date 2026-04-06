# ============================================================
# FreedomForge AI — core/agent_switcher.py
# Fixed: you now choose which agents run (no more forced 5 every time)
# ============================================================

from core.model_manager import get_model_list

AGENTS = {
    "Researcher": "Fast fact-finding and web search style",
    "Critic": "Finds flaws and improves answers",
    "Creative": "Wild ideas and storytelling",
    "Synthesizer": "Combines everything into clean output",
    "Coder": "Writes actual working code"
}

def get_available_agents():
    return list(AGENTS.keys())

def run_selected_agents(task: str, selected_agents: list):
    results = {}
    for agent in selected_agents:
        if agent == "Coder":
            results[agent] = f"[{agent}] Wrote code for: {task[:60]}..."
        elif agent == "Researcher":
            results[agent] = f"[{agent}] Found facts on: {task[:60]}..."
        else:
            results[agent] = f"[{agent}] Processed: {task[:60]}..."
    return results
