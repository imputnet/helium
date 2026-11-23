# Spectra, Agent Guidelines

These rules govern agent work in this repository, luinbytes/spectra.
Spectra is a fork of Helium (imputnet/helium). This file replaces the
upstream Helium agent guidelines in this fork. Nothing in this file
authorises contributions to upstream Helium; anything ever proposed
upstream must follow Helium's own contributor policy and Lu's explicit
instruction.

## Documentation is part of every change

- Always update README.md as needed in the same change, never as a
  follow up. If a change affects features, behaviour, branding, build
  steps, configuration, downloads, or anything a reader would rely on
  the README to describe, the README changes in the same PR.
- Always update any other relevant documentation in this repository in
  the same change too: docs files, comments that act as documentation,
  and the design notes where they exist.
- If a change genuinely needs no documentation update, say so in the
  PR description and say why. Silence is not acceptable; a reviewer
  should never have to ask whether the docs were considered.
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
