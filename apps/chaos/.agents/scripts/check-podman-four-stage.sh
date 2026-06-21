#!/usr/bin/env bash
# 使用四段一致性模型检查 Podman 环境：入口 -> 实例 -> 指向 -> 任务。
# 自动修复范围：
# - 没有 running machine 时启动默认 Podman machine；
# - default connection 未指向 running machine 时自动切换。
set -euo pipefail

AUTO_FIXES=()
STAGE_ENTRY='PENDING'
STAGE_INSTANCE='PENDING'
STAGE_POINTER='PENDING'
STAGE_TASK='PENDING'

log_ok() { printf '[OK] %s\n' "$1"; }
log_warn() { printf '[WARN] %s\n' "$1"; }
log_fail() { printf '[FAIL] %s\n' "$1" >&2; }
log_info() { printf '[INFO] %s\n' "$1"; }
log_debug() { printf '[DEBUG] %s\n' "$1"; }
log_step() { printf '\n== %s ==\n' "$1"; }

format_command() {
    printf 'podman'
    for arg in "$@"; do
        printf ' %s' "$arg"
    done
}

run_podman_capture() {
    local output exit_code command_line
    command_line="$(format_command "$@")"
    log_debug "run: $command_line"
    set +e
    output="$(podman "$@" 2>&1)"
    exit_code=$?
    set -e
    log_debug "exit($command_line): $exit_code"
    if [ -n "$output" ]; then
        log_debug "output($command_line):"
        printf '%s\n' "$output"
    fi
    if [ "$exit_code" -ne 0 ]; then
        printf '%s' "$output"
        return "$exit_code"
    fi
    printf '%s' "$output"
}

first_running_machine() {
    log_debug 'parse running machine from: podman machine list --format {{.Name}} {{.Running}}'
    podman machine list --format '{{.Name}} {{.Running}}' 2>/dev/null | awk '$2 == "true" || $2 == "True" { sub(/[*]$/, "", $1); print $1; exit }'
}

default_machine() {
    log_debug 'parse default machine from: podman machine list --format {{.Name}} {{.Default}}'
    podman machine list --format '{{.Name}} {{.Default}}' 2>/dev/null | awk '$2 == "true" || $2 == "True" { sub(/[*]$/, "", $1); print $1; exit }'
}

has_machine_support() {
    podman machine list >/dev/null 2>&1
}

get_default_connection_name() {
    log_debug 'parse default connection from: podman system connection list --format {{.Name}} {{.Default}}'
    podman system connection list --format '{{.Name}} {{.Default}}' 2>/dev/null | awk '$2 == "true" || $2 == "True" { print $1; exit }'
}

start_machine() {
    local name="$1"
    local output exit_code
    log_info "auto-fix: ensure Podman machine '$name' is running"
    set +e
    output="$(podman machine start "$name" 2>&1)"
    exit_code=$?
    set -e
    log_debug "exit(podman machine start $name): $exit_code"
    if [ -n "$output" ]; then
        log_debug "output(podman machine start $name):"
        printf '%s\n' "$output"
    fi
    if [ "$exit_code" -ne 0 ]; then
        if printf '%s' "$output" | grep -F 'already running' >/dev/null 2>&1; then
            log_info "recoverable state: machine '$name' is already running or still transitioning to running."
            AUTO_FIXES+=("confirmed machine already running/starting: $name")
            sleep 2
            return 0
        fi
        log_fail "non-recoverable machine start failure for '$name'."
        printf '%s\n' "$output" >&2
        return "$exit_code"
    fi
    AUTO_FIXES+=("started default machine: $name")
    sleep 2
}

connection_exists() {
    local name="$1"
    log_debug "check connection exists: $name"
    if podman system connection list --format '{{.Name}}' 2>/dev/null | grep -Fx -- "$name" >/dev/null 2>&1; then
        log_debug "connection exists($name): true"
        return 0
    fi
    log_debug "connection exists($name): false"
    return 1
}

log_step '0. Script context'
log_info "timestamp: $(date -Iseconds 2>/dev/null || date)"
log_info "script: ${BASH_SOURCE[0]}"
log_info "cwd: $(pwd)"
log_info "os: $(uname -a 2>/dev/null || printf unknown)"
log_info "bash: ${BASH_VERSION:-unknown}"

log_step '1. Entry: podman CLI'
if ! command -v podman >/dev/null 2>&1; then
    STAGE_ENTRY='FAIL'
    log_fail 'podman command not found. Install Podman or fix PATH.'
    exit 127
fi
log_info "podman path: $(command -v podman)"
podman_version="$(run_podman_capture --version)"
log_ok "$podman_version"
STAGE_ENTRY='OK'

log_step '2. Instance: Podman backend or machine'
running_machine=''
default_machine_name=''
if has_machine_support; then
    log_info 'raw machine list:'
    run_podman_capture machine list >/dev/null
    running_machine="$(first_running_machine || true)"
    default_machine_name="$(default_machine || true)"
    log_info "parsed running machine: ${running_machine:-<none>}"
    log_info "parsed default machine: ${default_machine_name:-<none>}"
    if [ -n "$running_machine" ]; then
        log_ok "running machine: $running_machine"
    elif [ -n "$default_machine_name" ]; then
        log_warn "no running Podman machine found; starting default machine '$default_machine_name'."
        start_machine "$default_machine_name"
        running_machine="$(first_running_machine || true)"
        if [ -n "$running_machine" ]; then
            log_ok "running machine after auto-fix: $running_machine"
        else
            log_fail "machine '$default_machine_name' did not reach running state."
            exit 1
        fi
    else
        log_warn 'no running or default Podman machine found; this may be fine on native Linux.'
    fi
else
    log_warn 'podman machine list is unavailable or unsupported; treating this as native/service-based Podman.'
fi
STAGE_INSTANCE='OK'

log_step '3. Pointer: default connection'
default_connection="$(get_default_connection_name || true)"
log_info 'raw connection list:'
if ! run_podman_capture system connection list >/dev/null; then
    log_warn 'podman system connection list is unavailable or unsupported.'
fi
log_info "parsed default connection: ${default_connection:-<none>}"
if [ -n "$default_connection" ]; then
    log_ok "default connection: $default_connection"
else
    log_warn 'no default Podman connection found; this may be fine on native Linux.'
fi

if [ -n "$running_machine" ] && [ "$default_connection" != "$running_machine" ]; then
    if connection_exists "$running_machine"; then
        log_warn "default connection points to '${default_connection:-<none>}', switching to '$running_machine'."
        run_podman_capture system connection default "$running_machine" >/dev/null
        AUTO_FIXES+=("switched default connection: ${default_connection:-<none>} -> $running_machine")
        default_connection="$(get_default_connection_name || true)"
        log_info "default connection after auto-fix: ${default_connection:-<none>}"
        if [ "$default_connection" = "$running_machine" ]; then
            log_ok "default connection switched to $running_machine"
        else
            STAGE_POINTER='FAIL'
            log_fail "failed to switch default connection to $running_machine"
            exit 1
        fi
    else
        log_warn "running machine '$running_machine' has no matching system connection; skip auto-fix."
    fi
fi
STAGE_POINTER='OK'

log_step '4. Task: podman info and smoke command'
log_info 'run task verification: podman info'
if ! run_podman_capture info >/dev/null; then
    STAGE_TASK='FAIL'
    log_fail 'podman info failed. Backend, socket, or connection is still not usable.'
    exit 1
fi
log_ok 'podman info succeeded'

log_info 'run task verification: podman ps'
if ! run_podman_capture ps >/dev/null; then
    STAGE_TASK='FAIL'
    log_fail 'podman ps failed. Podman is reachable but basic container listing failed.'
    exit 1
fi
log_ok 'podman ps succeeded'
STAGE_TASK='OK'

log_step '5. Summary'
printf '[%s] Entry\n' "$STAGE_ENTRY"
printf '[%s] Instance\n' "$STAGE_INSTANCE"
printf '[%s] Pointer\n' "$STAGE_POINTER"
printf '[%s] Task\n' "$STAGE_TASK"
if [ "${#AUTO_FIXES[@]}" -gt 0 ]; then
    log_info 'auto-fixes applied:'
    for fix in "${AUTO_FIXES[@]}"; do
        printf -- '- %s\n' "$fix"
    done
else
    log_info 'auto-fixes applied: none'
fi

printf '\nPodman four-stage consistency check passed.\n'
