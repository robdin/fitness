"""Monthly membership planning arithmetic, not a demand or earnings forecast."""
from decimal import Decimal, InvalidOperation, ROUND_CEILING
from .common import OSFailure


def scenario(data):
    fields = ("members", "monthly_price", "fee_refund_fraction", "variable_cost_per_member",
              "fixed_monthly_cost", "founder_hours", "hourly_value")
    try:
        v = {k: Decimal(str(data[k])) for k in fields}
        if any(not x.is_finite() or x < 0 for x in v.values()) or v["fee_refund_fraction"] >= 1 or v["members"] != v["members"].to_integral_value():
            raise ValueError("Invalid nonnegative planning input")
    except (KeyError, ValueError, InvalidOperation) as exc:
        raise OSFailure(f"Invalid economics scenario: {exc}") from exc
    contribution = v["monthly_price"]*(1-v["fee_refund_fraction"])-v["variable_cost_per_member"]
    gross = v["members"]*v["monthly_price"]
    labor = v["founder_hours"]*v["hourly_value"]
    cash = v["members"]*contribution-v["fixed_monthly_cost"]
    def amount(value): return float(value.quantize(Decimal(".01")))
    def breakeven(cost): return int((cost/contribution).to_integral_value(rounding=ROUND_CEILING)) if contribution > 0 else None
    return {"currency": data.get("currency", "USD"), "assumption_only": True,
            "gross_mrr": amount(gross), "contribution_per_member": amount(contribution),
            "cash_contribution": amount(cash), "after_founder_time": amount(cash-labor),
            "cash_breakeven_members": breakeven(v["fixed_monthly_cost"]),
            "labor_inclusive_breakeven_members": breakeven(v["fixed_monthly_cost"]+labor),
            "exclusions": "Taxes, acquisition, annual-plan allocation, one-time sales and ads. Substitute actual fees/refunds. Subscriber demand and churn are not estimated."}
