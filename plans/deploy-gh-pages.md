# GitHub Pages Deployment: Britain Concert Site

Publish the Britain-themed Blasmusik concert site (`docs/index.html`, 199 arrangements + 12 guest acts) on GitHub Pages via `gh` CLI, so orchestra colleagues get a clickable German UI without opening a CSV. Repo created under the `ederst` account; Pages served from `docs/` on `main`; regenerated and re-pushed whenever the data changes.

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
Status: Complete

- [x] Delete junk `typescript` (script-capture artifact, no content)
- [x] Delete dead scripts (0B stubs, never referenced): `plans/check_parity.py`, `plans/merge_all.py`, `plans/run_site_build.py`
- [x] Delete superseded perl scripts: `plans/make_site.pl` (replaced by `make_site.py`, which `.mise.toml` calls), `plans/merge_to_csv.pl` (replaced by `merge_lanes.py`)
- [x] Write `.gitignore`: `.venv/`, `__pycache__/`
- [x] Confirm git identity = ederst: `git config user.name && git config user.email` (set locally if wrong)
- [x] Stage + first commit: `git add -A && git commit -m "chore: britain concert site + research plans"`
- [x] Switch gh active account: `gh auth switch --user ederst` (verify with `gh auth status`)

### Verification Plan
- `git status` → clean tree, zero untracked files listed (`.venv/` and `typescript` absent)
- `ls plans/*.pl plans/check_parity.py plans/merge_all.py plans/run_site_build.py` → `No such file` for all
- `git log --oneline -1` → one commit, `main` branch
- `gh auth status` → `✓ Logged in to github.com account ederst` with `Active account: true`

### Phase Summary
Junk + 5 dead scripts deleted. `.gitignore` written (`.venv/`, `__pycache__/`). Git identity already ederst. First commit `66f5c15` (27 files, 1553 insertions). gh switched to ederst (active).

## Phase 2: Generate site into docs/
Status: Complete

- [x] Edit `plans/make_site.py`: output path repo-root `britain-concert-site.html` → `docs/index.html` (self-contained HTML unchanged)
- [x] Update `.mise.toml` `make-site` task description to reference `docs/index.html`
- [x] Regenerate: `mise run make-site`
- [x] Remove stale repo-root `britain-concert-site.html` (superseded by `docs/index.html`); delete file, no git mv needed

### Verification Plan
- `ls -la docs/` → `index.html` present, size ~184K
- `grep -c "<tr>" docs/index.html` → 211 (199 arrangement + 12 guest data rows)
- Generator stdout reports `199 arr + 12 guest rows embedded`
- `grep -o "<title>[^<]*</title>" docs/index.html` → `<title>Großbritannien Themenkonzert 2027, Auswahl-Hilfe</title>`
- Repo-root `britain-concert-site.html` gone

### Phase Summary
OUT path → `docs/index.html`; added `OUT.parent.mkdir(parents=True, exist_ok=True)` (first regen failed: docs/ missing). `.mise.toml` description updated. Regenerated (188,527b, 199 arr + 12 guest); stale root HTML deleted. Commit `5f50962` (3 files: git-mv root HTML → docs/index.html recorded by git as rename).

## Phase 3: Create repo + push
Status: Complete

- [x] `gh repo create 2027-themenkonzert-britain --public --source . --remote origin --push`
- [x] Confirm remote set + pushed: `git remote -v` → origin → github.com:ederst/2027-themenkonzert-britain

### Verification Plan
- `gh repo view ederst/2027-themenkonzert-britain --json name,visibility,defaultBranchRef` → public, main
- `git ls-remote origin HEAD` → matches local `main`
- No secrets in pushed tree: `git ls-files | grep -iE "env|token|secret|key"` → empty

### Phase Summary
Repo created: https://github.com/ederst/2027-themenkonzert-britain (PUBLIC, default branch main). Push OK, `main` tracks `origin/main`. No secrets in pushed tree.

## Phase 4: Enable Pages from docs/
Status: Complete

- [x] `gh api --method POST repos/ederst/2027-themenkonzert-britain/pages -f "source[branch]=main" -f "source[path]=/docs"`
- [x] Poll until built: `gh api repos/ederst/2027-themenkonzert-britain/pages --jq '.status'` → `built`

### Verification Plan
- `curl -sI https://ederst.github.io/2027-themenkonzert-britain/` → HTTP 200
- `curl -s https://ederst.github.io/2027-themenkonzert-britain/ | grep -o "<title>[^<]*</title>"` → matches title from Phase 2

### Phase Summary
Pages enabled with source main/docs (legacy build type, https_enforced). Status building → built after ~35s. Live URL returns HTTP 200; served title + h1 match local build.

## Phase 5: Document URL + handoff
Status: Complete

- [x] Insert live URL into site header or top of CSV? No. Add URL line to this plan's Final Recap
- [x] Update `plans/research-britain-arrangements.md` → Deployment Plan section: replace "push to GitHub Pages as docs/..." placeholder with the real URL + regen steps
- [x] Note in `plans/research-guest-act.md` Final Recap that site is live (URL)

### Verification Plan
- `grep -n "ederst.github.io" plans/research-britain-arrangements.md plans/research-guest-act.md plans/deploy-gh-pages.md` → URL present in all three
- `curl -sI https://ederst.github.io/2027-themenkonzert-britain/` → still 200 after any edits (site file untouched)

### Phase Summary
URL documented in both research plans (arrangements Deployment Plan replaced with live URL + regen steps; guest-act Final Recap notes live site). Deploy plan file updated with statuses/summaries. Final commit + push follows.

## Final Recap
Site LIVE: https://ederst.github.io/2027-themenkonzert-britain/ (public GitHub Pages, repo `ederst/2027-themenkonzert-britain`, source `docs/` on `main`, legacy build type). Deployed content: 199 arrangements + 12 guest acts, German UI, self-contained HTML, clickable shop links, embedded client-side filter. Repo hygiene done in passing: 6 dead/junk files deleted, `.gitignore` added, stub perl/python removed. Commits under ederst identity; gh active account now ederst. Regeneration = `mise run make-site` → commit `docs/index.html` → push (see Deployment Plan).

## Deployment Plan
Regeneration routine (after future CSV/JSON work):
1. `mise run make-site` → rewrites `docs/index.html`
2. `git add docs/index.html britain-arrangements.csv guest-acts.csv && git commit -m "data: update site"`
3. `git push` → Pages auto-rebuilds from `docs/` on `main`
4. Verify: `curl -sI https://ederst.github.io/2027-themenkonzert-britain/` → 200