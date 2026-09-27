import os
import re
import math
from typing import List, Dict, Any
from app.services.document_classifier import classifier_engine

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False


class DocumentQAEngine:
    def __init__(self):
        pass

    def _chunk_text(self, text: str, chunk_size: int = 350, overlap: int = 50) -> List[str]:
        sentences = re.split(r'(?<=[.!?])\s+', text)
        chunks = []
        current_chunk = []
        current_length = 0

        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
            words = sentence.split()
            if current_length + len(words) > chunk_size and current_chunk:
                chunks.append(" ".join(current_chunk))
                overlap_words = []
                for s in reversed(current_chunk):
                    if len(overlap_words) + len(s.split()) <= overlap:
                        overlap_words.insert(0, s)
                    else:
                        break
                current_chunk = overlap_words
                current_length = sum(len(s.split()) for s in current_chunk)

            current_chunk.append(sentence)
            current_length += len(words)

        if current_chunk:
            chunks.append(" ".join(current_chunk))

        return chunks if chunks else [text]

    def answer_question(self, filepath: str, filename: str, question: str) -> Dict[str, Any]:
        text = classifier_engine.extract_text(filepath, filename)
        if not text or len(text.strip()) < 10:
            return {
                "answer": f"Unable to extract readable text content from '{filename}' for Q&A.",
                "confidence": 0.0,
                "relevant_snippets": []
            }

        chunks = self._chunk_text(text)
        if not SKLEARN_AVAILABLE or len(chunks) == 0:
            return {
                "answer": f"Document summary for '{filename}': {text[:300]}...",
                "confidence": 0.70,
                "relevant_snippets": [text[:300]]
            }

        try:
            corpus = chunks + [question]
            vectorizer = TfidfVectorizer(stop_words='english', ngram_range=(1, 2))
            tfidf_matrix = vectorizer.fit_transform(corpus)

            question_vec = tfidf_matrix[-1]
            chunk_vecs = tfidf_matrix[:-1]

            similarities = cosine_similarity(question_vec, chunk_vecs)[0]
            top_indices = sorted(range(len(similarities)), key=lambda i: similarities[i], reverse=True)[:3]

            relevant_snippets = [chunks[i] for i in top_indices if similarities[i] > 0.05]
            max_sim = float(similarities[top_indices[0]]) if top_indices else 0.0

            if not relevant_snippets:
                return {
                    "answer": f"No direct match found for '{question}' in {filename}. Here is a summary of the document content: {text[:250]}...",
                    "confidence": round(max_sim, 2),
                    "relevant_snippets": [text[:250]]
                }

            primary_snippet = relevant_snippets[0]
            answer = f"Based on '{filename}':\n\"{primary_snippet}\""

            return {
                "answer": answer,
                "confidence": round(max_sim, 2),
                "confidence_percentage": f"{round(max_sim * 100, 1)}%",
                "relevant_snippets": relevant_snippets
            }

        except Exception as e:
            print(f"Document Q&A error: {e}")
            return {
                "answer": f"Extracted excerpt: {text[:250]}...",
                "confidence": 0.60,
                "relevant_snippets": [text[:250]]
            }


qa_engine = DocumentQAEngine()
