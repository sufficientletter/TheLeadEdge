# Git Conventions

- Commit messages: concise, imperative mood ("add feature" not "added feature").
- Branch naming: `feature/<name>`, `fix/<name>`, `docs/<name>`.
- Never force push to main/master.
- Always review changes before committing (`git diff`).
- Stage specific files by name, not `git add -A` (avoid committing secrets or MLS data).
- Include `Co-Authored-By` line for AI-assisted commits.
- NEVER commit files in Data/ directory (MLS exports, PII).
- NEVER commit .env files or credential files.
