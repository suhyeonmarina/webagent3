from __future__ import annotations

import json
from typing import List, Dict, Tuple


MODE_SAME_SUBDOMAIN_SAME_WEBSITE = "same_subdomain_same_website"
MODE_SAME_SUBDOMAIN_DIFF_WEBSITE = "same_subdomain_diff_website"
MODE_DIFF_SUBDOMAIN_DIFF_WEBSITE = "diff_subdomain_diff_website"


system_prompt_before = (
    "You are designing realistic user scenarios for a web agent benchmark.\n"
    "You will be given several concrete subtasks that a web agent could perform.\n"
    "Your job is to:\n"
    "1) Select a subset of 2 to 4 subtasks that could realistically be performed together by a single user.\n"
    "2) Only select subtasks that are tightly connected.\n"
    "3) Write a short, natural-language description of this situation as 'scenario'.\n"
    "4) Write a single high-level objective that unifies the selected subtasks as 'combined_task'.\n\n"
    "Constraints:\n"
    "- You do NOT need to USE ALL subtasks; selecting a coherent subset is encouraged.\n"
    "- The scenario must sound realistic and coherent for the selected subtasks.\n"
    "- You MUST include the exact selected subtasks verbatim in a list called 'selected_subtasks'. Do NOT rewrite, paraphrase, or summarize the subtasks.\n"
    "- If it is NOT realistically possible to find ANY subset of subtasks that can be naturally combined,\n"
    '  return ONLY the string "PASS".\n'
    "- If you return a scenario, return ONLY valid JSON with exactly these keys:\n"
    '  {"scenario": "...", "combined_task": "...", "selected_subtasks": [...]}'
)

system_prompt = (
    "You are designing realistic user scenarios for a web agent benchmark.\n"
    "You will be given several concrete subtasks that a web agent could perform.\n\n"
    "Your job is to:\n"
    "1) Select a subset of 2 to 4 subtasks that a single user would realistically do in ONE sitting.\n"
    "2) Only select subtasks that are tightly connected.\n"
    "3) Write a short natural-language 'scenario' that makes the connection obvious.\n"
    "4) Write a single high-level 'combined_task' that naturally unifies them.\n\n"
    
    "Tight-connection rule (MUST FOLLOW):\n"
    "- The selected subtasks must share at least TWO of the following anchors:\n"
    "  (A) same object/entity (e.g., same order, same person/patient, same dog, same recipe menu)\n"
    "  (B) same user goal/decision (one clear outcome the user wants)\n"
    "  (C) same time window (e.g., before an appointment, today, this weekend)\n"
    "  (D) same workflow/transaction chain (e.g., find -> compare -> choose -> verify/submit)\n"
    "- If you cannot find a subset satisfying the rule, return ONLY the string \"PASS\".\n\n"
    
    "Realism constraints:\n"
    "- Avoid 'kitchen-sink' stories that bundle unrelated errands.\n"
    "- Do NOT add new subtasks. Use only the provided ones.\n"

    "Output constraints:\n"
    "- You MUST include the exact selected subtasks verbatim in 'selected_subtasks'. Do NOT rewrite them.\n"
    "- If you return a scenario, return ONLY valid JSON with exactly these keys:\n"
    "- Keep scenario to 2–4 sentences. No long backstory."
    "- Do NOT repeat the same information across sentences"
    "  {\"scenario\": \"...\", \"combined_task\": \"...\", \"selected_subtasks\": [...]}.\n"
)

def build_prompts(
    candidate_blocks: List[Dict],
    mode: str,
) -> Tuple[str, str]:
    """
    candidate_blocks: LLM에 보여줄 후보 블록 리스트
      - same_website_same_subdomain: [{"website": "...", "tasks": [...], [...] }]
      - diff_website_same_subdomain: [{"website": "...", "tasks": [...] }, {"website": "...", "tasks": [...]} ...]
      - diff_website_diff_subdomain: [{"subdomain": "...", "website": "...", "tasks": [...] }, ...]
    """

    subtasks = []

    for block in candidate_blocks:
        tasks = block.get("tasks", [])
        subtasks.extend(tasks)

    # 혹시나 중복 제거
    subtasks = list(dict.fromkeys(subtasks))

    subtasks_str = "\n".join(
        f"- {task}" for task in subtasks
    )

    # ---------------------------------
    # 3. user prompt 구성
    # ---------------------------------
    user_prompt = (
        "Here are the subtasks:\n\n"
        f"{subtasks_str}\n\n"
        "Now produce a realistic 'scenario' and a high-level "
        "'combined_task' that naturally includes all of these subtasks."
    )

    return system_prompt, user_prompt