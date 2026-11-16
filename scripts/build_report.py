"""Write the five case-study findings from the loaded warehouse."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from phonepe.analysis import (  # noqa: E402
    add_quarter_growth,
    available_years,
    merchant_penetration,
    quarterly_state_totals,
    state_transaction_leaders,
    top_entities,
    transaction_mix,
    user_totals,
)


def _fmt_int(value) -> str:
    if value is None:
        return "n/a"
    return f"{int(value):,}"


def _top_lines(frame, name_col: str, value_col: str, limit: int = 5) -> str:
    if frame.empty:
        return "- No rows."
    lines = []
    for _, row in frame.head(limit).iterrows():
        lines.append(f"- {row[name_col]}: {_fmt_int(row[value_col])}")
    return "\n".join(lines)


def main() -> None:
    years = available_years()
    if not years:
        raise SystemExit("No rows loaded. Run scripts/setup.sh first.")
    year = max(year for year in years if year <= 2025) if any(y <= 2025 for y in years) else max(years)
    quarter = 1

    leaders = state_transaction_leaders(year, quarter, limit=5)
    mix = transaction_mix("india", year)
    users = user_totals(year)
    users_q = users[users["quarter"] == quarter] if not users.empty else users
    penetration = merchant_penetration(year, quarter)
    growth = add_quarter_growth(quarterly_state_totals())
    latest = growth[(growth["year"] == year) & (growth["quarter"] == quarter)].dropna(subset=["qoq_change"])
    fastest = latest.sort_values("qoq_change", ascending=False).head(5)
    top_districts = top_entities("top_transaction", year, quarter, "district", limit=5)
    top_user_states = top_entities("top_user", year, quarter, "state", limit=5)

    mix_lines = "- No national mix."
    if not mix.empty:
        totals = mix.groupby("transaction_type")["transaction_count"].sum().sort_values(ascending=False)
        mix_lines = "\n".join(f"- {name}: {_fmt_int(count)}" for name, count in totals.items())

    growth_lines = "- Not enough history."
    if not fastest.empty:
        growth_lines = "\n".join(
            f"- {row.state}: {row.qoq_change:.1%} versus the previous quarter"
            for row in fastest.itertuples()
        )

    penetration_lines = "- No overlap between user and merchant tables."
    if not penetration.empty:
        penetration_lines = "\n".join(
            f"- {row.state}: {_fmt_int(row.registered_merchants)} merchants, "
            f"{row.merchants_per_user:.4f} per registered user"
            for row in penetration.head(5).itertuples()
        )

    report = f"""# PhonePe findings

Period used for the snapshot: {year} Q{quarter}. The latest full calendar year at or before 2025 is preferred so a partial current year does not dominate the ranking.

## 1. Transaction dynamics

National payment-category counts for {year}:

{mix_lines}

States with the most mapped transactions in Q{quarter}:

{_top_lines(leaders, "state", "transaction_count")}

Fastest quarter-on-quarter transaction growth in that quarter:

{growth_lines}

## 2. User engagement

Device-brand files are not in the current Pulse dump, so engagement is measured from registered users. Largest states in {year} Q{quarter}:

{_top_lines(users_q, "state", "registered_users")}

Top states from the top-user extract:

{_top_lines(top_user_states, "entity_name", "metric_value")}

## 3. Merchant penetration

The course brief asks for insurance. The live Pulse repository publishes merchant registration instead. Highest merchant counts, with merchants per registered user:

{penetration_lines}

## 4. Market expansion

Use the state leader list above as the expansion baseline. Amounts are present on the map transaction table even when the aggregated transaction files only carry counts. Compare `transaction_amount` and `transaction_count` in the dashboard before treating a state as high value rather than high volume.

## 5. Top districts

Highest transaction districts in India for {year} Q{quarter}:

{_top_lines(top_districts, "entity_name", "metric_value")}

Pin codes are not in this Pulse snapshot. If an older dump with a `pincodes` array is placed in `data/pulse`, the loader stores those rows with `entity_level = pincode`.
"""
    out = ROOT / "reports" / "findings.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(report, encoding="utf-8")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
