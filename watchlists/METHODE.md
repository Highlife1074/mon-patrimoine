# Watchlists swing — méthode et procédure d'actualisation

Deux watchlists TradingView, actualisées **deux fois par semaine (lundi et jeudi, 07:43 Paris)**.
Chaque valeur retenue reçoit **un signal d'entrée** (alerte TradingView) avec **1 SL et 3 TP**.

| Watchlist TradingView | id | Préfixe des alertes |
|---|---|---|
| `SWING – Suivi de tendance (HH/HL)` | 351707303 | `[TEND]` |
| `SWING – Retournements` | 351707304 | `[RET]` |

L'état courant (valeurs, niveaux, ids d'alertes) est dans [`etat.json`](etat.json).

Univers : actions US (NYSE/NASDAQ/AMEX, hors OTC) et Euronext Paris (éligibles PEA).
6 valeurs maximum par liste (3–4 US + 2–3 Paris de préférence).

---

## 1. Suivi de tendance — plus hauts de plus en plus hauts

### Filtres (screener TradingView, timeframe journalier)
- US : `market_cap_basic` ≥ 5 Md$ ; Paris : ≥ 2 Md€
- `RSI` entre 55 et 72 (momentum sans surchauffe)
- `ADX` ≥ 22 (tendance établie)
- `Perf.3M` ≥ +12 % et `Perf.1M` ≥ 0
- Structure : `close` > `SMA50` > `SMA200`, cours à moins de 5 % du plus haut 20 séances
- Vérification graphique (OHLCV 1D, 45 barres) : succession de plus hauts et plus bas croissants

### Niveaux
- **Entrée (alerte `cross_up`)** = plus haut des 20 dernières séances + 0,2 × ATR(14) → achat sur cassure d'un nouveau plus haut
- **SL** = max(plus bas 10 séances − 0,2 × ATR ; entrée − 2,5 × ATR)
- **R** = entrée − SL
- **TP1** = entrée + 1,5 R · **TP2** = entrée + 2,5 R · **TP3** = entrée + 4 R

## 2. Retournements

### Filtres
- US : `market_cap_basic` ≥ 5 Md$, `average_volume_10d_calc` ≥ 500 k ; Paris : ≥ 2 Md€
- `RSI` entre 30 et 48 (sortie de survente), `Perf.6M` ≤ −15 %
- Cours sous la `SMA200` mais qui tient un creux (cours à moins de ~8 % du plus bas 1 mois)
- Préférence : consensus analystes Buy/StrongBuy, RSI qui remonte (`RSI` > `RSI[1]`)

### Niveaux
- **Entrée (alerte `cross_up`)** = plus haut des 5 dernières séances + 0,2 × ATR → cassure du dernier plus haut décroissant = 1er plus haut croissant
- **SL** = max(plus bas 20 séances − 0,2 × ATR ; entrée − 3 × ATR)
- **TP1** = entrée + 1,5 R · **TP2** = entrée + 2,5 R · **TP3** = entrée + 4 R

## 3. Gestion d'une position (les deux listes)
- TP1 : vendre 1/3, remonter le SL au prix d'entrée (break-even)
- TP2 : vendre 1/3, remonter le SL à TP1
- TP3 : solde
- Risque recommandé : 0,5–1 % du capital par trade → taille = (capital × risque %) / (entrée − SL)
- ⚠ Résultats trimestriels dans les 10 jours : signalé dans l'alerte ; réduire la taille ou attendre la publication.

## 4. Alertes TradingView
- Alerte d'entrée : prix `cross_up` au niveau d'entrée, résolution 1D, désactivation après 1er déclenchement, push + popup.
  Nom : `[TEND] TICKER – ENTRÉE xx` / `[RET] TICKER – ENTRÉE xx` ; le message contient SL, TP1, TP2, TP3.
- Une fois l'entrée déclenchée, l'actualisation suivante crée les alertes de gestion :
  `[TEND|RET] TICKER – SL xx` (`cross_down`), `– TP1 xx`, `– TP2 xx`, `– TP3 xx` (`cross_up`).
- Seules des alertes de prix simples sont possibles via l'API (pas d'alertes indicateur ni webhook).

## 5. Procédure d'actualisation (lundi et jeudi)
1. Lire `etat.json`.
2. Lister les alertes TradingView préfixées `[TEND]` / `[RET]` :
   - **Entrée déclenchée** (`last_fire_time` non nul) → la valeur passe en statut `en_position` : créer les 4 alertes de gestion (SL, TP1, TP2, TP3), la garder dans la watchlist.
   - **Position en cours** → si SL ou TP3 déclenché : statut `cloturee`, supprimer les alertes restantes, retirer de la watchlist. Si TP1 touché : supprimer l'ancienne alerte SL et en créer une au prix d'entrée (break-even) ; si TP2 touché : SL à TP1.
   - **Entrée non déclenchée** → relancer les filtres. Si la valeur ne passe plus les filtres (ou setup invalidé : cours sous le SL prévu) : supprimer l'alerte, retirer de la watchlist. Sinon recalculer les niveaux ; si l'entrée change de plus de 0,5 %, supprimer et recréer l'alerte.
3. Compléter chaque liste jusqu'à 6 valeurs avec les meilleurs nouveaux candidats (tri `Perf.3M` pour la tendance, capitalisation + RSI qui remonte pour les retournements), créer leurs alertes d'entrée.
4. Mettre à jour `etat.json` (niveaux, ids d'alertes, statut, date) et ajouter une ligne dans `journal.md`.
5. Commit + push sur la branche `claude/lucid-darwin-mxinhp`.
