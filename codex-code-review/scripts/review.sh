#!/usr/bin/env bash
#
# Codex Code Review Helper Script
#
# Usage:
#   review.sh [options]
#
# Options:
#   --staged             Review staged git changes using static diff mode
#   --uncommitted        Review staged, unstaged, and untracked changes
#   --branch <name>      Review current branch compared to base branch (default: main)
#   --commit <sha>       Review one commit
#   --files <paths>      Limit review to comma-separated files/dirs
#   --dir <path>         Limit review to one directory
#   --pr <number>        Review GitHub PR diff (requires gh CLI; static mode)
#   --security           Focus on security risks
#   --performance        Focus on performance risks
#   --static             Generate diff outside Codex and pipe it to codex exec
#   --max-bytes <n>      Max static diff bytes before refusing (default: 900000)
#   --output <file>      Save final review output
#   --model <model>      Use a specific model
#   --help               Show this help message

set -euo pipefail

RED=$'\033[0;31m'
GREEN=$'\033[0;32m'
YELLOW=$'\033[1;33m'
BLUE=$'\033[0;34m'
NC=$'\033[0m'

REVIEW_TYPE="branch"
BASE_BRANCH="main"
COMMIT_SHA=""
FILES=""
DIR=""
PR_NUMBER=""
FOCUS=""
STATIC_MODE=0
OUTPUT_FILE=""
MODEL=""
MAX_BYTES=900000

print_help() {
  sed -n '2,22p' "$0" | sed 's/^# \{0,1\}//'
}

log_info() {
  printf '%s[INFO]%s %s\n' "$BLUE" "$NC" "$1"
}

log_success() {
  printf '%s[SUCCESS]%s %s\n' "$GREEN" "$NC" "$1"
}

log_warn() {
  printf '%s[WARN]%s %s\n' "$YELLOW" "$NC" "$1"
}

log_error() {
  printf '%s[ERROR]%s %s\n' "$RED" "$NC" "$1" >&2
}

require_cmd() {
  if ! command -v "$1" >/dev/null 2>&1; then
    log_error "$1 is required but was not found on PATH."
    exit 1
  fi
}

split_paths() {
  local input="$1"
  local -n out_ref="$2"
  out_ref=()

  if [[ -z "$input" ]]; then
    return
  fi

  local old_ifs="$IFS"
  IFS=','
  read -r -a out_ref <<< "$input"
  IFS="$old_ifs"
}

focus_prompt() {
  case "$FOCUS" in
    security)
      cat <<'EOF'
Focus on concrete security risks: auth, authorization, input validation, injection, sensitive data exposure, CORS, rate limiting, unsafe file handling, and unsafe command execution.
EOF
      ;;
    performance)
      cat <<'EOF'
Focus on concrete performance risks: N+1 queries, blocking I/O, unnecessary re-render loops, expensive algorithms, excessive payloads, missing indexes, and resource leaks.
EOF
      ;;
    *)
      cat <<'EOF'
Focus on concrete findings only:
1. Breaking changes
2. API compatibility
3. Test coverage gaps
4. Documentation needs
5. Bugs, security risks, or regressions visible in the diff
EOF
      ;;
  esac
}

review_prompt() {
  cat <<EOF
Review the provided code changes.

$(focus_prompt)

Report findings first, ordered by severity. Include file and line references when available.
If there are no actionable findings in the reviewed scope, say so directly and mention residual risk.
EOF
}

parse_args() {
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --staged)
        REVIEW_TYPE="staged"
        STATIC_MODE=1
        shift
        ;;
      --uncommitted)
        REVIEW_TYPE="uncommitted"
        shift
        ;;
      --branch)
        REVIEW_TYPE="branch"
        BASE_BRANCH="${2:?--branch requires a value}"
        shift 2
        ;;
      --commit)
        REVIEW_TYPE="commit"
        COMMIT_SHA="${2:?--commit requires a value}"
        shift 2
        ;;
      --files)
        FILES="${2:?--files requires a comma-separated value}"
        shift 2
        ;;
      --dir)
        DIR="${2:?--dir requires a value}"
        shift 2
        ;;
      --pr)
        REVIEW_TYPE="pr"
        PR_NUMBER="${2:?--pr requires a value}"
        STATIC_MODE=1
        shift 2
        ;;
      --security)
        FOCUS="security"
        shift
        ;;
      --performance)
        FOCUS="performance"
        shift
        ;;
      --static)
        STATIC_MODE=1
        shift
        ;;
      --max-bytes)
        MAX_BYTES="${2:?--max-bytes requires a value}"
        shift 2
        ;;
      --output)
        OUTPUT_FILE="${2:?--output requires a value}"
        shift 2
        ;;
      --model)
        MODEL="${2:?--model requires a value}"
        shift 2
        ;;
      --help|-h)
        print_help
        exit 0
        ;;
      *)
        log_error "Unknown option: $1"
        print_help
        exit 1
        ;;
    esac
  done
}

build_codex_exec_cmd() {
  local -n cmd_ref="$1"
  cmd_ref=(codex exec --sandbox read-only)

  if [[ -n "$MODEL" ]]; then
    cmd_ref+=(--model "$MODEL")
  fi

  if [[ -n "$OUTPUT_FILE" ]]; then
    cmd_ref+=(-o "$OUTPUT_FILE")
  fi

  cmd_ref+=(--cd "$(pwd)")
}

build_codex_review_cmd() {
  local -n cmd_ref="$1"
  cmd_ref=(codex review)

  if [[ -n "$MODEL" ]]; then
    cmd_ref+=(-c "model=\"$MODEL\"")
  fi

  if [[ -n "$OUTPUT_FILE" ]]; then
    return 1
  fi

  case "$REVIEW_TYPE" in
    uncommitted)
      cmd_ref+=(--uncommitted)
      ;;
    branch)
      cmd_ref+=(--base "$BASE_BRANCH")
      ;;
    commit)
      cmd_ref+=(--commit "$COMMIT_SHA")
      ;;
    *)
      return 1
      ;;
  esac

  return 0
}

make_static_diff() {
  local diff_file="$1"
  local -a pathspecs=()
  local -a file_paths=()

  split_paths "$FILES" file_paths

  if [[ -n "$DIR" ]]; then
    pathspecs+=("$DIR")
  fi

  if [[ ${#file_paths[@]} -gt 0 ]]; then
    pathspecs+=("${file_paths[@]}")
  fi

  case "$REVIEW_TYPE" in
    staged)
      if [[ ${#pathspecs[@]} -gt 0 ]]; then
        git diff --cached --no-ext-diff --unified=80 -- "${pathspecs[@]}" > "$diff_file"
      else
        git diff --cached --no-ext-diff --unified=80 > "$diff_file"
      fi
      ;;
    uncommitted)
      if [[ ${#pathspecs[@]} -gt 0 ]]; then
        git diff HEAD --no-ext-diff --unified=80 -- "${pathspecs[@]}" > "$diff_file"
      else
        git diff HEAD --no-ext-diff --unified=80 > "$diff_file"
      fi
      ;;
    branch)
      if [[ ${#pathspecs[@]} -gt 0 ]]; then
        git diff --no-ext-diff --unified=80 "$BASE_BRANCH"...HEAD -- "${pathspecs[@]}" > "$diff_file"
      else
        git diff --no-ext-diff --unified=80 "$BASE_BRANCH"...HEAD > "$diff_file"
      fi
      ;;
    commit)
      git show --no-ext-diff --unified=80 --format=medium "$COMMIT_SHA" > "$diff_file"
      ;;
    pr)
      require_cmd gh
      gh pr diff "$PR_NUMBER" > "$diff_file"
      ;;
    *)
      log_error "Static diff mode does not support review type: $REVIEW_TYPE"
      exit 1
      ;;
  esac
}

run_static_review() {
  local diff_file
  diff_file="$(mktemp)"

  make_static_diff "$diff_file"

  local bytes
  bytes="$(wc -c < "$diff_file" | tr -d ' ')"

  if [[ "$bytes" -eq 0 ]]; then
    log_warn "No diff found for the selected scope."
    return 0
  fi

  log_info "Static diff size: $bytes bytes"

  if [[ "$bytes" -gt "$MAX_BYTES" ]]; then
    log_error "Diff is too large for static Codex review ($bytes bytes > $MAX_BYTES bytes)."
    log_error "Narrow the scope with --files, --dir, --commit, or raise --max-bytes if you know it will fit."
    return 2
  fi

  local -a cmd
  build_codex_exec_cmd cmd

  log_info "Running static diff review with codex exec..."
  local status=0
  "${cmd[@]}" "$(review_prompt)" < "$diff_file" || status=$?
  rm -f "$diff_file"
  return "$status"
}

run_native_review() {
  local -a cmd

  if ! build_codex_review_cmd cmd; then
    log_warn "Native review does not support this scope. Falling back to static diff mode."
    run_static_review
    return
  fi

  log_info "Running native Codex review..."
  "${cmd[@]}"
}

main() {
  parse_args "$@"
  require_cmd codex
  require_cmd git

  if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    log_error "Run this from inside a git repository."
    exit 1
  fi

  log_info "Review type: $REVIEW_TYPE"
  [[ -n "$FOCUS" ]] && log_info "Focus: $FOCUS"

  if [[ "$STATIC_MODE" -eq 1 || -n "$FILES" || -n "$DIR" ]]; then
    run_static_review
  else
    run_native_review
  fi

  log_success "Review command finished."
}

main "$@"
