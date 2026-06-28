# GitHub Contribution and Versioning Guide

Guidelines to track, version, and deploy updates via GitHub.

## Branching Model
- **main:** Production branch. Locked. Requires PR approvals.
- **develop:** Development aggregation branch.
- **feature/xxx:** Individual feature development branches.

## Git Commits Convention
Follow Conventional Commits:
- `feat(ml): add decision tree explanations`
- `fix(eda): resolve nan division in correlation`
- `docs(readme): update virtualenv instructions`

## CI/CD Pipeline
Configure GitHub Actions (`.github/workflows/deploy.yml`) to:
1. Lint python modules using `flake8` or `black`.
2. Build Vite bundle using `npm run build`.
3. Push images to GCP Artifact Registry / AWS ECR.
4. Deploy to Kubernetes / Cloud Run / EC2.
