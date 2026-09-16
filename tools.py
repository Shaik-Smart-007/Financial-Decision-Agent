from config import BUFFER_RATE, MIN_BUFFER
from validators import (
    ValidationError,
    validate_number,
    validate_frequency,
    validate_boolean,
)


def extract_commitment_details(
    price: float,
    frequency: str = "one-time",
    essential: bool = False
) -> dict:
    """
    Validate and structure the details of a financial commitment.
    """

    try:
        price = validate_number(price, "price")
        frequency = validate_frequency(frequency)
        essential = validate_boolean(essential, "essential")

        # Convert recurring commitments into a monthly equivalent.
        if frequency == "weekly":
            monthly_equivalent_price = price * 4.33
        elif frequency == "yearly":
            monthly_equivalent_price = price / 12
        else:
            monthly_equivalent_price = price

        return {
            "price": price,
            "frequency": frequency,
            "essential": essential,
            "monthly_equivalent_price": round(
                monthly_equivalent_price, 2
            ),
        }

    except ValidationError as error:
        return {
            "error": error.message
        }


def calculate_financial_position(
    income: float,
    essential_expenses: float,
    existing_commitments: float = 0
) -> dict:
    """
    Calculate the user's available money and a conservative
    safety buffer.
    
    existing_commitments is assumed to be a monthly amount.
    """

    try:
        income = validate_number(income, "income")
        essential_expenses = validate_number(
            essential_expenses,
            "essential_expenses",
            allow_zero=True
        )
        existing_commitments = validate_number(
            existing_commitments,
            "existing_commitments",
            allow_zero=True
        )

        remaining_money = (
            income
            - essential_expenses
            - existing_commitments
        )

        safety_buffer = max(
            income * BUFFER_RATE,
            MIN_BUFFER
        )

        safe_to_spend = remaining_money - safety_buffer

        return {
            "income": income,
            "essential_expenses": essential_expenses,
            "existing_commitments": existing_commitments,
            "remaining_money": round(remaining_money, 2),
            "safety_buffer": round(safety_buffer, 2),
            "safe_to_spend": round(safe_to_spend, 2),
        }

    except ValidationError as error:
        return {
            "error": error.message
        }


def evaluate_commitment(
    remaining_money: float,
    commitment_price: float,
    frequency: str = "one-time",
    safety_buffer: float = 0
) -> dict:
    """
    Evaluate a commitment using the available money and a conservative
    safety buffer. Recurring commitments are normalized to a monthly
    equivalent HERE, in Python, so correctness never depends on which
    field the LLM chooses.
    """

    try:
        remaining_money = validate_number(
            remaining_money,
            "remaining_money",
            allow_zero=True
        )

        commitment_price = validate_number(
            commitment_price,
            "commitment_price"
        )

        safety_buffer = validate_number(
            safety_buffer,
            "safety_buffer",
            allow_zero=True
        )

        frequency = validate_frequency(frequency)

        if frequency == "weekly":
            monthly_cost = commitment_price * 4.33
        elif frequency == "yearly":
            monthly_cost = commitment_price / 12
        else:
            monthly_cost = commitment_price

        remaining_after_purchase = remaining_money - monthly_cost
        remaining_after_buffer = remaining_after_purchase - safety_buffer

        if remaining_after_purchase < 0:
            decision = "CANNOT_AFFORD"

        elif remaining_after_buffer <= 0:
            decision = "TIGHT_LOW_BUFFER"

        else:
            decision = "CAN_AFFORD"

        return {
            "decision": decision,
            "monthly_equivalent_cost": round(monthly_cost, 2),
            "remaining_after_purchase": round(
                remaining_after_purchase, 2
            ),
            "remaining_after_buffer": round(
                remaining_after_buffer, 2
            ),
        }

    except ValidationError as error:
        return {
            "error": error.message
        }


if __name__ == "__main__":
    print("\n=== TEST 1: Commitment ===")

    commitment = extract_commitment_details(
        price=5000,
        frequency="one-time",
        essential=False
    )

    print(commitment)

    print("\n=== TEST 2: Financial Position ===")

    position = calculate_financial_position(
        income=30000,
        essential_expenses=18000,
        existing_commitments=3000
    )

    print(position)

    print("\n=== TEST 3: Evaluation ===")

    evaluation = evaluate_commitment(
        remaining_money=position["remaining_money"],
        commitment_price=commitment["price"],
        frequency=commitment["frequency"],
        safety_buffer=position["safety_buffer"]
    )

    print(evaluation)