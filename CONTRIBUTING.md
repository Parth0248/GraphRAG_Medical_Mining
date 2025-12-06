# Contributing to GraphRAG_Medical_Mining

Thanks for your interest in contributing! To keep the repository consistent and easy to maintain,
please follow the guidelines below.

## How to contribute
1. Fork the repository and create a branch named `feature/<short-description>` or `fix/<short-description>`.
2. Make small, focused commits. Use imperative commit messages, e.g. `Add CONTRIBUTING.md`.
3. Open a Pull Request with a clear description of what changed and why.

## Development setup
- Install dependencies:
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

- Run tests:
```bash
pytest -q
```

## Coding style
- Use `black` for formatting.
- Use `isort` to sort imports.
- Lint with `flake8` or `ruff`.

## Branching & PR rules
- Base branch: `main`
- PR title should be concise, e.g. `Add CI workflow and basic tests`
- Include tests for new features when possible.
- Link related issues in the PR description.

## Commit message guidelines
- Short summary (max 72 chars)
- Blank line
- More detailed description if needed

Example:
```
Add CI workflow and basic smoke tests

- Add GitHub Actions workflow for pytest and flake
- Add basic repository smoke test
```

## Code of Conduct
Be respectful and follow open-source community norms.