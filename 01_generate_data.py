"""
Synthetic client-onboarding dataset for a simulated KYC (Know Your Customer) /
AML (Anti-Money Laundering) screening exercise. All names, countries and
watchlist entries are fictional; "high-risk jurisdictions" are placeholder codes.
"""
import json, random
import pandas as pd

rng = random.Random(5)
TODAY = pd.Timestamp("2026-10-01")

F = ["Aran", "Belmor", "Cavil", "Dorian", "Elka", "Farid", "Galen", "Hestia", "Ilan", "Jorvik", "Kestrel", "Lunara", "Maren", "Nolan", "Orsin"]
L = ["Ashdown", "Brightwell", "Carrow", "Dunleavy", "Eastgate", "Fenwick", "Gladstone", "Hartley", "Ingram", "Jessop", "Kingsley", "Lockwood"]
ORG = ["Trading", "Logistics", "Capital", "Holdings", "Enterprises", "Industries"]
COUNTRIES = ["IN", "GB", "DE", "FR", "NL", "IE", "SG", "XA", "XB"]   # XA / XB = placeholder high-risk jurisdictions
HIGH_RISK = {"XA", "XB"}

# Watchlist uses a distinct name pool so accidental matches are impossible
WF = ["Zorvan", "Quillon", "Vexley", "Yarrow", "Wrenfield", "Tavish"]
WL = ["Drummond", "Okonkwo-Reyes", "Valdermar", "Rasmussen-Ley", "Petrakis", "Halvorsen"]
watch = [f"{a} {b}" for a in WF for b in WL][:30]

N = 200
rows = []
for i in range(1, N + 1):
    ctype = rng.choice(["Individual", "Corporate"])
    name = f"{rng.choice(F)} {rng.choice(L)}" if ctype == "Individual" else f"{rng.choice(F)} {rng.choice(L)} {rng.choice(ORG)} Ltd"
    rows.append(dict(client_id=f"KYC{i:04d}", client_name=name, client_type=ctype, country=rng.choice(COUNTRIES),
                     id_doc_expiry=(TODAY + pd.Timedelta(days=rng.randint(120, 1500))).date(),
                     address_proof_date=(TODAY - pd.Timedelta(days=rng.randint(5, 80))).date(),
                     ubo_declared="Yes" if ctype == "Corporate" else "N/A",
                     source_of_funds="Provided", pep_declared=rng.choices(["No", "Yes"], [0.95, 0.05])[0]))
df = pd.DataFrame(rows)
# baseline PEPs (declared) are legitimate inputs to scoring, not "errors"

pool = list(range(N)); rng.shuffle(pool)
def take(n):
    out = pool[:n]; del pool[:n]; return out
truth = {}
def mark(k, why): truth.setdefault(df.loc[k, "client_id"], []).append(why)

for k in take(10):   # expired ID
    df.loc[k, "id_doc_expiry"] = (TODAY - pd.Timedelta(days=rng.randint(5, 200))).date(); mark(k, "ID document expired")
for k in take(10):   # stale address proof (> 90 days)
    df.loc[k, "address_proof_date"] = (TODAY - pd.Timedelta(days=rng.randint(95, 300))).date(); mark(k, "Address proof older than 90 days")
corp = [k for k in range(N) if df.loc[k, "client_type"] == "Corporate" and k in pool]
for k in corp[:8]:   # corporate with no UBO declaration
    pool.remove(k); df.loc[k, "ubo_declared"] = "No"; mark(k, "Corporate: UBO not declared")
for k in take(8):    # missing source of funds
    df.loc[k, "source_of_funds"] = ""; mark(k, "Source of funds missing")
for k in take(8):    # exact watchlist hit
    df.loc[k, "client_name"] = rng.choice(watch); df.loc[k, "client_type"] = "Individual"; df.loc[k, "ubo_declared"] = "N/A"; mark(k, "Watchlist potential match")
for k in take(8):    # near-match (reordered / typo)
    w = rng.choice(watch).split(); w[0] = w[0][:-1] + w[0][-1].lower() + "e" if rng.random() < .5 else w[0]
    nm = f"{w[1]}, {w[0]}" if rng.random() < .5 else " ".join(w)
    df.loc[k, "client_name"] = nm; df.loc[k, "client_type"] = "Individual"; df.loc[k, "ubo_declared"] = "N/A"; mark(k, "Watchlist potential match")

df.to_csv("data/onboarding_clients.csv", index=False)
pd.DataFrame({"watchlist_name": watch}).to_csv("data/watchlist_synthetic.csv", index=False)
json.dump(truth, open("data/_ground_truth_for_validation.json", "w"), indent=1)
print(f"clients: {len(df)} | clients with planted issues: {len(truth)} | watchlist entries: {len(watch)}")
