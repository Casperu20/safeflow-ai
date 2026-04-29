import os
import json
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def detect_scam_patterns(payment):
    text = payment.get("message", "").lower()
    reasons = []
    score = 0
    scam_type = "Unknown"

    if payment.get("is_new_recipient"):
        score += 25
        reasons.append("New recipient")

    if "urgent" in text or "pay today" in text or "immediately" in text:
        score += 20
        reasons.append("Urgent language detected")

    if "bank details changed" in text or "new account" in text:
        score += 25
        reasons.append("Changed bank details mentioned")
        scam_type = "Payment Redirection"

    if payment["amount"] > payment.get("user_average_amount", 0) * 3:
        score += 20
        reasons.append("Amount is unusually high for this user")

    score = min(score, 100)

    if score >= 75:
        risk_level = "High"
        decision = "step_up_verification"
    elif score >= 40:
        risk_level = "Medium"
        decision = "warn_user"
    else:
        risk_level = "Low"
        decision = "allow"

    return {
        "risk_score": score,
        "risk_level": risk_level,
        "scam_type": scam_type,
        "decision": decision,
        "reasons": reasons,
    }


def generate_explanation(result, payment):
    prompt = f"""
You are SafeFlow AI, a scam-prevention assistant.

Explain this payment risk result in simple language for a banking user.

Payment:
{json.dumps(payment, indent=2)}

Risk result:
{json.dumps(result, indent=2)}

Return:
1. Short explanation
2. Why it is risky
3. Recommended action

Do not invent facts. Use only the provided data.
"""

    response = client.responses.create(
        model="gpt-5.5",
        input=prompt
    )

    return response.output_text


if __name__ == "__main__":
    payment = {
        "amount": 2500,
        "recipient_name": "ABC Consulting",
        "is_new_recipient": True,
        "payment_category": "invoice",
        "message": "Urgent invoice payment. Bank details changed. Please pay today.",
        "user_average_amount": 300
    }

    result = detect_scam_patterns(payment)
    explanation = generate_explanation(result, payment)

    final_output = {
        **result,
        "explanation": explanation
    }

    print(json.dumps(final_output, indent=2))