from ragas.dataset_schema import MultiTurnSample
from ragas.metrics import AgentGoalAccuracyWithReference
from ragas.llms import LangchainLLMWrapper
from ragas.integrations.langgraph import convert_to_ragas_messages
from src.utils.llm import grader_model

class Evaluator:
    def __init__(self):
        self.evaluator_llm = LangchainLLMWrapper(grader_model)
        self.scorer = AgentGoalAccuracyWithReference()

    async def evaluate_AgentGoalAccuracy(self, user_query: str, result):
        ragas_trace = convert_to_ragas_messages(
            result["messages"]
        )
        sample = MultiTurnSample(
            user_input=ragas_trace,
            reference=user_query,
        )

        self.scorer.llm = self.evaluator_llm
        score = await self.scorer.multi_turn_ascore(sample)
        print("-------------------------- ******************* --------------------------")
        print("score:", score)
        print("-------------------------- ******************* --------------------------")
        return score