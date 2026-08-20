// Copyright 2026 The Helium Authors
// You can use, redistribute, and/or modify this source code under
// the terms of the GPL-3.0 license that can be found in the LICENSE file.

#ifndef COMPONENTS_SYNC_SERVICE_HELIUM_SYNC_BACKEND_H_
#define COMPONENTS_SYNC_SERVICE_HELIUM_SYNC_BACKEND_H_

#include "components/sync/engine/custom_sync_backend.h"
#include <memory>
#include <string>

namespace syncer {

// Returns a Helium-provided CustomSyncBackend instance. The embedder (browser
// layer) can override this symbol to return a real provider that integrates
// with Helium's extension/provider. The default implementation in the
// translation unit returns nullptr so builds succeed when no provider is
// configured.
std::unique_ptr<CustomSyncBackend> CreateHeliumCustomSyncBackend();

}  // namespace syncer

#endif  // COMPONENTS_SYNC_SERVICE_HELIUM_SYNC_BACKEND_H_
