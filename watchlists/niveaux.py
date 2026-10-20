"""Calcule entrée / SL / TP1-3 selon METHODE.md.

Usage : python3 niveaux.py tendance|retournement REF_HIGH REF_LOW ATR
  tendance     : REF_HIGH = plus haut 20 séances, REF_LOW = plus bas 10 séances
  retournement : REF_HIGH = plus haut 5 séances,  REF_LOW = plus bas 20 séances
"""
import json
import sys

CAP_ATR = {"tendance": 2.5, "retournement": 3.0}


def niveaux(kind, ref_high, ref_low, atr):
    entry = ref_high + 0.2 * atr
    sl = max(ref_low - 0.2 * atr, entry - CAP_ATR[kind] * atr)
    risk = entry - sl
    nd = 1 if entry >= 1000 else 2
    return {
        "entry": round(entry, nd),
        "sl": round(sl, nd),
        "tp1": round(entry + 1.5 * risk, nd),
        "tp2": round(entry + 2.5 * risk, nd),
        "tp3": round(entry + 4 * risk, nd),
        "risk_pct": round(100 * risk / entry, 1),
    }


if __name__ == "__main__":
    kind, high, low, atr = sys.argv[1], *map(float, sys.argv[2:5])
    print(json.dumps(niveaux(kind, high, low, atr)))
