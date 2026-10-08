# Contributing

## Branch and deploy flow

PanKbase uses a two-stage promote model:

1. Open feature-branch PRs against **`dev`** (not `main`).
2. After CI is green and the PR is merged, verify on **staging** (`dev` deploys to staging).
3. Promote staging to production with a **`dev` → `main`** PR (merge only after staging checks and maintainer approval). `main` deploys to production.

Do not merge feature work directly to `main` except for emergency hotfixes, which should still be brought back to `dev` promptly.

Sync production back to staging when needed with a **`main` → `dev`** PR.
