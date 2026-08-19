import sys, unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from app.ai import LocalDeterministicProvider
class AITests(unittest.TestCase):
    def test_embedding_is_deterministic(self):
        p=LocalDeterministicProvider(); self.assertEqual(p.embed("vpn profile"),p.embed("vpn profile"))
    def test_no_evidence_refuses(self): self.assertEqual(LocalDeterministicProvider().answer("x",[]).groundedness,0)
if __name__=="__main__": unittest.main()
