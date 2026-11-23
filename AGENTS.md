# Spectra, Agent Guidelines

These rules govern agent work in this repository, luinbytes/spectra.
Spectra is a fork of Helium (imputnet/helium). This file replaces the
upstream Helium agent guidelines in this fork. Nothing in this file
authorises contributions to upstream Helium; anything ever proposed
upstream must follow Helium's own contributor policy and Lu's explicit
instruction.

## Documentation is part of every change

- The README does not need editing on every change. It does need
  thinking about on every change. For every PR, actively check whether
  anything in README.md or any other documentation in this repository
  is affected, and update what is affected in the same PR, never as a
  follow up Lu has to chase.
- Lu should never have to notice that the docs went stale. Remembering
  the documentation is the agent's job, not his.
- Watch for statements that are true today and will go false later:
  status claims, "not yet" claims, placeholder claims, planned versus
  shipped claims. When your change is the thing that makes one of
  those statements false, updating it is part of your change, even if
  nobody mentioned the README. Examples of the pattern: a first
  release makes "no releases yet" false, a landed feature makes
  "currently just a rebrand" false, a published legal page makes
  "will publish its own" false.
- When you add a new statement like that to the docs, add it to the
  watch list below in this file at the same time, so the next agent
  knows it exists and knows what should trigger its update.
- Always update any other relevant documentation in this repository in
  the same change too: docs files, comments that act as documentation,
  and the design notes where they exist.
- If a change genuinely needs no documentation update, say so in the
  PR description and say why. Silence is not acceptable; a reviewer
  should never have to ask whether the docs were considered.

### README statements on the watch list

These statements are in README.md right now and will go stale. Keep
this list current: add new ones as they appear, remove one only in the
same PR that updates or removes the statement itself.

- "Spectra does not have its own releases yet" and the Downloads
  section pointing to upstream Helium releases. Update on the first
  Spectra release.
- "Right now it is a rebrand of Helium with a design direction" and
  "the code here is currently Helium's". Update as Spectra's own
  features and patch layer land.
- The logo is a placeholder inherited from Helium. Update the README
  image and its alt text when Spectra gets its own logo.
- "Spectra will publish its own before any public release" in the
  legal documents section. Update when Spectra's own terms and
  privacy documents exist.
- The Helium beta note in Downloads. Revisit when Helium leaves beta
  or when Spectra's releases replace Helium's in that section.
- Never remove or weaken the Helium credit. README.md credits Helium
  at the top and at the bottom, and those credits stay in place in
  every edit. New features get described as Spectra's; the foundation
  stays credited to Helium and imput.
- Keep documentation honest about status. If something is planned,
  partial, or inherited unchanged from Helium, the docs say so.

## Pull requests and the Codex review

- Every PR in this repo gets an automatic review from ChatGPT Codex.
  Treat that review as part of the work, not as an optional extra.
- After opening or pushing to a PR, check for the Codex review and
  read every comment and finding it left. Do not report a PR as ready,
  finished, or safe to merge before that check has happened.
- Fix everything valid that Codex flags, in the same PR, then push and
  check for its re-review. Keep that loop going until the Codex review
  comes back with nothing outstanding that needs fixing.
- If a Codex finding is wrong or does not apply, do not silently
  ignore it. Reply on the PR explaining why, so the decision is on the
  record.
- When reporting back to Lu, state the Codex review status plainly:
  whether it has reviewed, what it flagged, what was fixed, and
  whether the latest re-review is clean.

## Working rules

- Work in a branch and open PRs inside luinbytes/spectra only. Do not
  push branches or open PRs to imputnet/helium or any other imputnet
  repository without Lu explicitly asking for exactly that.
- Keep Spectra's own changes as a clearly separated layer on top of
  Helium wherever practical, so rebasing onto upstream stays possible.
- Spectra and everything unique to it or to Helium in this repo is
  GPL-3.0. Keep the license file and all upstream credits intact.

## Branches stay clean

- main is always releasable. Nobody pushes to main directly; every
  change arrives by PR, with CI green and the Codex review checked
  (see above) before merge.
- One branch per change, named for what it does, with a short prefix
  for the kind of work: feat/, fix/, docs/, agents/, chore/,
  rebrand/ are the established prefixes.
- Branches are short lived. A branch exists to land one change, not
  to become a second home for work. If a branch is still open and
  untouched after about two weeks, it needs a decision: finish it,
  or close it and record what is left to do as an issue (see
  "Nothing gets forgotten" below). Never let it quietly rot.
- Delete branches when their PR merges or closes. A merged branch
  that still exists is clutter, not a backup; the history is in main.
- Keep an open branch current with main while it lives, so merges
  never arrive as a pile of stale conflicts.
- Never force push over someone else's work, and never rewrite
  history on main.

## Releases are deliberate

- Spectra follows the version scheme of the Helium and Chromium base
  it ships, with its own release notes. Do not invent a competing
  version story.
- A release is cut from main only, with CI green on the exact commit
  being released, and only through the release workflow or process
  documented at the time. No hand built one off releases.
- Every release gets notes: what changed, what is known broken, and
  which Helium and Chromium versions it is based on.
- The PR or change that cuts the first release, and every release
  after it, must sweep the README watch list above in the same work:
  release related statements are updated when the release happens,
  not later.
- Never edit, move, or delete a published release or its tag to make
  it look different. Fixes ship as a new release.
- If a release fails partway, say so plainly in the PR or issue
  tracking it. A half published release left silent is a stale fact
  waiting to mislead someone.

## CI workflows stay healthy

- The workflows under .github/workflows are part of the product.
  Treat a workflow change with the same care as a code change: its
  own branch, its own PR, Codex review checked.
- Never merge with red CI. A failing check is information, not an
  obstacle to route around. Do not disable, skip, or weaken a check
  to make a PR pass; fix the cause, or record the problem as an
  issue and leave the PR unmerged.
- Workflow edits are tested by the workflow itself running on the
  branch before merge wherever the trigger allows. A workflow that
  has never run successfully does not merge.
- Keep the third party actions used by the workflows current. Action
  versions age silently; they are on the maintenance sweep list
  below, and a version bump is a normal small PR, never a someday
  task.
- Secrets never appear in workflow files, logs, or artifacts. A
  workflow that needs a new secret stops and asks Lu; it does not
  invent a workaround.
- Cancel or supersede runs that no longer matter instead of letting
  the queue fill with stale builds. Long Chromium builds especially:
  one current build per branch is enough.

## Nothing gets forgotten

Lu's standing rule for this project: nothing is left to go stale,
unmaintained, or forgotten about. That only works if deferred work
lives somewhere an agent will actually see it again.

- Every deferred item, follow up, known issue, and "do this later"
  goes in exactly one durable place before the PR that created it
  closes: a GitHub issue in this repo, or an entry on the watch list
  in this file. A follow up mentioned only in a PR description, a
  review comment, or a chat message does not exist.
- Issues carry enough context to be picked up cold: what, why, and
  what done looks like. Close issues in the PR that resolves them,
  with the closing keyword, so nothing lingers as done but open.
- When you notice something stale while doing other work (an old
  branch, a red workflow nobody owns, a doc claim that drifted, a
  pin that aged), either fix it in scope or file the issue in the
  same session. Noticing and walking past is the failure this
  section exists to prevent.

### The maintenance sweep

On a regular pass, and whenever Lu asks for a tidy up, check each of
these and act on what you find. This list is the memory of the repo;
keep it complete. When something new starts aging (a new workflow, a
new pin, a new platform repo), add it here in the same change.

- Upstream: imputnet/helium releases and changes Spectra should
  absorb, and the state of Spectra's patch layer against them.
- Platform repos: luinbytes/spectra-linux exists and has its own
  AGENTS.md. Rule changes here should be considered for it, and
  vice versa, in the same piece of work, so the two never drift
  apart unnoticed. Any future platform repo joins this list when it
  is created.
- Workflows and the versions of the actions they use.
- Open branches and PRs: anything untouched for about two weeks
  gets a decision, per the branch rules above.
- Open issues: anything with no activity and no owner gets triaged,
  closed with a reason, or picked up.
- The README watch list above: every statement still true, every
  trigger still ahead of us rather than behind us.
- Pins and inputs that age: Chromium version references, GN flags,
  and any version pinned anywhere in the repo.

## Repository hygiene

- No build output, archives, or generated artifacts get committed.
  If a build product needs keeping, it belongs on a release, not in
  git. If something generated does belong in the repo, its PR says
  why and how it is regenerated.
- Keep the patch series tidy and ordered; a patch that no longer
  applies is fixed or removed in the change that breaks it, never
  left failing for the next person.
- Big or binary additions need a reason stated in the PR. Repo size
  is a cost every clone pays forever.
