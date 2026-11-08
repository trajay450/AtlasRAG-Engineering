import unittest
import tempfile
from pathlib import Path
from atlasrag.store import Store
from atlasrag.retrieval import retrieve
from atlasrag.answer import answer
from atlasrag.evaluate import metrics,benchmark
class TestPipeline(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.db=Store(Path(self.tmp.name)/"test.db")
  self.a=self.db.add("Vision","vision.txt","Vision transformers use image patches and attention for classification.")
  self.b=self.db.add("Retrieval","rag.txt","Retrieval evaluation uses recall and reciprocal rank to assess search quality.")
 def tearDown(self):self.db.close();self.tmp.cleanup()
 def test_index(self):self.assertEqual(len(self.db.passages()),2)
 def test_search(self):self.assertEqual(retrieve(self.db,"image patches",1)[0]["document_id"],self.a)
 def test_modes(self):
  for mode in ("hybrid","lexical","vector"):self.assertTrue(retrieve(self.db,"retrieval evaluation",mode=mode))
 def test_answer(self):
  result=answer(self.db,"image patches");self.assertEqual(result["status"],"evidence_found");self.assertTrue(result["citations"])
 def test_abstain(self):self.assertEqual(answer(self.db,"zzzxxyy" )["status"],"abstain")
 def test_update(self):
  self.db.add("Vision","vision.txt","Completely new document text.");self.assertEqual(len(self.db.passages()),2)
 def test_metrics(self):self.assertEqual(metrics(["b","a"],["a"],2)["mrr"],0.5)
 def test_benchmark(self):self.assertEqual(benchmark(self.db,[{"query":"image patches","relevant_document_ids":[self.a]}],1)["aggregate"]["recall"],1)
 def test_validation(self):
  with self.assertRaises(ValueError):retrieve(self.db,"",1)
  with self.assertRaises(ValueError):self.db.add("","x","content")
