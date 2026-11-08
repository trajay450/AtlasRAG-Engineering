# Engineering design notes

## Why hybrid retrieval?
FTS5 BM25 captures lexical overlap, while hashed-vector cosine offers a deterministic secondary ranking. Reciprocal rank fusion combines rank positions rather than uncalibrated score scales. Hashing does not deliver the semantic quality of learned embeddings.

## Data model
Documents have deterministic IDs derived from source and title. Passages have ordinal IDs, and store their original text and normalized vectors. Re-ingesting a document replaces its passages and FTS entries in one transaction.

## Evaluation protocol
Use separate labeled query sets. Inspect recall, precision, reciprocal rank, and hit rate at a declared k. A test collection should contain both answerable and unanswerable questions. Run ablations across modes, and report failures, latency, and variance before making performance claims.

## Security boundaries
Localhost server has no authentication or access controls. Do not bind to public interfaces or load confidential documents. Do not confuse retrieved evidence with verified truth. Inputs are parameterized for SQL queries; rendered text is inserted with DOM textContent rather than innerHTML.
