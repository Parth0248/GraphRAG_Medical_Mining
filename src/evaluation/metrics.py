"""Evaluation Metrics Framework for GraphRAG Medical Mining

Implements comprehensive evaluation metrics for:
-  Retrieval quality (Recall@k, MRR, NDCG)
- Entity extraction performance (F1, precision, recall)
- Answer generation quality (ROUGE-L, BERTScore)
- System performance (latency, throughput)

Integrates with TensorBoard for visualization.
"""

import numpy as np
from typing import List, Dict, Tuple, Set
from collections import defaultdict
import json
from datetime import datetime
from torch.utils.tensorboard import SummaryWriter


class RetrievalMetrics:
    """Metrics for document retrieval evaluation"""
    
    @staticmethod
    def recall_at_k(retrieved_docs: List[str], relevant_docs: Set[str], k: int) -> float:
        """
        Calculate Recall@k
        
        Args:
            retrieved_docs: List of retrieved document IDs (ranked)
            relevant_docs: Set of ground truth relevant document IDs
            k: Cutoff rank
            
        Returns:
            Recall@k score (0.0 to 1.0)
        """
        if not relevant_docs:
            return 0.0
        
        retrieved_at_k = set(retrieved_docs[:k])
        hits = len(retrieved_at_k & relevant_docs)
        return hits / len(relevant_docs)
    
    @staticmethod
    def precision_at_k(retrieved_docs: List[str], relevant_docs: Set[str], k: int) -> float:
        """Calculate Precision@k"""
        if k == 0:
            return 0.0
        
        retrieved_at_k = set(retrieved_docs[:k])
        hits = len(retrieved_at_k & relevant_docs)
        return hits / k
    
    @staticmethod
    def mean_reciprocal_rank(rankings: List[List[str]], relevant_docs_list: List[Set[str]]) -> float:
        """
        Calculate Mean Reciprocal Rank (MRR)
        
        Args:
            rankings: List of ranked document lists (one per query)
            relevant_docs_list: List of relevant document sets (one per query)
            
        Returns:
            MRR score
        """
        reciprocal_ranks = []
        
        for retrieved, relevant in zip(rankings, relevant_docs_list):
            for rank, doc_id in enumerate(retrieved, 1):
                if doc_id in relevant:
                    reciprocal_ranks.append(1.0 / rank)
                    break
            else:
                reciprocal_ranks.append(0.0)  # No relevant document found
        
        return np.mean(reciprocal_ranks) if reciprocal_ranks else 0.0
    
    @staticmethod
    def ndcg_at_k(retrieved: List[str], relevance_scores: Dict[str, float], k: int) -> float:
        """
        Calculate Normalized Discounted Cumulative Gain @k
        
        Args:
            retrieved: List of retrieved document IDs (ranked)
            relevance_scores: Dict mapping doc_id to relevance score (0-3)
            k: Cutoff rank
            
        Returns:
            NDCG@k score
        """
        def dcg(scores):
            return np.sum([
                (2**score - 1) / np.log2(idx + 2)
                for idx, score in enumerate(scores)
            ])
        
       # Get relevance scores for retrieved docs
        retrieved_scores = [relevance_scores.get(doc_id, 0.0) for doc_id in retrieved[:k]]
        
        if sum(retrieved_scores) == 0:
            return 0.0
        
        # Calculate DCG
        dcg_score = dcg(retrieved_scores)
        
        # Calculate ideal DCG (best possible ranking)
        ideal_scores = sorted(relevance_scores.values(), reverse=True)[:k]
        idcg_score = dcg(ideal_scores)
        
        if idcg_score == 0:
            return 0.0
        
        return dcg_score / idcg_score


class EntityMetrics:
    """Metrics for entity extraction evaluation"""
    
    @staticmethod
    def entity_f1(predicted: List[Dict], gold: List[Dict]) -> Dict[str, float]:
        """
        Calculate F1, Precision, Recall for entity extraction
        
        Args:
            predicted: List of predicted entities [{'text': str, 'label': str, 'start': int, 'end': int}]
            gold: List of gold standard entities (same format)
            
        Returns:
            Dict with 'precision', 'recall', 'f1' scores
        """
        # Convert to sets of (text, label, start, end) tuples for exact match
        pred_set = {(e['text'].lower(), e['label'], e['start'], e['end']) for e in predicted}
        gold_set = {(e['text'].lower(), e['label'], e['start'], e['end']) for e in gold}
        
        true_positives = len(pred_set & gold_set)
        false_positives = len(pred_set - gold_set)
        false_negatives = len(gold_set - pred_set)
        
        precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0.0
        recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0.0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0
        
        return {
            'precision': precision,
            'recall': recall,
            'f1': f1,
            'tp': true_positives,
            'fp': false_positives,
            'fn': false_negatives
        }
    
    @staticmethod
    def entity_f1_by_type(predicted: List[Dict], gold: List[Dict]) -> Dict[str, Dict[str, float]]:
        """Calculate F1 scores separately for each entity type"""
        # Group by entity type
        types = set([e['label'] for e in predicted + gold])
        
        results = {}
        for entity_type in types:
            pred_type = [e for e in predicted if e['label'] == entity_type]
            gold_type = [e for e in gold if e['label'] == entity_type]
            results[entity_type] = EntityMetrics.entity_f1(pred_type, gold_type)
        
        return results


class AnswerQualityMetrics:
    """Metrics for generated answer quality"""
    
    @staticmethod
    def rouge_l(generated: str, reference: str) -> float:
        """
        Calculate ROUGE-L score (Longest Common Subsequence)
        
        Args:
            generated: Generated answer
            reference: Reference answer
            
        Returns:
            ROUGE-L F1 score
        """
        try:
            from rouge_score import rouge_scorer
            scorer = rouge_scorer.RougeScorer(['rougeL'], use_stemmer=True)
            scores = scorer.score(reference, generated)
            return scores['rougeL'].fmeasure
        except ImportError:
            print("Warning: rouge-score not installed. Install with: pip install rouge-score")
            return 0.0
    
    @staticmethod
    def bertscore(generated: List[str], references: List[str]) -> Dict[str, float]:
        """
        Calculate BERTScore for semantic similarity
        
        Args:
            generated: List of generated answers
            references: List of reference answers
            
        Returns:
            Dict with 'precision', 'recall', 'f1' scores
        """
        try:
            from bert_score import score
            P, R, F1 = score(generated, references, lang='en', verbose=False)
            return {
                'precision': P.mean().item(),
                'recall': R.mean().item(),
                'f1': F1.mean().item()
            }
        except ImportError:
            print("Warning: bert-score not installed. Install with: pip install bert-score")
            return {'precision': 0.0, 'recall': 0.0, 'f1': 0.0}


class TensorBoardLogger:
    """TensorBoard integration for experiment tracking"""
    
    def __init__(self, log_dir='runs/graphrag_medical'):
        """Initialize TensorBoard writer"""
        self.writer = SummaryWriter(log_dir)
        self.step = 0
    
    def log_retrieval_metrics(self, metrics: Dict[str, float], step: int = None):
        """Log retrieval metrics to TensorBoard"""
        step = step if step is not None else self.step
        
        for metric_name, value in metrics.items():
            self.writer.add_scalar(f'Retrieval/{metric_name}', value, step)
    
    def log_entity_metrics(self, metrics: Dict[str, Dict[str, float]], step: int = None):
        """Log entity extraction metrics by type"""
        step = step if step is not None else self.step
        
        for entity_type, scores in metrics.items():
            for metric_name, value in scores.items():
                self.writer.add_scalar(f'Entity/{entity_type}/{metric_name}', value, step)
    
    def log_answer_quality(self, metrics: Dict[str, float], step: int = None):
        """Log answer generation quality metrics"""
        step = step if step is not None else self.step
        
        for metric_name, value in metrics.items():
            self.writer.add_scalar(f'Answer/{metric_name}', value, step)
    
    def log_latency(self, latencies: List[float], step: int = None):
        """Log response latency distribution"""
        step = step if step is not None else self.step
        
        self.writer.add_histogram('Performance/Latency', np.array(latencies), step)
        self.writer.add_scalar('Performance/Latency_Mean', np.mean(latencies), step)
        self.writer.add_scalar('Performance/Latency_P95', np.percentile(latencies, 95), step)
        self.writer.add_scalar('Performance/Latency_P99', np.percentile(latencies, 99), step)
    
    def log_confusion_matrix(self, confusion_matrix: np.ndarray, class_names: List[str], step: int = None):
        """Log confusion matrix as image"""
        import matplotlib.pyplot as plt
        import io
        from PIL import Image
        
        step = step if step is not None else self.step
        
        fig, ax = plt.subplots(figsize=(10, 8))
        im = ax.imshow(confusion_matrix, cmap='Blues')
        
        ax.set_xticks(np.arange(len(class_names)))
        ax.set_yticks(np.arange(len(class_names)))
        ax.set_xticklabels(class_names)
        ax.set_yticklabels(class_names)
        
        plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")
        
        # Annotate cells
        for i in range(len(class_names)):
            for j in range(len(class_names)):
                text = ax.text(j, i, confusion_matrix[i, j],
                             ha="center", va="center", color="black")
        
        ax.set_title("Entity Type Confusion Matrix")
        fig.tight_layout()
        
        # Convert to image
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        image = Image.open(buf)
        
        self.writer.add_image('Entity/ConfusionMatrix', np.array(image), step, dataformats='HWC')
        plt.close()
    
    def increment_step(self):
        """Increment global step counter"""
        self.step += 1
    
    def close(self):
        """Close TensorBoard writer"""
        self.writer.close()


class EvaluationRunner:
    """Main evaluation runner that coordinates all metrics"""
    
    def __init__(self, use_tensorboard=True):
        """Initialize evaluation runner"""
        self.use_tensorboard = use_tensorboard
        if use_tensorboard:
            self.tb_logger = TensorBoardLogger()
        
        self.results = {
            'retrieval': [],
            'entity': [],
            'answer': [],
            'latency': []
        }
    
    def evaluate_retrieval(self, retrieved_docs_list: List[List[str]], 
                          relevant_docs_list: List[Set[str]],
                          k_values: List[int] = [5, 10, 20]) -> Dict[str, float]:
        """
        Evaluate retrieval performance
        
        Args:
            retrieved_docs_list: List of retrieved doc rankings (one per query)
            relevant_docs_list: List of relevant doc sets (one per query)
            k_values: List of k values for Recall@k
            
        Returns:
            Dict of metric scores
        """
        metrics = {}
        
        # Recall@k
        for k in k_values:
            recalls = [
                RetrievalMetrics.recall_at_k(retrieved, relevant, k)
                for retrieved, relevant in zip(retrieved_docs_list, relevant_docs_list)
            ]
            metrics[f'Recall@{k}'] = np.mean(recalls)
        
        # MRR
        metrics['MRR'] = RetrievalMetrics.mean_reciprocal_rank(
            retrieved_docs_list, relevant_docs_list
        )
        
        self.results['retrieval'].append(metrics)
        
        if self.use_tensorboard:
            self.tb_logger.log_retrieval_metrics(metrics)
            self.tb_logger.increment_step()
        
        return metrics
    
    def save_results(self, output_file='results/evaluation_results.json'):
        """Save all evaluation results to JSON"""
        import os
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        results_with_timestamp = {
            'timestamp': datetime.now().isoformat(),
            'metrics': self.results
        }
        
        with open(output_file, 'w') as f:
            json.dump(results_with_timestamp, f, indent=2)
        
        print(f"✅ Evaluation results saved to: {output_file}")
    
    def close(self):
        """Cleanup"""
        if self.use_tensorboard:
            self.tb_logger.close()


if __name__ == "__main__":
    # Example usage
    print("=" * 70)
    print("      GraphRAG Medical Mining - Evaluation Framework")
    print("=" * 70)
    
    # Test retrieval metrics
    print("\n📊 Testing Retrieval Metrics...")
    
    retrieved = ['doc1', 'doc2', 'doc3', 'doc4', 'doc5']
    relevant = {'doc2', 'doc4', 'doc7'}
    
    recall_5 = RetrievalMetrics.recall_at_k(retrieved, relevant, k=5)
    precision_5 = RetrievalMetrics.precision_at_k(retrieved, relevant, k=5)
    
    print(f"   Recall@5: {recall_5:.3f}")
    print(f"   Precision@5: {precision_5:.3f}")
    
    # Test entity metrics
    print("\n📊 Testing Entity Metrics...")
    
    predicted_entities = [
        {'text': 'diabetes', 'label': 'Disease', 'start': 0, 'end': 8},
        {'text': 'insulin', 'label': 'Drug', 'start': 20, 'end': 27}
    ]
    
    gold_entities = [
        {'text': 'diabetes', 'label': 'Disease', 'start': 0, 'end': 8},
        {'text': 'insulin', 'label': 'Drug', 'start': 20, 'end': 27},
        {'text': 'metformin', 'label': 'Drug', 'start': 40, 'end': 49}
    ]
    
    entity_scores = EntityMetrics.entity_f1(predicted_entities, gold_entities)
    print(f"   F1: {entity_scores['f1']:.3f}")
    print(f"   Precision: {entity_scores['precision']:.3f}")
    print(f"   Recall: {entity_scores['recall']:.3f}")
    
    print("\n✅ Evaluation framework ready!")
    print("\n   To use in your code:")
    print("   >>> from src.evaluation.metrics import EvaluationRunner")
    print("   >>> runner = EvaluationRunner(use_tensorboard=True)")
    print("   >>> metrics = runner.evaluate_retrieval(...)")
    print("   >>> runner.save_results()")
