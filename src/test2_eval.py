#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Task B Evaluator
Computes Event-type Macro-F1, Sentiment Macro-F1, and Ticker Macro-F1
from two JSON files with the schema:
{
  "results": [
    {"event_type": "...", "sentiment": "pos|neu|neg", "ticker": "NVDA|null", "evidence": "..." },
    ...
  ]
}

Usage:
  python taskB_eval.py --gold gold.json --pred pred.json
Optional:
  --include-null-in-ticker (default: true)  Include `null` as a ticker class.
  --pretty  Pretty print per-class metrics.
"""

import argparse, json, sys
from typing import List, Dict, Any, Tuple, Optional

# ------------------------- Normalization helpers -------------------------

CANON_EVENTS = {
    'earnings','m&a_deal','regulatory_policy','investment_capex','product_tech',
    'labor_layoffs','ipo_listing','valuation_milestone','crypto_etf','macro_market','other'
}
EVENT_ALIASES = {
    'm&a': 'm&a_deal',
    'm_and_a': 'm&a_deal',
    'ma_deal': 'm&a_deal',
    'ipo': 'ipo_listing',
    'regulatory': 'regulatory_policy',
    'policy': 'regulatory_policy',
    'capex': 'investment_capex',
    'investment': 'investment_capex',
    'product': 'product_tech',
    'tech': 'product_tech',
    'valuation': 'valuation_milestone',
    'milestone': 'valuation_milestone',
    'crypto': 'crypto_etf',
    'etf': 'crypto_etf',
}
SENT_ALIASES = {
    'positive':'pos','neg':'neg','negative':'neg','neutral':'neu','n':'neu','p':'pos'
}

NULL_TICKER_SENTINEL = '∅'  # represent null/None tickers internally

def norm_event(x: Any) -> str:
    if x is None:
        return 'other'
    s = str(x).strip().lower()
    s = EVENT_ALIASES.get(s, s)
    if s not in CANON_EVENTS:
        s = 'other'
    return s

def norm_sentiment(x: Any) -> str:
    if x is None:
        return 'neu'
    s = str(x).strip().lower()
    s = SENT_ALIASES.get(s, s)
    if s not in {'pos','neu','neg'}:
        s = 'neu'
    return s

def norm_ticker(x: Any) -> str:
    if x is None:
        return NULL_TICKER_SENTINEL
    s = str(x).strip()
    if s == '' or s.lower() == 'null' or s.lower() == 'none':
        return NULL_TICKER_SENTINEL
    return s.upper()

# ------------------------- Metric computation -------------------------

def macro_f1(gold: List[str], pred: List[str], include_labels: Optional[List[str]]=None) -> Tuple[float, Dict[str, Dict[str, float]]]:
    """
    Compute Macro-F1 and per-class metrics. If include_labels is None,
    use unique labels appearing in gold (excluding labels with zero support).
    Returns: (macro_f1, details_per_class)
    details_per_class[label] = {'support': int, 'tp': int, 'fp': int, 'fn': int, 'precision': float, 'recall': float, 'f1': float}
    """
    assert len(gold) == len(pred), "gold and pred length mismatch"
    n = len(gold)
    if include_labels is None:
        labels = sorted(list({g for g in gold}))
    else:
        labels = include_labels

    details: Dict[str, Dict[str, float]] = {}
    f1s: List[float] = []
    for c in labels:
        tp = sum(1 for i in range(n) if gold[i] == c and pred[i] == c)
        fp = sum(1 for i in range(n) if gold[i] != c and pred[i] == c)
        fn = sum(1 for i in range(n) if gold[i] == c and pred[i] != c)
        support = sum(1 for i in range(n) if gold[i] == c)
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall    = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1        = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0

        details[c] = {
            'support': support, 'tp': tp, 'fp': fp, 'fn': fn,
            'precision': precision, 'recall': recall, 'f1': f1
        }
        if support > 0:
            f1s.append(f1)

    macro = sum(f1s)/len(f1s) if f1s else 0.0
    return macro, details

# ------------------------- IO & main -------------------------

def load_results(path: str) -> List[Dict[str, Any]]:
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    if not isinstance(data, dict) or 'results' not in data or not isinstance(data['results'], list):
        raise ValueError(f"File {path} must be a JSON object with a 'results' list")
    return data['results']

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Compute Macro-F1 for Event-type, Sentiment, and Ticker from Task B results.")
    parser.add_argument('--gold', required=True, help='Path to gold JSON file')
    parser.add_argument('--pred', required=True, help='Path to prediction JSON file')
    parser.add_argument('--include-null-in-ticker', type=str, default='true',
                        help="Include null tickers as a class in Ticker Macro-F1 (true/false). Default true.")
    parser.add_argument('--pretty', action='store_true', help='Pretty-print per-class metrics')
    args = parser.parse_args()

    include_null = str(args.include_null_in_ticker).lower() in {'1','true','t','yes','y'}

    gold_rows = load_results(args.gold)
    pred_rows = load_results(args.pred)
    if len(gold_rows) != len(pred_rows):
        print(f"[WARN] Different lengths: gold={len(gold_rows)} pred={len(pred_rows)}. Will align by index; extra items ignored.", file=sys.stderr)
    n = min(len(gold_rows), len(pred_rows))
    gold_rows = gold_rows[:n]
    pred_rows = pred_rows[:n]

    # Normalize labels
    gold_event = [norm_event(r.get('event_type')) for r in gold_rows]
    pred_event = [norm_event(r.get('event_type')) for r in pred_rows]

    gold_sent  = [norm_sentiment(r.get('sentiment')) for r in gold_rows]
    pred_sent  = [norm_sentiment(r.get('sentiment')) for r in pred_rows]

    gold_ticker = [norm_ticker(r.get('ticker')) for r in gold_rows]
    pred_ticker = [norm_ticker(r.get('ticker')) for r in pred_rows]

    # Event-type Macro-F1
    ev_macro, ev_details = macro_f1(gold_event, pred_event)

    # Sentiment Macro-F1
    sent_labels = sorted(list({g for g in gold_sent}))  # only classes with gold support
    sent_macro, sent_details = macro_f1(gold_sent, pred_sent, include_labels=sent_labels)

    # Ticker Macro-F1
    if not include_null:
        tick_labels = sorted(list({g for g in gold_ticker if g != NULL_TICKER_SENTINEL}))
    else:
        tick_labels = sorted(list({g for g in gold_ticker}))
    tick_macro, tick_details = macro_f1(gold_ticker, pred_ticker, include_labels=tick_labels)

    # Micro accuracies (companion stats)
    micro_event = sum(1 for i in range(n) if gold_event[i] == pred_event[i]) / n if n else 0.0
    micro_sent  = sum(1 for i in range(n) if gold_sent[i]  == pred_sent[i])  / n if n else 0.0
    micro_tick  = sum(1 for i in range(n) if gold_ticker[i]== pred_ticker[i]) / n if n else 0.0

    # Print summary
    def pct(x): return f"{x*100:.2f}%"
    print("== Task B Metrics ==")
    print(f"Samples: {n}")
    print(f"Event-type Macro-F1: {ev_macro:.3f} (micro-acc {pct(micro_event)})")
    print(f"Sentiment Macro-F1 : {sent_macro:.3f} (micro-acc {pct(micro_sent)})")
    print(f"Ticker Macro-F1    : {tick_macro:.3f} (micro-acc {pct(micro_tick)})")
    print("")

    if args.pretty:
        def show_table(title, details):
            print(f"-- {title} per-class --")
            hdr = f"{'class':30} {'supp':>5} {'tp':>4} {'fp':>4} {'fn':>4} {'P':>6} {'R':>6} {'F1':>6}"
            print(hdr)
            for c in sorted(details.keys(), key=lambda k: (-details[k]['support'], k)):
                d = details[c]
                print(f"{c:30} {d['support']:5d} {d['tp']:4d} {d['fp']:4d} {d['fn']:4d} {d['precision']:6.3f} {d['recall']:6.3f} {d['f1']:6.3f}")
            print("")
        show_table("Event-type", ev_details)
        show_table("Sentiment", sent_details)
        # map null sentinel for printing
        tick_print = { (k if k != NULL_TICKER_SENTINEL else 'null'): v for k,v in tick_details.items() }
        show_table("Ticker", tick_print)

if __name__ == "__main__":
    main()
