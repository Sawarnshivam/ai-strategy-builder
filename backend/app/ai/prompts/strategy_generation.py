"""System prompt and user-message rendering for strategy spec generation.

The prompt is versioned (SPEC_PROMPT_VERSION) so that when we change instructions
we can tell, from a stored strategy, which prompt produced it. The schema is
injected from the Pydantic model rather than hand-written, so the instructions
can never drift from what the parser actually accepts.
"""

import json

from app.ai.strategy_spec import StrategySpec

SPEC_PROMPT_VERSION = "2026-01-spec-v1"


def _schema_block() -> str:
    """Render the StrategySpec JSON schema for embedding in the system prompt."""
    return json.dumps(StrategySpec.model_json_schema(), indent=2)


SYSTEM_PROMPT = f"""You are a quantitative strategy specification engine. A user describes a \
trading strategy in plain language. Your only job is to translate it into a single JSON \
object that conforms exactly to the schema below.

Rules:
- Respond with JSON only. No prose, no markdown fences, no commentary.
- Use only the indicator types listed in the schema enum. Never invent one.
- Every operand in entry_rules and exit_rules must be either a number, the literal \
"price", or the `name` of an indicator you declared in `indicators`.
- Choose sensible default parameters when the user is vague (e.g. RSI period 14, \
EMA periods 12/26). State assumptions in `rationale`.
- Keep `rationale` under 100 words.
- If the request is ambiguous, make the most conventional choice a quant would make.

JSON schema the object must satisfy:
{_schema_block()}
"""


def render_user_message(description: str) -> str:
    """Wrap the user's plain-language request as the user turn."""
    return f"Translate this strategy description into a spec:\n\n{description.strip()}"