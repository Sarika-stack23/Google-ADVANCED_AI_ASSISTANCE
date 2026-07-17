"""
Evaluation Service — Offline LLM-as-judge pipeline for answering quality.
"""

import logging
from typing import Dict, List, Any
from backend.src.config import settings

logger = logging.getLogger("math_assistant.eval")

class EvaluationService:
    """Uses LLM-as-judge to evaluate generated math answers against reference solutions."""
    
    def __init__(self, judge_model: str = "gemini-2.5-flash"):
        self.judge_model = judge_model
        
    def evaluate_answer(self, question: str, generated_answer: str, reference_answer: str) -> Dict[str, Any]:
        """Ask the judge model to score the generated answer from 1 to 5."""
        from google import genai
        from google.genai import types
        
        api_key = settings.gemini_api_key
        if not api_key:
            return {"score": 0, "reasoning": "Missing API Key for evaluation"}
            
        client = genai.Client(api_key=api_key)
        
        prompt = f"""You are an expert mathematics teacher grading a student's answer.
        
        Question: {question}
        
        Reference/Correct Answer:
        {reference_answer}
        
        Student's Answer to evaluate:
        {generated_answer}
        
        Grade the student's answer from 1 to 5 based on:
        1. Accuracy: Is the final answer correct?
        2. Steps: Are the steps logical and mathematically sound?
        
        Format your response EXACTLY as follows:
        SCORE: [1-5]
        REASONING: [1-2 sentences explaining why]
        """
        
        config = types.GenerateContentConfig(
            temperature=0.1,
            max_output_tokens=150,
        )
        
        try:
            response = client.models.generate_content(
                model=self.judge_model,
                contents=prompt,
                config=config
            )
            
            text = response.text.strip()
            score = 0
            reasoning = text
            
            for line in text.split('\n'):
                if line.startswith("SCORE:"):
                    try:
                        score = int(line.replace("SCORE:", "").strip())
                    except:
                        pass
                elif line.startswith("REASONING:"):
                    reasoning = line.replace("REASONING:", "").strip()
                    
            return {"score": score, "reasoning": reasoning}
            
        except Exception as e:
            logger.error(f"Evaluation failed: {e}")
            return {"score": 0, "reasoning": f"Evaluation error: {e}"}
            
    def run_eval_pipeline(self, test_cases: List[Dict[str, str]]) -> Dict[str, Any]:
        """Run evaluation on a batch of test cases."""
        results = []
        total_score = 0
        
        for case in test_cases:
            res = self.evaluate_answer(
                question=case['question'],
                generated_answer=case['generated_answer'],
                reference_answer=case['reference_answer']
            )
            total_score += res['score']
            results.append({
                "question": case['question'],
                "score": res['score'],
                "reasoning": res['reasoning']
            })
            
        avg_score = total_score / len(test_cases) if test_cases else 0
        return {
            "average_score": avg_score,
            "total_evaluated": len(test_cases),
            "results": results
        }
