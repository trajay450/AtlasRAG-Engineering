import argparse
import json
from pathlib import Path
from .store import Store
from .retrieval import retrieve
from .answer import answer
from .evaluate import benchmark

def main(argv=None):
    p=argparse.ArgumentParser(description="AtlasRAG local-first retrieval toolkit")
    p.add_argument("--db",default="atlasrag.sqlite3")
    sub=p.add_subparsers(dest="command",required=True)
    a=sub.add_parser("ingest");a.add_argument("path");a.add_argument("--title");a.add_argument("--chunk-size",type=int,default=110)
    s=sub.add_parser("search");s.add_argument("query");s.add_argument("--mode",choices=["hybrid","lexical","vector"],default="hybrid");s.add_argument("-k",type=int,default=5)
    q=sub.add_parser("answer");q.add_argument("query");q.add_argument("-k",type=int,default=5)
    e=sub.add_parser("evaluate");e.add_argument("cases");e.add_argument("--mode",choices=["hybrid","lexical","vector"],default="hybrid");e.add_argument("-k",type=int,default=5)
    h=sub.add_parser("serve");h.add_argument("--host",default="127.0.0.1");h.add_argument("--port",type=int,default=8765)
    args=p.parse_args(argv)
    if args.command=="serve":
        from .server import serve
        serve(args.db,args.host,args.port);return
    db=Store(args.db)
    try:
        if args.command=="ingest":
            path=Path(args.path)
            paths=sorted(path.glob("*.txt")) if path.is_dir() else [path]
            for file in paths:
                if file.suffix.lower() not in (".txt",".md"):
                    raise ValueError("Only .txt and .md supported")
                doc_id=db.add(args.title or file.stem,str(file),file.read_text(encoding="utf-8"),chunk_size=args.chunk_size)
                print(f"Indexed {file}: {doc_id}")
            return
        if args.command=="search": result=retrieve(db,args.query,args.k,args.mode)
        elif args.command=="answer": result=answer(db,args.query,args.k)
        else: result=benchmark(db,json.loads(Path(args.cases).read_text()),args.k,args.mode)
        print(json.dumps(result,indent=2))
    finally:
        db.close()
if __name__=="__main__":main()
