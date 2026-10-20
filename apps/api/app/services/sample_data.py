"""Curated LinkedIn-Style Job Postings Dataset, Sample Resume Personas, and Evaluation Benchmark."""

from typing import TypedDict


class JobPostingRecord(TypedDict):
    job_id: str
    title: str
    company: str
    location: str
    work_mode: str
    domain: str
    seniority: str
    salary_range: str
    description: str


JOB_POSTINGS_DATASET: list[JobPostingRecord] = [
    {
        "job_id": "job-01",
        "title": "Applied AI & NLP Engineer (RAG / LLMs)",
        "company": "Veritas AI Labs",
        "location": "Bengaluru / Remote",
        "work_mode": "Hybrid",
        "domain": "AI & NLP",
        "seniority": "Mid-Level (2–4 yrs)",
        "salary_range": "$115k – $145k (₹28L – ₹42L)",
        "description": (
            "We are hiring an Applied AI & NLP Engineer to build production Retrieval-Augmented Generation (RAG) "
            "and document intelligence systems. Required skills: Python, NLP, spaCy, Sentence-Transformers, FAISS "
            "vector search, LLMs & GenAI (Gemini API, structured output), FastAPI, and PostgreSQL. "
            "Nice to have: Docker, Next.js, and MLOps model monitoring."
        ),
    },
    {
        "job_id": "job-02",
        "title": "Full-Stack AI Engineer (Next.js + FastAPI)",
        "company": "NovaStack Systems",
        "location": "San Francisco / Remote",
        "work_mode": "Remote",
        "domain": "Full Stack + AI",
        "seniority": "Mid-Level (2–4 yrs)",
        "salary_range": "$130k – $165k",
        "description": (
            "Build end-to-end AI-native web products from interactive React/Next.js frontends to async FastAPI "
            "backends. Required skills: TypeScript, React, Next.js, Tailwind CSS, Python, FastAPI, REST & GraphQL APIs, "
            "PostgreSQL, and LLMs & GenAI. Preferred: Docker, WebSockets, and CI/CD & Git Workflows."
        ),
    },
    {
        "job_id": "job-03",
        "title": "Machine Learning Engineer — Personalization & Search",
        "company": "PulseStream Media",
        "location": "Seattle, WA",
        "work_mode": "Hybrid",
        "domain": "Machine Learning",
        "seniority": "Mid-Level (2–4 yrs)",
        "salary_range": "$140k – $175k",
        "description": (
            "Design semantic retrieval and ranking models for millions of items. Required skills: Python, PyTorch, "
            "scikit-learn, Sentence-Transformers, FAISS, Pandas & NumPy, and SQL. "
            "Preferred: MLOps & Model Monitoring, Redis & Streaming Queues, and Docker."
        ),
    },
    {
        "job_id": "job-04",
        "title": "Senior Data Scientist — FinTech Risk & Explainable AI",
        "company": "Aegis Financial",
        "location": "New York / Bengaluru",
        "work_mode": "Hybrid",
        "domain": "Data Science",
        "seniority": "Senior (5+ yrs)",
        "salary_range": "$145k – $180k (₹35L – ₹50L)",
        "description": (
            "Lead churn prediction, credit risk scoring, and explainable ML dashboards. Required skills: Python, SQL, "
            "scikit-learn, XGBoost / LightGBM, Pandas & NumPy, Data Visualization, and PostgreSQL. "
            "Nice to have: FastAPI, MLOps & Model Monitoring, and Redis & Streaming Queues."
        ),
    },
    {
        "job_id": "job-05",
        "title": "Frontend Product Engineer (React, TypeScript & Design Systems)",
        "company": "LinearCraft UI",
        "location": "Remote",
        "work_mode": "Remote",
        "domain": "Frontend Engineering",
        "seniority": "Entry / Early Career (0–2 yrs)",
        "salary_range": "$105k – $135k",
        "description": (
            "Craft ultra-responsive, accessible web interfaces and interactive data visualizations. "
            "Required skills: TypeScript, JavaScript, React, Next.js, Tailwind CSS, Data Visualization, "
            "and REST & GraphQL APIs. Preferred: Node.js & Express, WebSockets, and CI/CD & Git Workflows."
        ),
    },
    {
        "job_id": "job-06",
        "title": "Backend Platform Engineer (Python, FastAPI & Distributed Queues)",
        "company": "Chronos Cloud",
        "location": "Austin, TX / Remote",
        "work_mode": "Remote",
        "domain": "Backend Engineering",
        "seniority": "Mid-Level (2–4 yrs)",
        "salary_range": "$125k – $155k",
        "description": (
            "Architect low-latency microservices and event-driven pipelines handling 20k req/sec. "
            "Required skills: Python, FastAPI, SQL, PostgreSQL, SQLAlchemy & ORM, Redis & Streaming Queues, "
            "Docker, and REST & GraphQL APIs. Nice to have: Go, Kubernetes, and Prometheus & Observability."
        ),
    },
    {
        "job_id": "job-07",
        "title": "Computer Vision & Edge AI Engineer",
        "company": "SightGuard Robotics",
        "location": "Munich / Hybrid",
        "work_mode": "Hybrid",
        "domain": "Computer Vision",
        "seniority": "Mid-Level (2–4 yrs)",
        "salary_range": "$120k – $150k",
        "description": (
            "Build real-time perception, face/gesture analytics, and ONNX edge inference pipelines. "
            "Required skills: Python, PyTorch, Computer Vision (OpenCV, YOLOv8, MediaPipe), FastAPI, "
            "and Pandas & NumPy. Preferred: C++, MLOps & Model Monitoring, and WebSockets."
        ),
    },
    {
        "job_id": "job-08",
        "title": "MLOps & Cloud Reliability Engineer",
        "company": "ScaleMesh AI",
        "location": "London / Remote",
        "work_mode": "Remote",
        "domain": "MLOps & DevOps",
        "seniority": "Mid-Level (2–4 yrs)",
        "salary_range": "$130k – $160k",
        "description": (
            "Automate ML training pipelines, containerized model serving, and drift observability. "
            "Required skills: Python, Docker, Cloud & Kubernetes (AWS/GCP), CI/CD & Git Workflows, "
            "Prometheus & Observability, MLOps & Model Monitoring, and FastAPI."
        ),
    },
    {
        "job_id": "job-09",
        "title": "Document Intelligence & NLP Research Engineer",
        "company": "LexiParse AI",
        "location": "Toronto / Remote",
        "work_mode": "Remote",
        "domain": "AI & NLP",
        "seniority": "Mid-Level (2–4 yrs)",
        "salary_range": "$120k – $150k",
        "description": (
            "Extract structured knowledge graphs and entities from complex PDFs, resumes, and legal contracts. "
            "Required skills: Python, Document Parsing (PyMuPDF/OCR), NLP, spaCy, Hugging Face Transformers, "
            "Sentence-Transformers, and LLMs & GenAI. Preferred: FastAPI and SQL."
        ),
    },
    {
        "job_id": "job-10",
        "title": "Cybersecurity & Threat Intelligence ML Engineer",
        "company": "SentinelSOC",
        "location": "Reston, VA / Hybrid",
        "work_mode": "Hybrid",
        "domain": "Cybersecurity + ML",
        "seniority": "Mid-Level (2–4 yrs)",
        "salary_range": "$135k – $168k",
        "description": (
            "Detect network intrusions, phishing, and anomalous log patterns in real time. "
            "Required skills: Python, scikit-learn, XGBoost / LightGBM, Application Security & Privacy, "
            "Pandas & NumPy, SQL, and Docker. Preferred: Prometheus & Observability and FastAPI."
        ),
    },
    {
        "job_id": "job-11",
        "title": "Junior Software & AI Developer (New Grad / Early Career)",
        "company": "LaunchPad Labs",
        "location": "Bengaluru / Hyderabad",
        "work_mode": "Hybrid",
        "domain": "Full Stack + AI",
        "seniority": "Entry / Early Career (0–2 yrs)",
        "salary_range": "$70k – $95k (₹14L – ₹22L)",
        "description": (
            "Join our core product squad shipping AI-powered developer tools. "
            "Required skills: Python, JavaScript, TypeScript, React, SQL, FastAPI, and CI/CD & Git Workflows. "
            "Nice to have: LLMs & GenAI, Tailwind CSS, and Docker."
        ),
    },
    {
        "job_id": "job-12",
        "title": "Real-Time Collaborative Systems Engineer",
        "company": "SyncCanvas",
        "location": "San Francisco / Remote",
        "work_mode": "Remote",
        "domain": "Full Stack Engineering",
        "seniority": "Senior (5+ yrs)",
        "salary_range": "$150k – $185k",
        "description": (
            "Build conflict-free collaborative editors and low-latency WebSocket workspaces. "
            "Required skills: TypeScript, JavaScript, React, Next.js, Node.js & Express, WebSockets, "
            "Redis & Streaming Queues, PostgreSQL, and Docker."
        ),
    },
]


SAMPLE_PERSONAS = [
    {
        "id": "ai-fullstack-builder",
        "label": "Aarav Sharma — AI & Full-Stack Engineer (Best Fit for NLP/RAG)",
        "role_focus": "Applied AI & Full-Stack Engineer",
        "target_role_title": "Applied AI & NLP Engineer (RAG / LLMs)",
        "resume_text": """Aarav Sharma
Email: aarav.sharma.dev@example.com | Phone: +91 98765-43210
GitHub: https://github.com/aarav-ai | LinkedIn: https://linkedin.com/in/aarav-sharma-ai
Pronouns: he/him

SUMMARY
Applied AI and Full-Stack Engineer with 2.5 years of experience building NLP pipelines, semantic search engines, and interactive Next.js + FastAPI web applications. Passionate about grounded LLM workflows and low-latency retrieval.

EXPERIENCE
AI Software Engineer | CogniWave Technologies (2024 - Present)
- Engineered a hybrid semantic search pipeline using Python, Sentence-Transformers, and FAISS over 150k technical documents, improving top-3 retrieval recall by 31%.
- Worked on backend REST APIs in FastAPI and SQLAlchemy to serve document parsing and entity extraction requests.
- Helped with integrating Gemini API structured JSON outputs for automated report synthesis and citation verification.
- Responsible for parsing noisy PDF and DOCX uploads using PyMuPDF and custom spaCy entity rules.

Full-Stack Developer Intern | CloudPulse Labs (2023 - 2024)
- Built a real-time analytics dashboard using React, Next.js, TypeScript, and Tailwind CSS, cutting page load latency by 42%.
- Assisted in writing SQL queries and PostgreSQL migrations for user session analytics and unit testing with pytest.

PROJECTS
Campus RAG Assistant & Evaluator
- Designed a local citation-grounded RAG assistant with Sentence-Transformers, FAISS, and FastAPI that refuses out-of-scope queries and measures faithfulness on 200 test questions.

EDUCATION
B.Tech in Computer Science & Engineering | National Institute of Technology (NIT) | 2023

SKILLS
Python, TypeScript, JavaScript, SQL, NLP, spaCy, Sentence-Transformers, FAISS, LLMs & GenAI, Gemini API, PyMuPDF, FastAPI, React, Next.js, Tailwind CSS, PostgreSQL, SQLAlchemy, pytest, Git
""",
        "job_description": """Role: Applied AI & NLP Engineer (RAG / LLMs) — Veritas AI Labs
We are looking for an Applied AI & NLP Engineer to architect our next-generation resume intelligence and enterprise RAG platform.

Required Qualifications:
- 2+ years of hands-on experience in Python and modern Backend APIs (FastAPI, Pydantic, REST APIs).
- Strong foundation in NLP, entity extraction (spaCy), and Document Parsing (PyMuPDF / PDF extraction).
- Practical experience with Semantic Embeddings (Sentence-Transformers) and Vector Search (FAISS, Chroma, or pgvector).
- Experience integrating LLMs & GenAI (Gemini API, prompt engineering, structured JSON output with guardrails).
- Proficiency with relational databases (PostgreSQL, SQL) and full-stack UI integration (React, Next.js, TypeScript).

Preferred / Nice to Have:
- Containerization with Docker & Docker Compose.
- MLOps & Model Monitoring (MLflow, ONNX Runtime, drift detection).
- Prometheus & Observability for tracking API latency and token usage.
""",
    },
    {
        "id": "data-scientist-ml",
        "label": "Priya Nair — Data Scientist & Tabular ML (Switching to AI Eng)",
        "role_focus": "Data Scientist / ML Engineer",
        "target_role_title": "Machine Learning Engineer — Personalization & Search",
        "resume_text": """Priya Nair
Email: priya.nair.ds@example.com | Phone: (415) 555-0192
LinkedIn: https://linkedin.com/in/priya-nair-ml

SUMMARY
Data Scientist with 3 years of experience in predictive modeling, customer churn analytics, and explainable AI. Skilled in turning messy tabular datasets into calibrated production models.

EXPERIENCE
Data Scientist | FinSight Analytics (2023 - Present)
- Developed an XGBoost and scikit-learn customer churn classifier on 250k telecom accounts, improving PR-AUC from 0.64 to 0.83.
- Worked on generating SHAP per-customer explanations and interactive Streamlit dashboards for retention teams.
- Responsible for SQL and Pandas feature engineering pipelines across PostgreSQL data warehouses.
- Helped with training a PyTorch neural network prototype for transaction anomaly scoring.

Data Analyst | MetricCore (2022 - 2023)
- Automated weekly cohort reporting using Python, NumPy, Pandas, and SQL window functions, saving 12 hours of manual work per week.

EDUCATION
M.S. in Data Science | University of Washington | 2022
B.E. in Information Technology | Mumbai University | 2020

SKILLS
Python, SQL, scikit-learn, XGBoost, LightGBM, PyTorch, Pandas, NumPy, Streamlit, Plotly, PostgreSQL, Git
""",
        "job_description": """Role: Machine Learning Engineer — Personalization & Search (PulseStream Media)
Join our Search & Discovery ML team to build dense semantic retrieval and real-time ranking systems.

Required Qualifications:
- Strong proficiency in Python, SQL, Pandas & NumPy, and classical ML (scikit-learn, XGBoost).
- Deep learning experience with PyTorch for representation learning and ranking models.
- Hands-on experience with Sentence-Transformers embeddings and FAISS vector search indexes.
- Ability to expose low-latency inference services via FastAPI and package environments with Docker.

Preferred / Nice to Have:
- Experience with Redis & Streaming Queues for real-time feature stores.
- MLOps & Model Monitoring (MLflow, ONNX, drift tracking).
""",
    },
    {
        "id": "frontend-react-dev",
        "label": "Rohan Verma — Frontend React Developer (Targeting Full-Stack AI)",
        "role_focus": "Frontend / Web Engineer",
        "target_role_title": "Full-Stack AI Engineer (Next.js + FastAPI)",
        "resume_text": """Rohan Verma
Email: rohan.ui@example.com | Phone: +1-650-555-0148
GitHub: https://github.com/rohanverma-ui

SUMMARY
Frontend Software Engineer with 2 years of experience crafting responsive React and Next.js web applications, design systems, and real-time dashboards.

EXPERIENCE
Frontend Engineer | PixelForge Studio (2024 - Present)
- Built 18 reusable accessible UI components in React 18, Next.js App Router, TypeScript, and Tailwind CSS, achieving a 98 Lighthouse performance score.
- Worked on integrating REST APIs and WebSockets for live collaborative dashboard charts using Recharts.
- Helped with Node.js and Express proxy routes and GitHub Actions CI/CD workflows.

Web Developer Intern | BrightWeb (2023 - 2024)
- Responsible for converting Figma mockups into responsive JavaScript and CSS layouts.

EDUCATION
B.Tech in Computer Science | Vellore Institute of Technology | 2023

SKILLS
TypeScript, JavaScript, React, Next.js, Tailwind CSS, Recharts, Chart.js, Node.js, REST APIs, WebSockets, Git, GitHub Actions
""",
        "job_description": """Role: Full-Stack AI Engineer (Next.js + FastAPI) — NovaStack Systems
We are seeking a Full-Stack AI Engineer to build interactive AI workspaces powered by Next.js on the frontend and Python FastAPI + Gemini LLMs on the backend.

Required Qualifications:
- Strong frontend mastery in TypeScript, React, Next.js, and Tailwind CSS.
- Backend API development using Python and FastAPI with REST & GraphQL APIs.
- Experience integrating LLMs & GenAI (Gemini API, structured JSON schemas, semantic embeddings).
- Relational data modeling with PostgreSQL and SQL.

Preferred / Nice to Have:
- Real-time streaming with WebSockets.
- Docker containerization and CI/CD & Git Workflows.
""",
    },
]


# Gold-standard evaluation benchmark comparing Hybrid Semantic + Taxonomy Search vs. Naive Keyword Counting
EVALUATION_BENCHMARK_CASES = [
    {
        "case_id": "eval-01",
        "title": "Synonym & Paraphrase Resilience (Neural Nets -> PyTorch/Embeddings)",
        "resume_snippet": (
            "Engineered dense bi-encoder text representations using MiniLM and indexed 50k passages in a nearest-neighbor "
            "vector store. Exposed async Python Starlette endpoints and parsed PDFs with fitz. Integrated Gemini structured JSON."
        ),
        "expected_relevant_jobs": ["job-01", "job-09", "job-03"],
    },
    {
        "case_id": "eval-02",
        "title": "Full-Stack AI Product Engineer Alignment",
        "resume_snippet": (
            "Built interactive Next.js App Router interfaces in strict TypeScript and Tailwind CSS connected to a Python "
            "FastAPI backend, PostgreSQL database, WebSockets, and LLM prompt pipelines."
        ),
        "expected_relevant_jobs": ["job-02", "job-11", "job-05"],
    },
    {
        "case_id": "eval-03",
        "title": "Tabular Data Science & Explainable FinTech ML",
        "resume_snippet": (
            "Trained calibrated gradient boosted decision trees (XGBoost, LightGBM) and scikit-learn pipelines on imbalanced "
            "customer churn data in SQL, Pandas, and NumPy with SHAP waterfall explanations."
        ),
        "expected_relevant_jobs": ["job-04", "job-10", "job-03"],
    },
    {
        "case_id": "eval-04",
        "title": "Real-Time Computer Vision & Edge Inference",
        "resume_snippet": (
            "Developed real-time video frame processors using OpenCV, MediaPipe landmarks, and YOLOv8 object detection in "
            "PyTorch, serving alerts over FastAPI WebSockets."
        ),
        "expected_relevant_jobs": ["job-07", "job-03", "job-01"],
    },
    {
        "case_id": "eval-05",
        "title": "Cloud MLOps, Containers & Observability",
        "resume_snippet": (
            "Containerized Python FastAPI model servers with multi-stage Dockerfiles, deployed on Kubernetes/GCP with GitHub "
            "Actions CI/CD, and monitored latency and drift in Prometheus and Grafana."
        ),
        "expected_relevant_jobs": ["job-08", "job-06", "job-01"],
    },
]
