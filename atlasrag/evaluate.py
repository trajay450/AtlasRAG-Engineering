from .retrieval import retrieve

def metrics(ranked_ids, relevant_ids, k):
    relevant = set(relevant_ids)
    if not relevant:
        raise ValueError("Relevant IDs cannot be empty")
    ranked = ranked_ids[:k]
    hits = [i for i,pid in enumerate(ranked,1) if pid in relevant]
    return {"recall":len(hits)/len(relevant),"precision":len(hits)/k,"mrr":1/hits[0] if hits else 0.0,"hit_rate":float(bool(hits))}

def benchmark(store, cases, k=5, mode="hybrid"):
    output=[]
    for case in cases:
        hits=retrieve(store,case["query"],top_k=k,mode=mode)
        # Relevant documents may contain multiple passages; document IDs are evaluated.
        ids=list(dict.fromkeys(h["document_id"] for h in hits))
        row={"query":case["query"],**metrics(ids,case["relevant_document_ids"],k)}
        output.append(row)
    avg={metric:sum(row[metric] for row in output)/len(output) for metric in ("recall","precision","mrr","hit_rate")} if output else {}
    return {"mode":mode,"k":k,"cases":output,"aggregate":avg}
