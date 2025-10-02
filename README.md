<div align="center">
    <br/>
    <p>
        <img src="resources/branding/app_icon/raw.png"
            title="Helium" alt="Helium logo" width="120" />
        <h1>Helium</h1>
    </p>
    <p width="120">
        The Chromium-based web browser made for people, with love.
        <br>
        Best privacy by default, unbiased ad-blocking, no bloat and no noise.
    </p>
    <a href="https://helium.computer/">
        helium.computer
    </a>
    <br/>
</div>

## Downloads
> [!NOTE]
> Helium is still in beta, so unexpected issues may occur. We are not responsible
for any damage caused by usage of beta software.

Best way to download Helium is to open [helium.computer](https://helium.computer/) on your computer.
It'll pick the right build for your OS and architecture automatically.

If you wish to download builds "straight from the tap" with all options in one place,
you can do it on GitHub in the Releases section in each platform's repo:
- [macOS](https://github.com/imputnet/helium-macos/releases/latest)
- [Linux](https://github.com/imputnet/helium-linux/releases/latest) (AppImage)
- [Windows](https://github.com/imputnet/helium-windows/releases/latest) (no auto-updates yet)

## Platform packaging
Helium is available on all major desktop platforms, with entirety of source code
for all of them published here:
- [Helium for macOS](https://github.com/imputnet/helium-macos)
- [Helium for Linux](https://github.com/imputnet/helium-linux)
- [Helium for Windows](https://github.com/imputnet/helium-windows)

## Other Helium repos
Along with the main repo and platform packaging, these projects are also a part of Helium:
- [Helium services](https://github.com/imputnet/helium-services)
- [Helium onboarding](https://github.com/imputnet/helium-onboarding) (the onboarding page seen in Helium at `helium://setup`)
- [uBlock Origin packaging](https://github.com/imputnet/ublock-origin-crx)

## Credits
### ungoogled-chromium
Helium is proudly based on [ungoogled-chromium](https://github.com/ungoogled-software/ungoogled-chromium).
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
any other content that is unique to Helium and not imported from other
repositories is licensed under GPL-3.0. See [LICENSE](LICENSE).

Any content imported from other projects retains its original license (for
example, any original unmodified code imported from ungoogled-chromium remains
licensed under their [BSD 3-Clause license](LICENSE.ungoogled_chromium)).

## More documentation (soon)
> [!NOTE]
> We will add more documentation along with design and motivation guidelines in the future.
All docs will be linked here along with other related content.
