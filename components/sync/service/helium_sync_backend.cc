// Copyright 2026 The Helium Authors
// You can use, redistribute, and/or modify this source code under
// the terms of the GPL-3.0 license that can be found in the LICENSE file.

#include <memory>
#include "components/sync/service/helium_sync_backend.h"
#include "components/sync/engine/custom_sync_backend.h"

namespace syncer {

// Default no-op implementation. Embedders should provide their own
// implementation (in the browser/Helium layer) that returns a functional
// CustomSyncBackend. The default returns nullptr so that the tree builds when
// no provider is configured.
std::unique_ptr<CustomSyncBackend> CreateHeliumCustomSyncBackend() {
  return nullptr;
}

}  // namespace syncer
