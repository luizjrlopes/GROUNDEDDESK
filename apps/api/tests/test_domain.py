import sys, unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from app.domain import can, can_transition, reciprocal_rank_fusion

class DomainTests(unittest.TestCase):
    def test_requester_cannot_reply_as_agent(self): self.assertFalse(can("requester","tickets:reply"))
    def test_agent_can_reply(self): self.assertTrue(can("agent","tickets:reply"))
    def test_state_machine(self):
        self.assertTrue(can_transition("Em atendimento","Resolvido"))
        self.assertFalse(can_transition("Fechado","Em atendimento"))
    def test_rrf_prefers_two_channels(self): self.assertGreater(reciprocal_rank_fusion(1,2),reciprocal_rank_fusion(1,None))
if __name__=="__main__": unittest.main()
