# Contributing to RoleFit AI

Thank you for your interest in contributing to **RoleFit AI — Smart Resume Analyzer and Job Matcher**!

---

## How You Can Contribute

1. **Expanding the Skill Taxonomy:** Add new emerging technical skills, aliases, and course learning paths in `apps/api/app/services/taxonomy.py`.
2. **Adding LinkedIn Job Postings:** Add realistic job postings across new engineering disciplines in `apps/api/app/services/sample_data.py`.
3. **Enhancing Evaluation Benchmark Cases:** Add real-world resume-job pairs with expected relevant IDs in `EVALUATION_BENCHMARK_CASES`.
4. **UI Improvements:** Enhance charts, accessibility, or mobile responsiveness in `apps/web/src/app/page.tsx`.

---

## Development Workflow

1. Fork the repository and create your feature branch:
   ```bash
   git checkout -b feature/my-new-feature
   ```
2. Make your changes and verify with automated tests:
   ```bash
   cd apps/api
   PYTHONPATH=. .venv/bin/python -m pytest -v
   ```
3. Commit your changes with descriptive messages:
   ```bash
   git commit -m "feat(taxonomy): add Rust async and Tokio aliases"
   ```
4. Push to your branch and submit a Pull Request!
