#!/usr/bin/env python3
"""Firecrawl vs Local Crawler cost estimation tool.

Usage:
    python3 ops/scripts/estimate_crawler_cost.py
    python3 ops/scripts/estimate_crawler_cost.py --articles 660 --scrape-credits 3
    echo "660" | python3 ops/scripts/estimate_crawler_cost.py --stdin

Pure stdlib (argparse + json). No third-party dependencies.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass


# ── Firecrawl pricing tiers (as of 2026-09) ──

@dataclass(frozen=True)
class FirecrawlTier:
    name: str
    monthly_fee_usd: float
    credits_per_month: int
    credits_are_total: bool  # True = lifetime (Free); False = monthly (paid)
    extra_cost_per_1k: float  # cost per 1000 extra credits beyond plan


FIRECRAWL_TIERS = [
    FirecrawlTier("Free",        0.0,    1000,  True,  0.0),
    FirecrawlTier("Hobby",      16.0,    5000,  False, 0.0),
    FirecrawlTier("Standard",   99.0,   30000,  False, 5.0),
]

# ── Local cost defaults ──

DEFAULT_MAC_STUDIO_WATTS    = 30
DEFAULT_RUNNING_HOURS_PER_DAY = 24
DEFAULT_DAYS_PER_MONTH       = 30
DEFAULT_PRICE_PER_KWH        = 0.20   # USD — adjust to your electricity rate
DEFAULT_HARDWARE_MONTHLY     = 0.0    # set >0 if amortizing hardware purchase


def firecrawl_cost(tier: FirecrawlTier, articles: int, credits_per_article: int) -> dict:
    """Return cost details for a Firecrawl tier given article volume."""
    total_credits = articles * credits_per_article
    base_cost = tier.monthly_fee_usd
    extra_credits = max(0, total_credits - tier.credits_per_month)
    extra_cost = (extra_credits / 1000) * tier.extra_cost_per_1k
    total_cost = base_cost + extra_cost
    fits = total_credits <= tier.credits_per_month
    return {
        "tier": tier.name,
        "monthly_fee": base_cost,
        "plan_credits": tier.credits_per_month,
        "credits_needed": total_credits,
        "credits_are_total": tier.credits_are_total,
        "fits_in_plan": fits,
        "extra_credits": extra_credits,
        "extra_cost": round(extra_cost, 2),
        "total_cost": round(total_cost, 2),
    }


def local_cost(watts: float, hours: float, days: float, price_per_kwh: float,
               hardware_monthly: float) -> dict:
    """Return monthly local running cost."""
    kwh = watts * hours * days / 1000
    electricity = kwh * price_per_kwh
    total = electricity + hardware_monthly
    return {
        "watts": watts,
        "hours_per_day": hours,
        "days_per_month": days,
        "kwh_per_month": round(kwh, 2),
        "price_per_kwh": price_per_kwh,
        "electricity_cost": round(electricity, 2),
        "hardware_monthly": hardware_monthly,
        "total_cost": round(total, 2),
    }


def markdown_table(headers: list[str], rows: list[list[str]]) -> str:
    """Render a simple markdown table."""
    widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            widths[i] = max(widths[i], len(cell))

    def pad(s: str, w: int) -> str:
        return s + " " * (w - len(s))

    lines = []
    lines.append("| " + " | ".join(pad(h, widths[i]) for i, h in enumerate(headers)) + " |")
    lines.append("| " + " | ".join("-" * widths[i] for i in range(len(headers))) + " |")
    for row in rows:
        lines.append("| " + " | ".join(pad(cell, widths[i]) for i, cell in enumerate(row)) + " |")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Compare Firecrawl cloud vs local crawler monthly costs.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python3 ops/scripts/estimate_crawler_cost.py\n"
            "  python3 ops/scripts/estimate_crawler_cost.py --articles 660 --scrape-credits 3\n"
            "  echo '660' | python3 ops/scripts/estimate_crawler_cost.py --stdin\n"
        ),
    )
    parser.add_argument("--articles", type=int, default=660,
                        help="Monthly articles to crawl (default: 660)")
    parser.add_argument("--scrape-credits", type=int, default=3,
                        help="Firecrawl credits per scrape (default: 3)")
    parser.add_argument("--watts", type=float, default=DEFAULT_MAC_STUDIO_WATTS,
                        help=f"Device wattage (default: {DEFAULT_MAC_STUDIO_WATTS}W)")
    parser.add_argument("--price-per-kwh", type=float, default=DEFAULT_PRICE_PER_KWH,
                        help=f"Electricity price USD/kWh (default: ${DEFAULT_PRICE_PER_KWH})")
    parser.add_argument("--hardware-monthly", type=float, default=DEFAULT_HARDWARE_MONTHLY,
                        help="Monthly hardware amortization USD (default: $0)")
    parser.add_argument("--stdin", action="store_true",
                        help="Read article count from stdin")
    parser.add_argument("--json", action="store_true",
                        help="Output raw JSON instead of markdown")
    args = parser.parse_args(argv)

    articles = args.articles
    credits_per = args.scrape_credits

    if args.stdin:
        line = sys.stdin.readline().strip()
        if line.isdigit():
            articles = int(line)
        else:
            print(f"Error: invalid article count on stdin: {line!r}", file=sys.stderr)
            return 1

    fc_results = [firecrawl_cost(t, articles, credits_per) for t in FIRECRAWL_TIERS]
    loc = local_cost(args.watts, DEFAULT_RUNNING_HOURS_PER_DAY,
                     DEFAULT_DAYS_PER_MONTH, args.price_per_kwh,
                     args.hardware_monthly)

    annual_fc = sum(r["total_cost"] * 12 for r in fc_results if r["tier"] == "Hobby")
    annual_local = loc["total_cost"] * 12
    annual_savings = annual_fc - annual_local

    if args.json:
        print(json.dumps({
            "articles_per_month": articles,
            "credits_per_article": credits_per,
            "firecrawl": fc_results,
            "local": loc,
            "annual_hobby_cost": round(annual_fc, 2),
            "annual_local_cost": round(annual_local, 2),
            "annual_savings": round(annual_savings, 2),
        }, indent=2))
        return 0

    # ── Markdown output ──
    print(f"# Firecrawl vs Local Crawler Cost Estimate")
    print(f"")
    print(f"**Articles/month:** {articles} &nbsp;&nbsp; **Credits/article:** {credits_per} &nbsp;&nbsp; **Total credits needed:** {articles * credits_per}")
    print(f"")

    print("## Firecrawl Cloud Tiers")
    print("")
    headers = ["Tier", "Monthly Fee", "Plan Credits", "Credits Needed", "Fits?", "Extra Cost", "Total Cost"]
    rows = []
    for r in fc_results:
        rows.append([
            r["tier"],
            f"${r['monthly_fee']:.0f}",
            f"{r['plan_credits']:,}",
            f"{r['credits_needed']:,}",
            "✅ Yes" if r["fits_in_plan"] else "❌ Over",
            f"${r['extra_cost']:.2f}" if r["extra_credits"] > 0 else "—",
            f"${r['total_cost']:.2f}",
        ])
    print(markdown_table(headers, rows))
    print("")

    print("## Local Running Cost (Mac Studio M3 Ultra)")
    print("")
    print(f"| Component | Value |")
    print(f"| --- | --- |")
    print(f"| Power draw | {loc['watts']}W |")
    print(f"| Daily runtime | {loc['hours_per_day']:.0f}h |")
    print(f"| Monthly kWh | {loc['kwh_per_month']:.1f} kWh |")
    print(f"| Electricity rate | ${loc['price_per_kwh']}/kWh |")
    print(f"| Electricity cost | **${loc['electricity_cost']:.2f}/mo** |")
    if loc["hardware_monthly"] > 0:
        print(f"| Hardware amortization | ${loc['hardware_monthly']:.2f}/mo |")
    print(f"| **Total local** | **${loc['total_cost']:.2f}/mo** |")
    print("")

    print("## Annual Comparison")
    print("")
    print(f"| | Firecrawl Hobby | Local | Savings |")
    print(f"| --- | --- | --- | --- |")
    print(f"| Monthly | ${fc_results[1]['total_cost']:.2f} | ${loc['total_cost']:.2f} | ${fc_results[1]['total_cost'] - loc['total_cost']:.2f} |")
    print(f"| **Annual** | **${annual_fc:.0f}** | **${annual_local:.0f}** | **${annual_savings:.0f}** |")
    print("")
    print(f"> 💡 Local cost assumes the Mac Studio is already purchased. Hardware amortization is excluded by default.")
    print(f"> Use `--hardware-monthly` to include device payments in the comparison.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
