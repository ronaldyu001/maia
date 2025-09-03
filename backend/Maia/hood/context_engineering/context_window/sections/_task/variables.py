DEFAULT_CHAT = """
Current task: Be helpful and concise. Ask at most one clarifying question.
"""

SUMMARIZE_CONVERSATION = """
Current task:
- Produce a concise summary in 1–6 bullet points.
- No preamble, no conclusions, no continuation of the conversation.
- Output plain text bullets only.

Granularity vs. coherence (for embedding/RAG):
- Wide conversations → 1 bullet per distinct topic (compact bullets).
- Narrow conversations → fewer, richer bullets that capture the full idea; only split if ideas are clearly distinct.
- Aim for 1–5 sentences per bullet. Preserve enough detail to be self-contained.

Content selection:
- Focus on what was actually discussed: key facts, problems raised, solutions proposed, decisions made, constraints, or follow-ups.
- Omit filler, pleasantries, repeated phrasing, and speculation.
- Do not rephrase as advice or instructions — capture what was said.

Clarity:
- Each bullet should express a single cohesive idea and stand alone without the transcript. i.e. a problem and its solution.
- Use neutral, past-tense “notes” style (e.g., “Ronald Discussed/Did/Asked X and I Y”) rather than prescriptive wording.
- Use plain, direct language; avoid jargon unless central to the discussion.

The following text is the conversation to summarize:
"""