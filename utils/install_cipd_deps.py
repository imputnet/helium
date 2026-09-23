#!/usr/bin/env python3
"""Install the selected Chromium CIPD tools for this build host."""

from concurrent.futures import ThreadPoolExecutor

import argparse
import pathlib
import platform
import subprocess
import sys


def dependency_paths(host_os, host_cpu, remote_exec=False):
    """Select host tools and optional Linux remote-worker tools."""
    cpu = host_cpu.lower()
    if cpu in ("arm64", "aarch64"):
        arch = "arm64"
    elif cpu in ("x86_64", "amd64", "x64"):
        arch = "amd64"
    else:
        raise ValueError(f"Unsupported build CPU: {host_cpu}")

    if host_os == "linux":
        gn_dep = "src/buildtools/linux64"
        typescript = "src/third_party/typescript/linux-amd64/src"
    elif host_os == "darwin":
        gn_dep = "src/buildtools/mac"
        typescript = f"src/third_party/typescript/mac-{arch}/src"
    elif host_os == "win32":
        gn_dep = "src/buildtools/win"
        typescript = "src/third_party/typescript/windows-amd64/src"
    else:
        raise ValueError(f"Unsupported build host: {host_os}")

    go_os = {"linux": "linux", "darwin": "mac", "win32": "windows"}[host_os]
    paths = [
        gn_dep, "src/third_party/siso/cipd", typescript,
        f"src/third_party/dawn/tools/golang/{go_os}-{arch}",
        "src/third_party/devtools-frontend/src/third_party/esbuild"
    ]
    if remote_exec:
        linux_typescript = "src/third_party/typescript/linux-amd64/src"
        if linux_typescript not in paths:
            paths.append(linux_typescript)
    return paths


def selected_packages(src_dir, names):
    """Yield destinations and CIPD manifests for the selected DEPS entries."""
    sys.path.insert(0, str(src_dir / "third_party/depot_tools"))
    import gclient_eval # pylint: disable=import-outside-toplevel,import-error

    deps_file = src_dir / "DEPS"
    deps = gclient_eval.Parse(deps_file.read_text(), str(deps_file))["deps"]
    for directory in ("third_party/dawn", "third_party/devtools-frontend/src"):
        deps_file = src_dir / directory / "DEPS"
        nested_deps = gclient_eval.Parse(deps_file.read_text(), str(deps_file))["deps"]
        deps.update({f"src/{directory}/{name}": dep for name, dep in nested_deps.items()})
    for name in names:
        dep = deps[name]
        if dep.get("dep_type") != "cipd":
            raise ValueError(f"Not a CIPD dependency: {name}")
        # Explicit selection overrides DEPS conditions such as non_git_source.
        destination = src_dir.joinpath(*pathlib.PurePosixPath(name).parts[1:])
        manifest = "".join(f"{package['package']} {package['version']}\n"
                           for package in dep["packages"])
        yield destination, manifest


def install(cipd, destination, manifest):
    """Install one selected CIPD dependency."""
    destination.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [str(cipd), "ensure", "-root",
         str(destination), "-ensure-file", "-"],
        input=manifest,
        text=True,
        check=True,
    )


def main():
    """Install host tools and any requested remote-worker tools."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("src_dir", type=pathlib.Path)
    parser.add_argument("--remote-exec", action="store_true")
    args = parser.parse_args()

    src_dir = args.src_dir.resolve()
    cipd_name = "cipd.bat" if sys.platform == "win32" else "cipd"
    cipd = src_dir / "third_party/depot_tools" / cipd_name
    names = dependency_paths(sys.platform, platform.machine(), args.remote_exec)
    packages = list(selected_packages(src_dir, names))
    # Windows' cipd.bat bootstraps a shared client on first use.
    workers = 1 if sys.platform == "win32" else min(4, len(packages))
    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = [
            executor.submit(install, cipd, destination, manifest)
            for destination, manifest in packages
        ]
        for future in futures:
            future.result()


if __name__ == "__main__":
    main()
