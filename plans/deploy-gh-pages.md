# GitHub Pages Deployment: Britain Concert Site

Publish the Britain-themed Blasmusik concert site (`britain-concert-site.html`, 199 arrangements + 12 guest acts) on GitHub Pages via `gh` CLI, so orchestra colleagues get a clickable German UI without opening a CSV. Repo created under the `ederst` account; Pages served from `docs/` on `main`; regenerated and re-pushed whenever the data changes.

Locked decisions (user):
- GitHub account: `ederst` (already logged into `gh`, currently inactive; switch with `gh auth switch --user ederst`). Commits authored as ederst.
- Repo visibility: **public** (required for free-plan Pages). Repo name = directory name: `2027-themenkonzert-britain`.
- Pages source: `docs/` folder on the default branch `main`. Generator output path moves from repo root to `docs/index.html`.
- Deploy now with current data (199 arr + 12 guest rows); regeneration documented as routine push step.
- Privacy: guest contact data (emails, phones) stays in the site. It is public-source information (found on public booking pages) and the repo is public anyway, so a JS gate would be fake protection. Skip it.
- Junk file `typescript` (leftover `script` capture of a failed command) deleted; `.venv/` gitignored.

## For Future Agents
Mark checkboxes `- [x]` as complete; when a phase is done, set its status to `Complete` and write its **Phase Summary** (what was done, key decisions, anything needed to continue with zero context); run the phase's **Verification Plan** and record the result before moving on. When all phases are done, fill in **Final Recap** and **Deployment Plan**.

## Phase 1: Repo hygiene + first commit
Status: Not started

- [ ] Delete junk `typescript` (script-capture artifact, no content)
- [ ] Delete dead scripts (0B stubs, never referenced): `plans/check_parity.py`, `plans/merge_all.py`, `plans/run_site_build.py`
- [ ] Delete superseded perl scripts: `plans/make_site.pl` (replaced by `make_site.py`, which `.mise.toml` calls), `plans/merge_to_csv.pl` (replaced by `merge_lanes.py`)
- [ ] Write `.gitignore`: `.venv/`, `__pycache__/`
- [ ] Confirm git identity = ederst: `git config user.name && git config user.email` (set locally if wrong)
- [ ] Stage + first commit: `git add -A && git commit -m "chore: britain concert site + research plans"`
- [ ] Switch gh active account: `gh auth switch --user ederst` (verify with `gh auth status`)

### Verification Plan
- `git status` → clean tree, zero untracked files listed (`.venv/` and `typescript` absent)
- `ls plans/*.pl plans/check_parity.py plans/merge_all.py plans/run_site_build.py` → `No such file` for all
- `git log --oneline -1` → one commit, `main` branch
- `gh auth status` → `✓ Logged in to github.com account ederst` with `Active account: true`

### Phase Summary
_(write when phase completes)_

## Phase 2: Generate site into docs/
Status: Not started

- [ ] Edit `plans/make_site.py`: output path repo-root `britain-concert-site.html` → `docs/index.html` (self-contained HTML unchanged)
- [ ] Update `.mise.toml` `make-site` task description to reference `docs/index.html`
- [ ] Regenerate: `mise run make-site`
- [ ] Remove stale repo-root `britain-concert-site.html` (superseded by `docs/index.html`); delete file, no git mv needed

### Verification Plan
- `ls -la docs/` → `index.html` present, size ~184K
- `grep -c "<tr>" docs/index.html` → 211 (199 arrangement + 12 guest data rows)
- Generator stdout reports `199 arr + 12 guest rows embedded`
- `grep -o "<title>[^<]*</title>" docs/index.html` → `<title>Großbritannien Themenkonzert 2027, Auswahl-Hilfe</title>`
- Repo-root `britain-concert-site.html` gone

### Phase Summary
_(write when phase completes)_

## Phase 3: Create repo + push
Status: Not started

- [ ] `gh repo create 2027-themenkonzert-britain --public --source . --remote origin --push`
- [ ] Confirm remote set + pushed: `git remote -v` → origin → github.com:ederst/2027-themenkonzert-britain

### Verification Plan
- `gh repo view ederst/2027-themenkonzert-britain --json name,visibility,defaultBranchRef` → public, main
- `git ls-remote origin HEAD` → matches local `main`
- No secrets in pushed tree: `git ls-files | grep -iE "env|token|secret|key"` → empty

### Phase Summary
_(write when phase completes)_

## Phase 4: Enable Pages from docs/
Status: Not started

- [ ] `gh api --method POST repos/ederst/2027-themenkonzert-britain/pages -f "source[branch]=main" -f "source[path]=/docs"`
- [ ] Poll until built: `gh api repos/ederst/2027-themenkonzert-britain/pages --jq '.status'` → `built`

### Verification Plan
- `curl -sI https://ederst.github.io/2027-themenkonzert-britain/` → HTTP 200
- `curl -s https://ederst.github.io/2027-themenkonzert-britain/ | grep -o "<title>[^<]*</title>"` → matches title from Phase 2

### Phase Summary
_(write when phase completes)_

## Phase 5: Document URL + handoff
Status: Not started

- [ ] Insert live URL into site header or top of CSV? No. Add URL line to this plan's Final Recap
- [ ] Update `plans/research-britain-arrangements.md` → Deployment Plan section: replace "push to GitHub Pages as docs/..." placeholder with the real URL + regen steps
- [ ] Note in `plans/research-guest-act.md` Final Recap that site is live (URL)

### Verification Plan
- `grep -n "ederst.github.io" plans/research-britain-arrangements.md plans/research-guest-act.md plans/deploy-gh-pages.md` → URL present in all three
- `curl -sI https://ederst.github.io/2027-themenkonzert-britain/` → still 200 after any edits (site file untouched)

### Phase Summary
_(write when phase completes)_

## Final Recap
_(write when all phases complete: live URL, repo location, what was deployed)_

## Deployment Plan
_(write when all phases complete: how to regenerate + publish updated data)_

Regeneration routine (after future CSV/JSON work):
1. `mise run make-site` → rewrites `docs/index.html`
2. `git add docs/index.html britain-arrangements.csv guest-acts.csv && git commit -m "data: update site"`
3. `git push` → Pages auto-rebuilds from `docs/` on `main`
4. Verify: `curl -sI https://ederst.github.io/2027-themenkonzert-britain/` → 200