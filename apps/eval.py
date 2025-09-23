#!/usr/bin/env python3
"""
Evaluation harness for Vectorpenter
Test retrieval quality with gold Q&A pairs
"""

import json
import time
from pathlib import Path
from typing import List, Dict, Any
from dataclasses import dataclass, asdict
import click
from core.logging import logger
from index.embedder import embed_texts
from rag.retriever import vector_search
from rag.context_builder import hydrate_matches, build_context
from rag.generator import answer
from search.hybrid import hybrid_search, is_available as typesense_available

@dataclass
class EvalQuestion:
    """Evaluation question with expected answers"""
    question: str
    expected_chunks: List[str]  # Expected chunk IDs
    expected_answer_keywords: List[str]  # Keywords that should appear in answer
    category: str = "general"

@dataclass
class EvalResult:
    """Evaluation result for a single question"""
    question: str
    retrieved_chunks: List[str]
    answer: str
    retrieval_precision: float
    retrieval_recall: float
    answer_keyword_score: float
    response_time_ms: float

def load_eval_dataset(eval_file: Path) -> List[EvalQuestion]:
    """Load evaluation dataset from JSON file"""
    try:
        with open(eval_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        questions = []
        for item in data:
            questions.append(EvalQuestion(
                question=item['question'],
                expected_chunks=item.get('expected_chunks', []),
                expected_answer_keywords=item.get('expected_answer_keywords', []),
                category=item.get('category', 'general')
            ))
        
        return questions
        
    except Exception as e:
        logger.error(f"Failed to load evaluation dataset: {e}")
        return []

def evaluate_retrieval(question: str, expected_chunks: List[str], 
                      hybrid: bool = False, k: int = 12) -> Dict[str, Any]:
    """Evaluate retrieval quality for a single question"""
    start_time = time.time()
    
    try:
        # Embed query
        vec = embed_texts([question])[0]
        
        # Search
        if hybrid and typesense_available():
            matches, best_score = hybrid_search(question, vec, top_k=k)
        else:
            matches, best_score = vector_search(vec, top_k=k)
        
        # Get chunk IDs
        retrieved_chunk_ids = [m['id'] for m in matches]
        
        # Calculate precision and recall
        expected_set = set(expected_chunks)
        retrieved_set = set(retrieved_chunk_ids)
        
        if len(retrieved_set) > 0:
            precision = len(expected_set & retrieved_set) / len(retrieved_set)
        else:
            precision = 0.0
        
        if len(expected_set) > 0:
            recall = len(expected_set & retrieved_set) / len(expected_set)
        else:
            recall = 1.0  # No expected chunks means perfect recall
        
        response_time = (time.time() - start_time) * 1000
        
        return {
            "retrieved_chunks": retrieved_chunk_ids,
            "precision": precision,
            "recall": recall,
            "best_score": best_score,
            "response_time_ms": response_time,
            "success": True
        }
        
    except Exception as e:
        response_time = (time.time() - start_time) * 1000
        logger.error(f"Retrieval evaluation failed: {e}")
        return {
            "retrieved_chunks": [],
            "precision": 0.0,
            "recall": 0.0,
            "best_score": 0.0,
            "response_time_ms": response_time,
            "success": False,
            "error": str(e)
        }

def evaluate_answer_quality(question: str, answer_text: str, 
                           expected_keywords: List[str]) -> float:
    """Evaluate answer quality based on keyword presence"""
    if not expected_keywords:
        return 1.0  # No keywords to check
    
    answer_lower = answer_text.lower()
    found_keywords = 0
    
    for keyword in expected_keywords:
        if keyword.lower() in answer_lower:
            found_keywords += 1
    
    return found_keywords / len(expected_keywords)

def run_evaluation(eval_file: Path, hybrid: bool = False, k: int = 12) -> Dict[str, Any]:
    """Run complete evaluation"""
    questions = load_eval_dataset(eval_file)
    
    if not questions:
        return {"error": "No evaluation questions loaded"}
    
    results = []
    total_precision = 0.0
    total_recall = 0.0
    total_answer_score = 0.0
    total_response_time = 0.0
    successful_queries = 0
    
    logger.info(f"Starting evaluation with {len(questions)} questions")
    
    for i, eq in enumerate(questions, 1):
        logger.info(f"Evaluating question {i}/{len(questions)}: {eq.question[:50]}...")
        
        # Evaluate retrieval
        retrieval_result = evaluate_retrieval(eq.question, eq.expected_chunks, hybrid, k)
        
        if not retrieval_result['success']:
            logger.warning(f"Question {i} failed: {retrieval_result.get('error')}")
            continue
        
        # Generate answer if retrieval successful
        try:
            snippets = hydrate_matches([
                {"id": chunk_id, "score": 0.8} 
                for chunk_id in retrieval_result['retrieved_chunks'][:k]
            ])
            context_pack = build_context(snippets)
            answer_text = answer(eq.question, context_pack)
            
            # Evaluate answer quality
            answer_score = evaluate_answer_quality(eq.question, answer_text, eq.expected_answer_keywords)
            
        except Exception as e:
            logger.warning(f"Answer generation failed for question {i}: {e}")
            answer_text = ""
            answer_score = 0.0
        
        # Record result
        result = EvalResult(
            question=eq.question,
            retrieved_chunks=retrieval_result['retrieved_chunks'],
            answer=answer_text,
            retrieval_precision=retrieval_result['precision'],
            retrieval_recall=retrieval_result['recall'],
            answer_keyword_score=answer_score,
            response_time_ms=retrieval_result['response_time_ms']
        )
        
        results.append(result)
        
        # Accumulate metrics
        total_precision += retrieval_result['precision']
        total_recall += retrieval_result['recall']
        total_answer_score += answer_score
        total_response_time += retrieval_result['response_time_ms']
        successful_queries += 1
    
    if successful_queries == 0:
        return {"error": "No successful evaluations"}
    
    # Calculate averages
    avg_precision = total_precision / successful_queries
    avg_recall = total_recall / successful_queries
    avg_answer_score = total_answer_score / successful_queries
    avg_response_time = total_response_time / successful_queries
    
    # Calculate F1 score
    f1_score = (2 * avg_precision * avg_recall) / (avg_precision + avg_recall) if (avg_precision + avg_recall) > 0 else 0.0
    
    return {
        "total_questions": len(questions),
        "successful_queries": successful_queries,
        "avg_precision": avg_precision,
        "avg_recall": avg_recall,
        "f1_score": f1_score,
        "avg_answer_keyword_score": avg_answer_score,
        "avg_response_time_ms": avg_response_time,
        "search_type": "hybrid" if hybrid else "vector",
        "k": k,
        "results": [asdict(r) for r in results]
    }

@click.command()
@click.option('--eval-file', default='data/eval/questions.json', help='Path to evaluation dataset')
@click.option('--hybrid', is_flag=True, help='Use hybrid search')
@click.option('--k', default=12, help='Number of results to retrieve')
@click.option('--output', help='Output file for detailed results')
def evaluate(eval_file: str, hybrid: bool, k: int, output: str):
    """Run evaluation on the dataset"""
    eval_path = Path(eval_file)
    
    if not eval_path.exists():
        click.echo(f"❌ Evaluation file not found: {eval_path}")
        click.echo("💡 Create evaluation dataset in data/eval/questions.json")
        return
    
    click.echo(f"🧪 Running evaluation: {eval_file}")
    click.echo(f"   Search type: {'Hybrid' if hybrid else 'Vector'}")
    click.echo(f"   K: {k}")
    
    # Run evaluation
    results = run_evaluation(eval_path, hybrid, k)
    
    if "error" in results:
        click.echo(f"❌ Evaluation failed: {results['error']}")
        return
    
    # Display results
    click.echo("\n📊 EVALUATION RESULTS")
    click.echo("=" * 50)
    click.echo(f"Questions: {results['total_questions']}")
    click.echo(f"Successful: {results['successful_queries']}")
    click.echo(f"Precision: {results['avg_precision']:.3f}")
    click.echo(f"Recall: {results['avg_recall']:.3f}")
    click.echo(f"F1 Score: {results['f1_score']:.3f}")
    click.echo(f"Answer Quality: {results['avg_answer_keyword_score']:.3f}")
    click.echo(f"Avg Response Time: {results['avg_response_time_ms']:.1f}ms")
    
    # Save detailed results if requested
    if output:
        output_path = Path(output)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        click.echo(f"💾 Detailed results saved to: {output_path}")

if __name__ == "__main__":
    evaluate()
