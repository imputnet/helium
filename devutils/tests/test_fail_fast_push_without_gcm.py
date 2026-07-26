# -*- coding: UTF-8 -*-

# Copyright 2026 The Helium Authors
# You can use, redistribute, and/or modify this source code under
# the terms of the GPL-3.0 license that can be found in the LICENSE file.
"""Test fail-fast-push-without-gcm.patch"""

import logging
import subprocess
import tempfile
from pathlib import Path

ENCODING = 'UTF-8'


def test_fail_fast_push_without_gcm():
    """Test fail-fast-push-without-gcm.patch"""

    logging.basicConfig(level=logging.DEBUG)
    log = logging.getLogger('ungoogled')

    patches_dir = Path(__file__).resolve().parents[2] / 'patches'
    series_path = patches_dir / 'series'
    patch_path = patches_dir / 'helium/core/fail-fast-push-without-gcm.patch'
    patch_name = 'helium/core/fail-fast-push-without-gcm.patch'
    prior_name = 'helium/core/fix-instance-id-stuck.patch'

    fixture = """}

GCMClient::Result GCMDriverDesktop::EnsureStarted(
    GCMClient::StartMode start_mode) {
  DCHECK(ui_thread_->RunsTasksInCurrentSequence());

  if (gcm_started_)
    return GCMClient::SUCCESS;

  // Have any app requested the service?
  if (app_handlers().empty())
    return GCMClient::UNKNOWN_ERROR;

  if (!delayed_task_controller_)
    delayed_task_controller_ = std::make_unique<GCMDelayedTaskController>();

  // Note that we need to pass weak pointer again since the existing weak
  // pointer in IOWorker might have been invalidated when GCM is stopped.
  io_thread_->PostTask(
      FROM_HERE, base::BindOnce(&GCMDriverDesktop::IOWorker::Start,
                                base::Unretained(io_worker_.get()), start_mode,
                                weak_ptr_factory_.GetWeakPtr(),
                                /*time_task_posted=*/base::TimeTicks::Now()));

  return GCMClient::SUCCESS;
}

void GCMDriverDesktop::RemoveCachedData() {
}
"""

    log.info('Check series placement')
    series = [
        line.strip() for line in series_path.read_text(encoding=ENCODING).splitlines()
        if line.strip() and not line.strip().startswith('#')
    ]
    assert patch_name in series
    assert series.index(patch_name) == series.index(prior_name) + 1

    log.info('Check patch returns GCM_DISABLED')
    patch_content = patch_path.read_text(encoding=ENCODING)
    assert 'GCMDriverDesktop::EnsureStarted' in patch_content
    assert patch_content.count('+  return GCMClient::GCM_DISABLED;') == 1
    assert '-  return GCMClient::SUCCESS;' in patch_content

    log.info('Check patch applies to EnsureStarted fixture')
    with tempfile.TemporaryDirectory() as tmpdirname:
        root = Path(tmpdirname)
        target = root / 'components/gcm_driver/gcm_driver_desktop.cc'
        target.parent.mkdir(parents=True)
        target.write_text(fixture, encoding=ENCODING)

        local_patch_lines = []
        for line in patch_content.splitlines(keepends=True):
            if line.startswith('@@'):
                local_patch_lines.append('@@ -1,28 +1,10 @@\n')
            else:
                local_patch_lines.append(line)
        local_patch = root / 'test.patch'
        local_patch.write_text(''.join(local_patch_lines), encoding=ENCODING)

        dry = subprocess.run(['patch', '-p1', '--dry-run', '-i',
                              str(local_patch)],
                             cwd=root,
                             capture_output=True,
                             text=True,
                             check=False)
        assert dry.returncode == 0, dry.stdout + dry.stderr

        applied = subprocess.run(['patch', '-p1', '-i',
                                  str(local_patch)],
                                 cwd=root,
                                 capture_output=True,
                                 text=True,
                                 check=False)
        assert applied.returncode == 0, applied.stdout + applied.stderr
        patched = target.read_text(encoding=ENCODING)
        assert 'return GCMClient::GCM_DISABLED;' in patched
        assert 'delayed_task_controller_ = std::make_unique' not in patched


if __name__ == '__main__':
    test_fail_fast_push_without_gcm()
