import unittest
from atlasrag.text import chunks, hashed_vector, cosine
class TestText(unittest.TestCase):
 def test_chunks(self):self.assertEqual(list(chunks("a b c d e",3,1)),["a b c","c d e"])
 def test_bad_chunks(self):
  with self.assertRaises(ValueError):list(chunks("a b",2,2))
 def test_vector(self):self.assertAlmostEqual(cosine(hashed_vector("image model"),hashed_vector("image model")),1)
 def test_empty(self):self.assertEqual(sum(hashed_vector("")),0)
