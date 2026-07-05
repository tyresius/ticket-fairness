"""Transaction-weighted systemic-fraud calibration.

Fraud rates are measured per secondary-market BUYER. Secondary transactions
concentrate on high-demand events, so the empirical blended rate must be
weighted by resale-transaction VOLUME, not event frequency. This is the correct
denominator for matching Ireland/Victoria/UK figures.
"""
import random
from gre_sim import simulate, Rule, BASELINE_SECONDARY_FRAUD_PENALTY

# Event-frequency distribution (most events not oversold)
DIST = {1.0: 0.45, 1.5: 0.20, 2.0: 0.13, 3.0: 0.09, 5.0: 0.07, 8.0: 0.04, 10.0: 0.02}
R = 200

def tw_fraud(cap, k):
    """Transaction-weighted fraud: weight systemic_fraud by resale volume."""
    num = den = 0.0
    for mul, w in DIST.items():
        random.seed(42)
        sf = vol = 0.0
        for _ in range(R):
            if cap is None:
                r = simulate(Rule("SQ", cap=None, plimit=8, dyn_mul=None), mul, dark_systemic_k=k)
                v = r["secondary_sold"]
                # uncapped fraud proxy = baseline secondary penalty per secondary buyer
                sf += BASELINE_SECONDARY_FRAUD_PENALTY * v
            else:
                r = simulate(Rule("B%d" % int(cap * 100), cap=cap, plimit=4, dyn_mul=None),
                             mul, dark_systemic_k=k)
                v = r["secondary_sold"] + r["dark_sold"]
                sf += r["systemic_fraud"] * v
            vol += v
        num += w * sf
        den += w * vol
    return num / den if den else 0.0

def main():
    lines = []
    lines.append("Transaction-weighted (per-resale-buyer) systemic fraud calibration")
    lines.append("Targets: Ireland 0%=13.6%, Victoria 10%=13.7%, UK uncapped=3.8%\n")
    lines.append("%5s | %8s | %8s" % ("K", "0pct", "10pct"))
    lines.append("-" * 28)
    best = None
    for k in [round(1.0 + 0.25 * i, 2) for i in range(17)]:
        f0 = tw_fraud(0.0, k)
        f10 = tw_fraud(0.10, k)
        sse = (f0 - 0.136) ** 2 + (f10 - 0.137) ** 2
        lines.append("%5.2f | %8.4f | %8.4f" % (k, f0, f10))
        if best is None or sse < best[1]:
            best = (k, sse, f0, f10)
    lines.append("\nBest K = %.2f  (0%%=%.4f, 10%%=%.4f, SSE=%.6f)"
                 % (best[0], best[2], best[3], best[1]))
    # UK uncapped check at best K
    uk = tw_fraud(None, best[0])
    lines.append("UK uncapped check at K=%.2f: modeled=%.4f  (target 0.038)" % (best[0], uk))
    with open("calibrate_tw.out", "w") as f:
        f.write("\n".join(lines) + "\n")
    print("done; best K =", best[0])

if __name__ == "__main__":
    main()
