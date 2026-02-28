<div align="center">
    <br/>
    <p>
        <img src="resources/branding/app_icon/raw.png"
            title="Zephyr" alt="Zephyr logo" width="120" />
        <h1>Zephyr</h1>
    </p>
    <p width="120">
        Community-maintained fork of Helium focused on UI improvements.
        <br>
        Helium core compatibility is intentionally preserved where possible.
    </p>
    <a href="https://github.com/quanticstudios/zephyr">
        github.com/quanticstudios/zephyr
    </a>
    <br/>
</div>

## Fork status
> [!IMPORTANT]
> Zephyr is an unofficial fork built on top of [Helium](https://github.com/imputnet/helium).
> This project keeps upstream attribution and licensing intact.
> See [FORK_NOTICE.md](FORK_NOTICE.md) for details.

## Downloads
> [!NOTE]
> Zephyr is in early development, so unexpected issues may occur. We are not responsible
for any damage caused by usage of beta software.

Zephyr release artifacts will be published in this repository:
- [Zephyr releases](https://github.com/quanticstudios/zephyr/releases)

Upstream Helium releases are still available here:
- [macOS](https://github.com/imputnet/helium-macos/releases/latest)
- [Linux](https://github.com/imputnet/helium-linux/releases/latest) (AppImage)
- [Windows](https://github.com/imputnet/helium-windows/releases/latest) (no auto-updates yet)

## Upstream platform packaging
Helium upstream is available on all major desktop platforms:
- [Helium for macOS](https://github.com/imputnet/helium-macos)
- [Helium for Linux](https://github.com/imputnet/helium-linux)
- [Helium for Windows](https://github.com/imputnet/helium-windows)

## Upstream Helium repos
Along with the main repo and platform packaging, these projects are part of Helium:
- [Helium services](https://github.com/imputnet/helium-services)
- [Helium onboarding](https://github.com/imputnet/helium-onboarding) (the onboarding page seen in Helium at `helium://setup`)
- [uBlock Origin packaging](https://github.com/imputnet/ublock-origin-crx)

## Credits
### Helium
Zephyr is built on top of [Helium](https://github.com/imputnet/helium).
We continue to credit upstream and intend to upstream applicable fixes where possible.

### ungoogled-chromium
Helium (and therefore Zephyr) is proudly based on [ungoogled-chromium](https://github.com/ungoogled-software/ungoogled-chromium).
It wouldn't be possible for us to get rid of Google's bloat and get a development+building pipeline this fast without it.
Huge shout-out to everyone behind this amazing project!
(and we intend to contribute even more stuff upstream in the future)

### The Chromium project
[The Chromium Project](https://www.chromium.org/) is obviously at the core of Helium,
making it possible to exist in the first place.

### ungoogled-chromium's dependencies
- [Inox patchset](https://github.com/gcarq/inox-patchset)
- [Debian](https://tracker.debian.org/pkg/chromium-browser)
- [Bromite](https://github.com/bromite/bromite)
- [Iridium Browser](https://iridiumbrowser.de/)

## License
All code, patches, modified portions of imported code or patches, and
any other content that is unique to this repository and not imported from other
repositories is licensed under GPL-3.0. See [LICENSE](LICENSE).

Any content imported from other projects retains its original license (for
example, any original unmodified code imported from ungoogled-chromium remains
licensed under their [BSD 3-Clause license](LICENSE.ungoogled_chromium)).

## More documentation (soon)
> [!NOTE]
> We will add more documentation along with design and motivation guidelines in the future.
All docs will be linked here along with other related content.
