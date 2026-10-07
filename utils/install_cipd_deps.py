#!/usr/bin/env python3
"""Install the selected Chromium build dependencies for this build host."""

import argparse
from concurrent.futures import ThreadPoolExecutor
import os
from pathlib import Path, PurePosixPath
import platform
import subprocess
import sys

HOST_OS = {"darwin": "mac", "linux": "linux", "win32": "win"}


def normalize_cpu(host_cpu):
    """Return Chromium's canonical name for a host CPU."""
    cpu = host_cpu.lower()
    if cpu in ("arm64", "aarch64"):
        return "arm64"
    if cpu in ("x86_64", "amd64"):
        return "x64"
    raise ValueError(f"Unsupported build CPU: {host_cpu}")


def dependency_paths(host_os, host_cpu, remote_exec=False):
    """Select host tools and optional Linux remote-worker tools."""
    arch = "arm64" if normalize_cpu(host_cpu) == "arm64" else "amd64"

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


def load_chromium_modules(src_dir):
    """Load checkout-relative Chromium modules after src_dir is known."""
    sys.path.insert(0, str(src_dir / "third_party/depot_tools"))
    import gclient_eval # pylint: disable=import-outside-toplevel,import-error
    import gclient # pylint: disable=import-outside-toplevel,import-error
    return gclient_eval, gclient


def load_deps(src_dir, gclient_eval):
    """Load the DEPS entries used by this installer."""
    deps_file = src_dir / "DEPS"
    deps = gclient_eval.Parse(deps_file.read_text(), str(deps_file))["deps"]
    for directory in ("third_party/dawn", "third_party/devtools-frontend/src"):
        deps_file = src_dir / directory / "DEPS"
        nested_deps = gclient_eval.Parse(deps_file.read_text(), str(deps_file))["deps"]
        deps.update({f"src/{directory}/{name}": dep for name, dep in nested_deps.items()})
    return deps


def selected_packages(src_dir, deps, names):
    """Yield destinations and CIPD manifests for the selected DEPS entries."""
    for name in names:
        dep = deps[name]
        if dep.get("dep_type") != "cipd":
            raise ValueError(f"Not a CIPD dependency: {name}")
        # Explicit selection overrides DEPS conditions such as non_git_source.
        destination = src_dir.joinpath(*PurePosixPath(name).parts[1:])
        manifest = "".join(f"{package['package']} {package['version']}\n"
                           for package in dep["packages"])
        yield destination, manifest


def install_cipd(cipd, destination, manifest):
    """Install one selected CIPD dependency."""
    destination.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [str(cipd), "ensure", "-root",
         str(destination), "-ensure-file", "-"],
        input=manifest,
        text=True,
        check=True,
    )


def selected_libclang(deps, gclient_eval, host_os, host_cpu):
    """Return the host libclang object selected by Chromium's DEPS."""
    dep = deps["src/third_party/llvm-libclang"]
    variables = {
        "host_os": HOST_OS[host_os],
        "host_cpu": normalize_cpu(host_cpu),
        "non_git_source": True,
    }
    objects = [
        obj for obj in dep["objects"]
        if gclient_eval.EvaluateCondition(obj.get("condition", "True"), variables)
    ]
    if len(objects) != 1:
        raise ValueError(f"Expected one libclang package for {host_os}/{host_cpu}")
    return dep, objects[0]


def install_libclang(src_dir, dep, gcs_object, gclient):
    """Install libclang with depot_tools' archive verification and extraction."""
    client = gclient.GClient(str(src_dir), argparse.Namespace(deps_os=None))
    dependency = gclient.GcsDependency(
        parent=client,
        name="third_party/llvm-libclang",
        bucket=dep["bucket"],
        object_name=gcs_object["object_name"],
        sha256sum=gcs_object["sha256sum"],
        output_file=gcs_object.get("output_file"),
        size_bytes=gcs_object["size_bytes"],
        gcs_root=client.GetGcsRoot(),
        custom_vars={},
        should_process=True,
        relative=False,
        condition=None,
    )
    dependency.DownloadGoogleStorage()


def main():
    """Install host tools and any requested remote-worker tools."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("src_dir", type=Path)
    parser.add_argument("--remote-exec", action="store_true")
    args = parser.parse_args()

    src_dir = args.src_dir.resolve()
    os.environ["PATH"] = (str(src_dir / "third_party/depot_tools") + os.pathsep +
                          os.environ.get("PATH", ""))
    gclient_eval, gclient = load_chromium_modules(src_dir)
    deps = load_deps(src_dir, gclient_eval)
    cipd = src_dir / "third_party/depot_tools" / ("cipd.bat" if sys.platform == "win32" else "cipd")
    host_cpu = platform.machine()
    packages = list(
        selected_packages(src_dir, deps, dependency_paths(sys.platform, host_cpu,
                                                          args.remote_exec)))
    libclang_dep, libclang = selected_libclang(deps, gclient_eval, sys.platform, host_cpu)
    # Windows' cipd.bat bootstraps a shared client on first use.
    workers = 1 if sys.platform == "win32" else min(4, len(packages) + 1)
    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = [
            executor.submit(install_cipd, cipd, destination, manifest)
            for destination, manifest in packages
        ]
        futures.append(executor.submit(install_libclang, src_dir, libclang_dep, libclang, gclient))
        for future in futures:
            future.result()


if __name__ == "__main__":
    main()
