<div align="center">
    <img src="resources/branding/app_icon/raw.png"
        title="Spectra" alt="Spectra logo (placeholder, inherited from Helium)" width="120" />
    <h1>Spectra</h1>
    <p>
        A Linux-first browser with AI through the whole stack,
        built around privacy, consent, and comfort.
    </p>
    <p>
        <strong>Built on <a href="https://github.com/imputnet/helium">Helium</a> by
        <a href="https://imput.net/">imput</a>.</strong><br />
        Spectra is a fork of Helium, the private, fast, and honest
        Chromium browser. Full credit for the foundation belongs to the
        Helium project and its contributors; see the credit at the bottom
        of this page too.
    </p>
</div>

## What is Spectra?

Spectra starts from Helium and asks what a browser shaped like Arc,
with AI that actually does something, would look like on Linux.

- **Chromium under the hood, via Helium.** Full Chrome Web Store
  extension support, de-Googled, with uBlock Origin built in.
- **Linux first.** Arc never shipped for Linux. Spectra starts there.
- **A sidebar that is the browser.** Tabs, pinned sites, and Spaces
  live in the sidebar, each Space with its own band of the spectrum
  as its colour identity.
- **Deep AI, clean surface.** AI that can see context across tabs and
  Spaces (with per-Space permission), think and research across them,
  organise them, and act inside a tab with visible steps and approval
  gates. One command bar and one panel, quiet by default, and you pick
  the model.
- **Nothing disappears silently.** No tab is ever archived, renamed,
  or tidied away without you seeing it happen.

> [!NOTE]
> Spectra is at the very beginning. Right now it is a rebrand of
> Helium with a design direction, not a finished browser. The code
> here is currently Helium's, and Spectra's own changes will land on
> top of it as a clearly separated patch layer so the fork can always
> rebase onto upstream.

## Downloads

Spectra does not have its own releases yet. Until it does, use the
upstream Helium releases, which are the same browser under the hood:

> [!NOTE]
> Helium is in beta, so unexpected issues may occur.
> Please report them to the relevant project if they haven't already
> been reported.

The easiest way to download Helium is [helium.computer](https://helium.computer/).
It'll pick a compatible binary for your platform automatically.

The same releases can also be downloaded from source on GitHub:

- [Latest macOS release](https://github.com/imputnet/helium-macos/releases/latest)
- [Latest Linux release](https://github.com/imputnet/helium-linux/releases/latest)
- [Latest Windows release](https://github.com/imputnet/helium-windows/releases/latest)

Helium supports automatic updates on macOS and Windows.

## Upstream Helium repos

Spectra is built from Helium, and all Helium packaging, tooling,
services, and components are open source and published on GitHub by
imput. These repos belong to the upstream project:

### Platform packaging and tooling
- [Helium for macOS](https://github.com/imputnet/helium-macos)
- [Helium for Linux](https://github.com/imputnet/helium-linux)
- [Helium for Windows](https://github.com/imputnet/helium-windows)

### Web services
[Helium services](https://github.com/imputnet/helium-services) are Helium's
privacy-first cloud services that handle the extension proxy, !bangs, filter
lists, browser updates, crash reports, and etc. The services are self-hostable
and the repo includes exactly what imput use and host, down to Ansible playbooks.

### Components
- [Helium uBlock Origin](https://github.com/imputnet/uBlock) is a
Helium-specific fork of uBlock Origin that includes their filters, defaults, and
CNAME uncloaking.

- [Helium onboarding](https://github.com/imputnet/helium-onboarding) includes
the browser setup experience seen at `helium://setup` on first launch.

- [Helium non-free assets](https://github.com/imputnet/helium-nonfree-assets)
repo handles non-free assets used in Helium, such as search engine icons and
icons of other browsers.

### Tooling
- [Chromium tarballs](https://github.com/imputnet/chromium-tarballs) creates
prepared Chromium source archives used by Helium builds.

- [Helium Prism](https://github.com/imputnet/helium-prism) is a Svelte UI
Component library used in onboarding and the landing page.

### Legal documents
[Helium Legal](https://github.com/imputnet/helium-legal) repo includes the
source for [Terms of Use](https://helium.computer/terms) and
[Privacy Policy](https://helium.computer/privacy) documents, along with their
full change history. Those documents are Helium's and do not describe
Spectra; Spectra will publish its own before any public release.

## Development

macOS and Linux are the primary development platforms for Helium, so they're the
recommended development environment for community contributions. Spectra
development happens on Linux first.

[> See development docs in the upstream macOS repo](https://github.com/imputnet/helium-macos/blob/main/docs/building.md#development-build-and-environment)

Linux packaging includes a similar development script, so the same guide
can be applied there too.

## Contributing

Before contributing to Spectra, please read the guidelines in
[CONTRIBUTING.md](CONTRIBUTING.md), inherited from Helium for now.
If you want to contribute to the browser Spectra is built on, contribute
to [Helium](https://github.com/imputnet/helium) upstream instead.

## Credits

### Helium

Spectra exists because of [Helium](https://github.com/imputnet/helium),
by [imput](https://imput.net/) and the Helium contributors. Helium is
"the browser built around privacy, consent, and comfort", and Spectra
keeps that foundation and its GPL-3.0 license. If you like Spectra,
you like Helium, so consider supporting them.

### The Chromium project
[The Chromium Project](https://www.chromium.org/) is at the core of Helium
and Spectra, making both possible in the first place.

### ungoogled-chromium
Helium originally branched off
[ungoogled-chromium](https://github.com/ungoogled-software/ungoogled-chromium).
Special thanks to everyone behind ungoogled-chromium, they made working with
Chromium much easier.

### Other Chromium projects

Helium includes some patches from other open source Chromium projects:

- [Inox patchset](https://github.com/gcarq/inox-patchset)
- [Debian](https://tracker.debian.org/pkg/chromium-browser)
- [Bromite](https://github.com/bromite/bromite)
- [Iridium Browser](https://iridiumbrowser.de/)
- [Brave](https://github.com/brave/brave-core)

All patches are sorted by vendor in the [patches](patches/) directory of this repo.

## License

All code, patches, modified portions of imported code or patches, and
any other content that is unique to Spectra or Helium and not imported
from other repositories is licensed under GPL-3.0. See [LICENSE](LICENSE).

Any content imported from other projects retains its original license (for
example, any original unmodified code imported from ungoogled-chromium remains
licensed under their [BSD 3-Clause license](LICENSE.ungoogled_chromium)).

---

<div align="center">
    <p>
        <strong>Spectra is a fork of
        <a href="https://github.com/imputnet/helium">Helium</a>.</strong>
    </p>
    <p>
        Helium is created by <a href="https://imput.net/">imput</a> and
        released under GPL-3.0 at
        <a href="https://helium.computer/">helium.computer</a>.
        Spectra is an independent project built on their work, is not
        affiliated with or endorsed by imput or the Helium project, and
        keeps their license and this credit in place.
        Thank you to everyone who builds Helium.
    </p>
</div>
