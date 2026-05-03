"""Generic (unconstrained) model — verbose natural language output."""
import anthropic

_SYSTEM = """You are a network operations analyst. Summarize the investigation findings in a comprehensive report. Be thorough and include all relevant context, background, and caveats."""


def summarize(evidence: list[str], tool_results: list[dict], client: anthropic.Anthropic) -> dict:
    content = "Based on the following investigation evidence, provide a comprehensive incident analysis:\n\n"
    content += "\n".join(f"- {e}" for e in evidence)
    if tool_results:
        content += "\n\nTool results gathered during investigation:\n"
        for tr in tool_results[:4]:
            content += f"\n{tr['tool']}:\n{str(tr['result'])[:600]}\n"

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2048,
        system=_SYSTEM,
        messages=[{"role": "user", "content": content}],
    )

    return {
        "output": response.content[0].text,
        "input_tokens": response.usage.input_tokens,
        "output_tokens": response.usage.output_tokens,
        "total_tokens": response.usage.input_tokens + response.usage.output_tokens,
    }
