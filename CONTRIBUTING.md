# Contributing to Agentic Math Solver

Thank you for your interest in contributing! This guide will help you get started.

---

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
- [Development Setup](#development-setup)
- [Pull Request Process](#pull-request-process)
- [Code Style](#code-style)
- [Reporting Bugs](#reporting-bugs)
- [Suggesting Features](#suggesting-features)

---

## Code of Conduct

This project follows a standard code of conduct. By participating, you agree to uphold a respectful, inclusive environment for everyone.

---

## How Can I Contribute?

### 🐛 Bug Reports
- Use the [GitHub Issues](https://github.com/Sarika-stack23/agentic-math-solver/issues) tab
- Include steps to reproduce, expected vs actual behavior, and screenshots if applicable
- Tag with `bug` label

### 💡 Feature Requests
- Open an issue with the `enhancement` label
- Describe the use case and expected behavior
- If possible, include mockups or diagrams

### 🔧 Code Contributions
- Fork the repository
- Create a feature branch (`git checkout -b feat/your-feature`)
- Make your changes with clear, atomic commits
- Submit a pull request

---

## Development Setup

### Prerequisites
- **Python 3.9+** and **pip**
- **Node.js 18+** and **npm**
- **Docker** (optional, for containerized development)

### Backend

```bash
# Clone and navigate
git clone https://github.com/Sarika-stack23/agentic-math-solver.git
cd agentic-math-solver/backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate   # macOS/Linux
# venv\Scripts\activate    # Windows

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp ../.env.example ../.env
# Edit .env with your API keys

# Run the backend
uvicorn src.main:app --reload --port 8080
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Running Tests

```bash
# From project root
pytest tests/ -v
```

---

## Pull Request Process

1. **Fork** the repo and create your branch from `main`
2. **Write clear commit messages** using [Conventional Commits](https://www.conventionalcommits.org/):
   - `feat:` — new feature
   - `fix:` — bug fix
   - `docs:` — documentation changes
   - `refactor:` — code restructuring
   - `test:` — adding or updating tests
   - `chore:` — tooling, CI, or dependency updates
3. **Ensure tests pass** before submitting
4. **Update documentation** if your change affects the public API or user-facing features
5. **Request a review** — all PRs require at least one approval

---

## Code Style

### Python (Backend)
- Follow [PEP 8](https://peps.python.org/pep-0008/)
- Use type hints for function signatures
- Keep functions focused and under 50 lines where possible
- Write docstrings for public functions and classes

### TypeScript (Frontend)
- Use functional components with hooks
- Keep components small and reusable
- Use meaningful variable and function names
- Avoid `any` types — prefer explicit typing

### General
- No hardcoded secrets or API keys
- Use environment variables for configuration
- Write meaningful commit messages
- Comment non-obvious logic

---

## Reporting Bugs

When reporting bugs, please include:

| Detail | Description |
| :--- | :--- |
| **Environment** | OS, browser, Python/Node version |
| **Steps to Reproduce** | Numbered steps to trigger the bug |
| **Expected Behavior** | What should happen |
| **Actual Behavior** | What actually happens |
| **Screenshots/Logs** | Any visual evidence or error output |

---

## Suggesting Features

We love new ideas! When suggesting features:

- **Check existing issues** to avoid duplicates
- **Describe the problem** your feature solves
- **Propose a solution** with implementation details if possible
- **Consider trade-offs** — performance, complexity, and maintenance cost

---

## 📬 Questions?

If you have questions about contributing, feel free to open a [Discussion](https://github.com/Sarika-stack23/agentic-math-solver/discussions) or reach out via issues.

---

<div align="center">
  <i>Thank you for helping make Agentic Math Solver better! 🚀</i>
</div>
