import re
from .retrieval import retrieve
from .text import tokens

def answer(store, query, top_k=5, min_overlap=1):
    hits = retrieve(store,query,top_k)
    q = set(tokens(query))
    evidence = []
    for hit in hits:
        sentences = re.split(r"(?<=[.!?])\s+",hit["text"])
        ranked = sorted(sentences,key=lambda s:len(q.intersection(tokens(s))),reverse=True)
        if ranked and len(q.intersection(tokens(ranked[0])))>=min_overlap:
            evidence.append({"claim":ranked[0].strip(),"citation":hit["passage_id"],"source":hit["source"],"title":hit["title"]})
    if not evidence:
        return {"query":query,"status":"abstain","answer":"Insufficient matching evidence in the indexed documents.","citations":[],"evidence":[]}
    evidence = evidence[:3]
    return {"query":query,"status":"evidence_found","answer":" ".join(f'{e["claim"]} [{e["citation"]}]' for e in evidence),"citations":[e["citation"] for e in evidence],"evidence":evidence}
