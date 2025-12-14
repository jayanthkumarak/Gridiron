"""
LLM Prompt Chains for Gridiron
Chain A: User Query → R Script
Chain B: R Result → Memo + Chart Config
"""

import os
import json
from openai import AsyncOpenAI
from typing import Optional
from pathlib import Path

from r_client import execute_r_script

# OpenRouter configuration
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

# Model selection
CODE_MODEL = "anthropic/claude-3.5-sonnet"  # Best for code generation
SUMMARY_MODEL = "meta-llama/llama-3.1-8b-instruct"  # Fast for text synthesis

# Load analytics framework
FRAMEWORK_PATH = Path(__file__).parent / "prompts" / "nfl_analytics_framework.md"


def load_analytics_framework() -> str:
    """Load the NFL analytics framework as system context"""
    try:
        return FRAMEWORK_PATH.read_text()
    except FileNotFoundError:
        return ""


# System prompts
CODE_SYSTEM_PROMPT = """You are an expert NFL data analyst. You generate R code using the nflfastR package.

CRITICAL RULES:
1. The data is already loaded in `pbp_data` - DO NOT call load_pbp()
2. Return ONLY valid R code - no explanations, no markdown
3. End with a result that can be serialized to JSON
4. Use dplyr functions: filter, group_by, summarize, arrange
5. Always use na.rm = TRUE for calculations
6. Never generate plots or images

IMPORTANT: The R execution environment has these functions available:
- filter, select, mutate, summarize, summarise, group_by, ungroup, arrange, desc, n
- mean, sum, round, head, tail, unique, length, is.na
- pbp_data (the pre-loaded play-by-play data)

{framework}

OUTPUT FORMAT:
Return ONLY the R code. Example:
```
pbp_data |>
  filter(posteam == "SEA", down == 3, !is.na(epa)) |>
  summarize(
    plays = n(),
    epa_per_play = round(mean(epa, na.rm = TRUE), 3),
    success_rate = round(mean(success, na.rm = TRUE), 3)
  )
```
"""

MEMO_SYSTEM_PROMPT = """You are a sports analytics writer creating concise insights.

Write a brief memo based on the data provided. Format:
1. One clear headline (no markdown)
2. 2-3 sentence summary with key numbers
3. Suggest a chart configuration if the data supports visualization

Use these HTML classes for styling numbers:
- <span class="positive">+0.15</span> for positive values
- <span class="negative">-0.08</span> for negative values
- <strong>42%</strong> for emphasis

Keep it concise - this is a "one-page memo" style.

For chart configuration, respond with JSON in this format at the end:
```json
{"type": "dot", "xLabel": "Team", "yLabel": "EPA/Play", "data": [...]}
```

Chart types: "dot" (ranking), "slope" (before/after), "sparkline" (trend)
"""


async def get_client() -> AsyncOpenAI:
    """Get configured OpenAI client for OpenRouter"""
    return AsyncOpenAI(
        api_key=OPENROUTER_API_KEY,
        base_url=OPENROUTER_BASE_URL,
    )


async def chain_a_generate_r_script(query: str) -> str:
    """
    Chain A: Convert natural language query to R script
    """
    client = await get_client()
    framework = load_analytics_framework()
    
    response = await client.chat.completions.create(
        model=CODE_MODEL,
        messages=[
            {
                "role": "system",
                "content": CODE_SYSTEM_PROMPT.format(framework=framework)
            },
            {
                "role": "user",
                "content": f"Generate R code for this query: {query}"
            }
        ],
        temperature=0.1,  # Low temperature for code
        max_tokens=1000,
    )
    
    r_code = response.choices[0].message.content or ""
    
    # Clean up code block markers if present
    r_code = r_code.strip()
    if r_code.startswith("```r"):
        r_code = r_code[4:]
    elif r_code.startswith("```R"):
        r_code = r_code[4:]
    elif r_code.startswith("```"):
        r_code = r_code[3:]
    if r_code.endswith("```"):
        r_code = r_code[:-3]
    
    return r_code.strip()


async def chain_b_synthesize_memo(query: str, data: dict) -> dict:
    """
    Chain B: Convert R result to memo with chart config
    """
    client = await get_client()
    
    response = await client.chat.completions.create(
        model=SUMMARY_MODEL,
        messages=[
            {
                "role": "system",
                "content": MEMO_SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": f"""Original question: {query}

Data from analysis:
{json.dumps(data, indent=2)}

Write a brief memo and suggest chart configuration."""
            }
        ],
        temperature=0.7,
        max_tokens=800,
    )
    
    content = response.choices[0].message.content or ""
    
    # Parse response
    lines = content.strip().split('\n')
    headline = lines[0].strip('#').strip() if lines else "Analysis Results"
    
    # Extract chart config if present
    chart_config = None
    summary_text = content
    
    if "```json" in content:
        try:
            json_start = content.index("```json") + 7
            json_end = content.index("```", json_start)
            chart_json = content[json_start:json_end].strip()
            chart_config = json.loads(chart_json)
            summary_text = content[:content.index("```json")].strip()
        except (ValueError, json.JSONDecodeError):
            pass
    
    # Clean up summary
    summary_lines = summary_text.split('\n')[1:]  # Skip headline
    summary = '\n'.join(line for line in summary_lines if line.strip())
    
    return {
        "headline": headline,
        "summary": f"<p>{summary}</p>",
        "chart": chart_config
    }


async def analyze_query(query: str) -> dict:
    """
    Main analysis pipeline:
    1. Generate R code from query
    2. Execute R code
    3. Synthesize memo from results
    """
    # Chain A: Generate R code
    r_script = await chain_a_generate_r_script(query)
    
    # Execute R script
    r_result = await execute_r_script(r_script)
    
    if not r_result.get("success"):
        return {
            "headline": "Analysis Error",
            "summary": f"<p>Could not execute analysis: {r_result.get('error', 'Unknown error')}</p>",
            "error": r_result.get("error"),
            "raw_data": {"r_script": r_script}
        }
    
    # Chain B: Synthesize memo
    memo = await chain_b_synthesize_memo(query, r_result.get("result", {}))
    memo["raw_data"] = r_result.get("result")
    
    return memo
