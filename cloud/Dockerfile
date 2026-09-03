# Checklist Garden cloud agent image.
#
# Thin wrapper around the official opencode image: the container's ONLY job is
# to run `opencode run` against a repo bind-mounted at /repo by the host.
# All git (clone/branch/commit/push) stays on the host.
FROM ghcr.io/anomalyco/opencode

# Best-effort: ensure git exists for opencode's VCS helpers.
# Base image may be Debian/Ubuntu (apt) or Alpine (apk) — try both, never fail the build.
RUN (command -v git >/dev/null 2>&1 && echo "git present") \
    || (apt-get update && apt-get install -y --no-install-recommends git ca-certificates && rm -rf /var/lib/apt/lists/*) \
    || (apk add --no-cache git ca-certificates)

ENTRYPOINT ["opencode"]
