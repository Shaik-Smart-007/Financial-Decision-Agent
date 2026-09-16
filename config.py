# Business rules for the financial decision agent.

# Prototype safety-buffer rule:
# The user should ideally keep this amount untouched after a purchase.
BUFFER_RATE = 0.10
MIN_BUFFER = 1000

# Supported commitment frequencies.
VALID_FREQUENCIES = {
    "one-time",
    "monthly",
    "weekly",
    "yearly"
}

# Maximum number of Gemini/tool-calling turns.
MAX_AGENT_TURNS = 6