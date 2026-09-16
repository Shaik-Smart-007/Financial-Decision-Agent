from google import genai
from google.genai import types
from dotenv import load_dotenv

from config import MAX_AGENT_TURNS

from tools import (
    extract_commitment_details,
    calculate_financial_position,
    evaluate_commitment,
)

# -----------------------------
# LOAD ENVIRONMENT
# -----------------------------

load_dotenv()

client = genai.Client()


# -----------------------------
# TOOL REGISTRY
# -----------------------------

TOOL_FUNCTIONS = {
    "extract_commitment_details": extract_commitment_details,
    "calculate_financial_position": calculate_financial_position,
    "evaluate_commitment": evaluate_commitment,
}

tools = list(TOOL_FUNCTIONS.values())


# -----------------------------
# CREATE AGENT CHAT
# -----------------------------

chat = client.chats.create(
    model="gemini-3.5-flash-lite",
    config=types.GenerateContentConfig(
        tools=tools,

        # We disable automatic function calling so that
        # OUR PYTHON CODE controls the agent loop.
        automatic_function_calling=types.AutomaticFunctionCallingConfig(
            disable=True
        ),

        system_instruction="""
You are a financial decision-support agent.

Your job is to help users evaluate whether a financial
commitment or purchase fits their stated financial situation.

You have access to Python tools.

IMPORTANT RULES:

1. Use the Python tools whenever financial calculations
   or structured evaluation are required.

2. Do not invent financial numbers.

3. Do not perform important financial calculations yourself
   when a Python tool is available.

4. If important information is missing, ask the user for it
   instead of guessing.

5. Treat existing_commitments as a MONTHLY amount.

6. Pass the ORIGINAL commitment price and its frequency straight through
   to evaluate_commitment — do not pre-convert it yourself. The tool
   normalizes weekly/yearly commitments to a monthly equivalent internally.

8. Explain decisions using the actual numbers returned
   by the Python tools.

9. The safety buffer is a conservative prototype rule used
   by this application. Do not present it as a universal
   financial rule.

10. Decision meanings:

   CAN_AFFORD =
   The purchase fits while leaving money ABOVE the
   configured safety buffer.

   TIGHT_LOW_BUFFER =
   The purchase fits mathematically, but leaves the user
   at or below the configured safety buffer.

   CANNOT_AFFORD =
   The purchase exceeds the user's available money.

11. If a tool returns an error, explain what information
    needs to be corrected or provided. Do not guess.

12. If the user provides insufficient financial information,
    ask only for the missing information needed to evaluate
    the purchase.

Your response should be clear, concise, and easy for a
normal user to understand.

13. After your explanation, always end your response with a summary block
    in EXACTLY this format, using the real numbers from the tools
    (write "N/A" for any line that wasn't calculated):

    Decision: <CAN_AFFORD|TIGHT_LOW_BUFFER|CANNOT_AFFORD>
    Monthly Income: ₹<value>
    Essential Expenses: ₹<value>
    Existing Monthly Commitments: ₹<value>
    Remaining Money: ₹<value>
    Safety Buffer: ₹<value>
    Remaining after purchase: ₹<value>

    Do not omit this block, reorder it, or add extra text inside it.
"""
    ),
)


# -----------------------------
# TOOL EXECUTOR
# -----------------------------

def run_tool(name: str, args: dict) -> dict:
    """
    Execute a tool requested by Gemini.
    """

    function = TOOL_FUNCTIONS.get(name)

    if function is None:
        return {
            "error": f"Unknown tool requested: {name}"
        }

    try:
        result = function(**args)

        if not isinstance(result, dict):
            return {
                "error": f"Tool {name} returned an invalid result."
            }

        return result

    except Exception as error:
        return {
            "error": f"Tool {name} failed: {error}"
        }


# -----------------------------
# AGENT LOOP
# -----------------------------

def run_agent(
    user_request: str,
    max_turns: int = MAX_AGENT_TURNS
):
    """
    Run the financial decision-support agent.

    Gemini decides which tools are needed.
    Python executes those tools.
    The results are sent back to Gemini.
    Gemini then produces the final answer.
    """

    try:
        response = chat.send_message(user_request)

    except Exception as error:
        print("\n❌ Could not contact Gemini.")
        print(error)
        return

    for turn in range(max_turns):

        print(f"\n🔄 Agent turn {turn + 1}")

        # ---------------------------------
        # CHECK FOR TOOL CALLS
        # ---------------------------------

        function_calls = response.function_calls

        if not function_calls:

            print("\n🤖 AGENT:")
            print(response.text)

            return response.text

        # ---------------------------------
        # EXECUTE REQUESTED TOOLS
        # ---------------------------------

        function_response_parts = []

        for call in function_calls:

            print(
                f"\n🔧 Tool requested: "
                f"{call.name}({call.args})"
            )

            result = run_tool(
                call.name,
                dict(call.args)
            )

            print(f"📊 Tool result: {result}")

            # Send the Python result back to Gemini.
            function_response_parts.append(
                types.Part.from_function_response(
                    name=call.name,
                    response={
                        "result": result
                    },
                )
            )

        # ---------------------------------
        # SEND TOOL RESULTS BACK TO GEMINI
        # ---------------------------------

        try:
            response = chat.send_message(
                function_response_parts
            )

        except Exception as error:
            print(
                "\n❌ Gemini failed while processing "
                "tool results."
            )
            print(error)
            return

    # ---------------------------------
    # SAFETY STOP
    # ---------------------------------

    print(
        "\n⚠️ Agent stopped safely after reaching "
        f"the maximum of {max_turns} turns."
    )

    print(
        "The agent could not complete the evaluation "
        "within the allowed number of steps."
    )


# -----------------------------
# MAIN PROGRAM
# -----------------------------

if __name__ == "__main__":

    print("\n===================================")
    print("💰 FINANCIAL DECISION AGENT")
    print("===================================")

    user_request = input(
        "\n💬 What do you want to evaluate?\n> "
    )

    if not user_request.strip():

        print("\n⚠️ Please enter a request.")

    else:

        run_agent(user_request)