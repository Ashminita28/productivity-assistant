import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from deepeval.test_case import LLMTestCase
from deepeval.metrics import AnswerRelevancyMetric, FaithfulnessMetric
from deepeval import assert_test
from deepeval.models.base_model import DeepEvalBaseLLM
from backend.services.rag_service import rag_service
from backend.agents.llm_factory import get_llm

class DeepEvalCustomLLM(DeepEvalBaseLLM):
    def __init__(self):
        self.model = get_llm(task_type="smart", temperature=0)

    def load_model(self):
        return self.model

    def generate(self, prompt: str) -> str:
        return self.model.invoke(prompt).content

    async def a_generate(self, prompt: str) -> str:
        return (await self.model.ainvoke(prompt)).content

    def get_model_name(self):
        return "Custom Local LLM"

def test_rag_agent_answer():
  
    input_question = "What is the primary topic of the document?"
    

    retrieved_context_raw = rag_service.query_knowledge_base(input_question, k=3)
    

    retrieval_context = [retrieved_context_raw] if retrieved_context_raw else ["No context found."]
    

    actual_output = "The primary topic is currently unknown because we are simulating this response. In production, this would be the LLM's answer."

    
    test_case = LLMTestCase(
        input=input_question,
        actual_output=actual_output,
        retrieval_context=retrieval_context
    )
    
  
    evaluator_llm = DeepEvalCustomLLM()
    
    answer_relevancy_metric = AnswerRelevancyMetric(threshold=0.5, model=evaluator_llm)
    faithfulness_metric = FaithfulnessMetric(threshold=0.5, model=evaluator_llm)

 
    assert_test(test_case, [answer_relevancy_metric, faithfulness_metric])
