import os
import json
import re
import math
from typing import List, Dict, Any, Tuple, Optional
from app.core.config import DATA_DIR

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.linear_model import SGDClassifier
    from sklearn.pipeline import Pipeline
    import numpy as np
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

try:
    import pypdf
    PYPDF_AVAILABLE = True
except ImportError:
    PYPDF_AVAILABLE = False

try:
    import docx
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False


METADATA_FILE = os.path.join(DATA_DIR, "file_metadata.json")


def load_all_metadata() -> Dict[str, Dict[str, Any]]:
    if os.path.exists(METADATA_FILE):
        try:
            with open(METADATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def save_all_metadata(metadata: Dict[str, Dict[str, Any]]):
    try:
        with open(METADATA_FILE, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Error saving metadata: {e}")


def get_file_metadata(filename: str) -> Dict[str, Any]:
    all_data = load_all_metadata()
    return all_data.get(filename, {
        "tags": [],
        "predicted_category": "General",
        "confidence": 0.0,
        "summary": "",
        "biometric_protected": False,
        "is_ghost_share": False,
        "custom_tags": []
    })


def update_file_metadata(filename: str, updates: Dict[str, Any]):
    all_data = load_all_metadata()
    if filename not in all_data:
        all_data[filename] = {
            "tags": [],
            "predicted_category": "General",
            "confidence": 0.0,
            "summary": "",
            "biometric_protected": False,
            "is_ghost_share": False,
            "custom_tags": []
        }
    all_data[filename].update(updates)
    save_all_metadata(all_data)


def delete_file_metadata(filename: str):
    all_data = load_all_metadata()
    if filename in all_data:
        del all_data[filename]
        save_all_metadata(all_data)


class DocumentClassifierEngine:
    def __init__(self):
        self.model: Optional[Pipeline] = None
        self.categories = [
            "Finance & Business",
            "Legal & Contracts",
            "Technology & Code",
            "Medical & Healthcare",
            "Academic & Research",
            "Marketing & Sales",
            "Personal & HR"
        ]
        self._initialize_and_train_model()

    def _get_training_corpus(self) -> Tuple[List[str], List[str]]:
        corpus = [
            ("Invoice payment statement tax return balance sheet revenue quarter profit loss accounting audit quarterly financial result bank statement credit receipt transaction fiscal budget expenditure cash flow interest rate equity investment assets liability", "Finance & Business"),
            ("Quarterly financial report Q1 Q2 Q3 Q4 revenue growth gross profit margin EBITDA operating expenses cash flow statement balance sheet audit report tax withholding invoice total due billing", "Finance & Business"),
            ("Billing receipt invoice number total amount paid payment due date tax identification number bank account wire transfer pricing cost expenditure budget forecast ledger balance", "Finance & Business"),
            ("Stock portfolio market valuation dividend capital gains investment fund asset management fiscal policy commercial banking transaction interest yield inflation hedge bond yield", "Finance & Business"),
            ("Agreement contract terms conditions NDA non-disclosure agreement liability privacy policy clause breach copyright trademark patent jurisdiction litigation dispute governing law indemnification intellectual property signatory license agreement binding arbitration", "Legal & Contracts"),
            ("Non disclosure agreement confidential information party disclosing receiving obligations proprietary trade secrets term termination jurisdiction applicable law signatures witness", "Legal & Contracts"),
            ("Employment contract terms of service privacy policy GDPR compliance legal regulations statutory requirements liability clause copyright infringement patent claim court order subpoena affidavit power of attorney", "Legal & Contracts"),
            ("Service level agreement SLA breach of contract indemnification limitation of liability dispute resolution governing jurisdiction legal counsel attorney client privilege signature date execution", "Legal & Contracts"),
            ("Python FastAPI REST API server endpoint code function algorithm database SQL React JavaScript async await frontend backend computer science network protocol HTTP web socket software architecture git repository docker deployment microservice bug fix release", "Technology & Code"),
            ("React component jsx state props hooks useEffect useState tailwind css style UI dashboard web app typescript node npm build bundle vite webpack routing frontend web development", "Technology & Code"),
            ("Database schema query postgresql mysql mongodb redis query execution index SQL table primary key join foreign key transaction database migration RESTful API GraphQL JSON response", "Technology & Code"),
            ("Machine learning deep learning neural network model training dataset accuracy loss function python pytorch tensorflow scikit-learn classification regression NLP computer vision transformer model gradient descent feature extraction", "Technology & Code"),
            ("Patient medical report clinical diagnosis doctor prescription pharmacy medicine treatment health symptoms vital signs lab test results MRI scan X-ray blood pressure heart rate oncology cardiology hospital admission pathology", "Medical & Healthcare"),
            ("Medical record physician consultation diagnosis dosage medication prescription pharmacy health insurance claim treatment protocol patient history clinical trial surgery procedure nursing care cardiology neurology", "Medical & Healthcare"),
            ("Clinical trial report pharmaceutical drug test efficacy dosage side effects patient study placebo control group medical ethics FDA approval pathology lab results immunology diagnostic analysis", "Medical & Healthcare"),
            ("Abstract paper study methodology research thesis literature review hypothesis analysis results discussion citation bibliography methodology peer review doi journal publication experiment findings statistical significance sample size dataset", "Academic & Research"),
            ("Research paper abstract introduction background literature review methodology data analysis empirical results conclusion bibliography citation IEEE ACM Springer journal peer-reviewed study experiment hypothesis methodology", "Academic & Research"),
            ("Scientific study experimental setup quantitative analysis qualitative survey sample statistical variance standard deviation p-value confidence interval hypothesis testing methodology discussion references", "Academic & Research"),
            ("Marketing campaign SEO search engine optimization social media target audience leads conversion rate click-through rate CTR sales funnel brand awareness content strategy customer acquisition marketing analytics advertising copy email campaign market research", "Marketing & Sales"),
            ("Sales strategy customer relationship CRM lead generation campaign conversion revenue goal product launch market positioning buyer persona target demographic social media advertising ROI brand strategy promotional offers", "Marketing & Sales"),
            ("Resume CV curriculum vitae work experience education skills qualifications candidate job application employment history summary references contact phone email cover letter portfolio HR interview recruiter onboarding evaluation performance review", "Personal & HR"),
            ("Curriculum vitae resume experience history education bachelor master degree skills languages certification projects references cover letter job application candidate performance review employee appraisal HR interview", "Personal & HR")
        ]

        texts = [item[0] for item in corpus]
        labels = [item[1] for item in corpus]
        return texts, labels

    def _initialize_and_train_model(self):
        if not SKLEARN_AVAILABLE:
            return

        try:
            texts, labels = self._get_training_corpus()
            self.model = Pipeline([
                ('tfidf', TfidfVectorizer(ngram_range=(1, 2), stop_words='english', min_df=1, sublinear_tf=True)),
                ('clf', SGDClassifier(loss='log_loss', max_iter=1000, random_state=42, alpha=1e-4))
            ])
            self.model.fit(texts, labels)
        except Exception as e:
            print(f"Error training ML document classifier: {e}")
            self.model = None

    def extract_text(self, filepath: str, filename: str) -> str:
        ext = os.path.splitext(filename)[1].lower()
        extracted_text = ""

        try:
            if ext == ".pdf":
                if PYPDF_AVAILABLE:
                    reader = pypdf.PdfReader(filepath)
                    pages_text = []
                    for i, page in enumerate(reader.pages):
                        if i >= 15:
                            break
                        t = page.extract_text()
                        if t:
                            pages_text.append(t)
                    extracted_text = " ".join(pages_text)

            elif ext in [".docx", ".doc"]:
                if DOCX_AVAILABLE and ext == ".docx":
                    doc = docx.Document(filepath)
                    extracted_text = " ".join([p.text for p in doc.paragraphs if p.text])

            elif ext in [".txt", ".md", ".py", ".js", ".html", ".css", ".json", ".csv", ".rtf", ".cpp", ".c", ".java", ".ts"]:
                with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                    extracted_text = f.read(50000)

        except Exception as e:
            print(f"Text extraction failed for {filename}: {e}")

        return extracted_text.strip()

    def generate_keywords(self, text: str, filename: str) -> List[str]:
        words = re.findall(r'\b[a-zA-Z]{3,15}\b', text.lower())
        stopwords = {
            "the", "and", "for", "that", "this", "with", "have", "from", "your", "which",
            "will", "can", "are", "were", "been", "has", "had", "not", "but", "all", "any",
            "one", "about", "into", "through", "during", "before", "after", "above", "below",
            "to", "from", "up", "down", "in", "out", "on", "off", "over", "under", "again",
            "further", "then", "once", "here", "there", "when", "where", "why", "how", "other",
            "some", "such", "no", "nor", "only", "own", "same", "so", "than", "too", "very"
        }

        ext = os.path.splitext(filename)[1].lower().replace(".", "")
        tags = []
        if ext:
            tags.append(ext.upper())

        freq = {}
        for w in words:
            if w not in stopwords and not w.isdigit():
                freq[w] = freq.get(w, 0) + 1

        sorted_words = sorted(freq.items(), key=lambda x: x[1], reverse=True)
        top_words = [w[0].capitalize() for w in sorted_words[:5]]

        for tw in top_words:
            if tw not in tags:
                tags.append(tw)

        return tags[:6]

    def classify(self, filepath: str, filename: str) -> Dict[str, Any]:
        text = self.extract_text(filepath, filename)
        
        if not text or len(text.strip()) < 15:
            ext_cat_map = {
                ".pdf": "Document",
                ".docx": "Document",
                ".doc": "Document",
                ".txt": "Document",
                ".png": "Image",
                ".jpg": "Image",
                ".jpeg": "Image",
                ".mp4": "Video",
                ".mp3": "Audio",
                ".zip": "Archive",
                ".py": "Technology & Code",
                ".js": "Technology & Code"
            }
            ext = os.path.splitext(filename)[1].lower()
            fallback_cat = ext_cat_map.get(ext, "General")
            
            return {
                "predicted_category": fallback_cat,
                "confidence": 0.85,
                "confidence_percentage": "85.0%",
                "tags": [ext.replace(".", "").upper() or "FILE", fallback_cat],
                "summary": f"Binary/Media file ({filename}). Content auto-categorized by file format.",
                "domain_scores": {fallback_cat: 0.85}
            }

        if SKLEARN_AVAILABLE and self.model:
            try:
                probs = self.model.predict_proba([text])[0]
                best_idx = np.argmax(probs)
                best_cat = self.model.classes_[best_idx]
                confidence = float(probs[best_idx])
                
                domain_scores = {
                    cls: round(float(p), 3) 
                    for cls, p in zip(self.model.classes_, probs)
                }
            except Exception as e:
                print(f"ML Prediction error: {e}")
                best_cat = "General"
                confidence = 0.70
                domain_scores = {"General": 0.70}
        else:
            best_cat = "General"
            confidence = 0.75
            domain_scores = {"General": 0.75}

        extracted_tags = self.generate_keywords(text, filename)
        if best_cat not in extracted_tags:
            extracted_tags.insert(0, best_cat)

        summary_clean = re.sub(r'\s+', ' ', text[:250]).strip()
        summary = summary_clean + ("..." if len(text) > 250 else "")

        return {
            "predicted_category": best_cat,
            "confidence": round(confidence, 4),
            "confidence_percentage": f"{round(confidence * 100, 1)}%",
            "tags": extracted_tags,
            "summary": summary,
            "domain_scores": domain_scores
        }


classifier_engine = DocumentClassifierEngine()
