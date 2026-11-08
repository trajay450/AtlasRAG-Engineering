import json
from collections import Counter
from .text import tokens, hashed_vector, cosine

def retrieve(store, query, top_k=5, mode="hybrid"):
    if not query.strip():
        raise ValueError("Query must not be empty")
    if top_k < 1 or top_k > 100:
        raise ValueError("top_k must be 1..100")
    if mode not in ("hybrid","lexical","vector"):
        raise ValueError("Invalid retrieval mode")
    rows = store.passages()
    qvec = hashed_vector(query)
    qterms = Counter(tokens(query))
    lexical = {}
    if store.fts:
        lexical = {pid: -score for pid,score in store.fts_ids(query)}
    candidates = []
    for row in rows:
        terms = Counter(tokens(row["text"]))
        lex = lexical.get(row["id"], sum(min(n,terms[t]) for t,n in qterms.items()))
        sem = cosine(qvec,json.loads(row["vector"]))
        candidates.append((row,lex,sem))
    # Reciprocal rank fusion prevents incomparable BM25 and cosine scales.
    lex_order = {r[0]["id"]:i for i,r in enumerate(sorted(candidates,key=lambda r:(-r[1],r[0]["id"]))) if r[1]>0}
    sem_order = {r[0]["id"]:i for i,r in enumerate(sorted(candidates,key=lambda r:(-r[2],r[0]["id"]))) if r[2]>0}
    results = []
    for row,lex,sem in candidates:
        if mode == "lexical": score=lex
        elif mode == "vector": score=sem
        else: score = (1/(60+lex_order[row["id"]]+1) if row["id"] in lex_order else 0) + (1/(60+sem_order[row["id"]]+1) if row["id"] in sem_order else 0)
        if score <= 0:
            continue
        results.append({"passage_id":row["id"],"document_id":row["document_id"],"title":row["title"],"source":row["source"],"text":row["text"],"score":round(score,8)})
    return sorted(results,key=lambda r:(-r["score"],r["passage_id"]))[:top_k]
