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
