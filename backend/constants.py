from typing import Literal

Action = Literal[
    "new_research",
    "follow_up",
    "compare",
    "rewrite",
    "summarize",
    "optimize",
    "elaborate",
]

Provider = Literal[
    "tavily",
    "exa",
    "arxiv",
    "semanticscholar",
    "openalex",
]

ComparisonStrategy = Literal[
    "simple",
    "hierarchical",
]

WorkflowStep = Literal[
    "planning",
    "routing",
    "research",
    "comparator",
    "fact_check",
    "writer",
    "failed",
    "completed",
]

VALID_PROVIDERS = {
    "tavily",
    "exa",
    "arxiv",
    "semanticscholar",
    "openalex",
}

VALID_ACTIONS = {
    "new_research",
    "follow_up",
    "compare",
    "rewrite",
    "summarize",
    "optimize",
    "elaborate",
}

VALID_COMPARISON_STRATEGIES = {
    "simple",
    "hierarchical",
}

RESEARCH_ACTIONS = {
    "new_research",
    "follow_up",
    "compare",
    "elaborate",
}

WRITER_ACTIONS = {
    "rewrite",
    "summarize",
    "optimize",
}