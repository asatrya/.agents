#!/usr/bin/env bash
# Export an HTML slide deck to PDF with DeckTape.
# Installs Node.js (via Homebrew on macOS) and decktape when missing.
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: export-pdf.sh [options] <html-file-or-url>

Options:
  -o, --output PATH     Output PDF path (default: same dir/name as the HTML)
  -s, --size WxH        Viewport size, e.g. 1920x1080
  --slides RANGE        Slide range, e.g. 1-3,5,8
  --plugin NAME         DeckTape plugin (default: auto-detect, else reveal)
  --pause MS            Pause before each slide (default: decktape default)
  --chrome-path PATH    Chrome/Chromium executable
  -h, --help            Show this help

Examples:
  export-pdf.sh ./deck.html
  export-pdf.sh -o /tmp/talk.pdf ./slides/index.html
  export-pdf.sh --size 1920x1080 https://example.com/talk/
EOF
}

html_source=""
output=""
size=""
slides=""
plugin=""
pause=""
chrome_path=""
extra_args=()

while [[ $# -gt 0 ]]; do
  case "$1" in
    -h|--help)
      usage
      exit 0
      ;;
    -o|--output)
      output="${2:?--output requires a path}"
      shift 2
      ;;
    -s|--size)
      size="${2:?--size requires WxH}"
      shift 2
      ;;
    --slides)
      slides="${2:?--slides requires a range}"
      shift 2
      ;;
    --plugin)
      plugin="${2:?--plugin requires a name}"
      shift 2
      ;;
    --pause)
      pause="${2:?--pause requires milliseconds}"
      shift 2
      ;;
    --chrome-path)
      chrome_path="${2:?--chrome-path requires a path}"
      shift 2
      ;;
    --)
      shift
      extra_args+=("$@")
      break
      ;;
    -*)
      echo "Unknown option: $1" >&2
      usage >&2
      exit 2
      ;;
    *)
      if [[ -n "$html_source" ]]; then
        echo "Only one HTML source is allowed. Got '$html_source' and '$1'." >&2
        exit 2
      fi
      html_source="$1"
      shift
      ;;
  esac
done

if [[ -z "$html_source" ]]; then
  echo "Missing HTML source. Pass a local .html file or a URL." >&2
  usage >&2
  exit 2
fi

install_node() {
  if command -v node >/dev/null 2>&1 && command -v npm >/dev/null 2>&1; then
    return 0
  fi

  echo "Node.js / npm not found. Installing..." >&2

  if [[ "$(uname -s)" == "Darwin" ]] && command -v brew >/dev/null 2>&1; then
    brew install node
  elif command -v apt-get >/dev/null 2>&1; then
    sudo apt-get update
    sudo apt-get install -y nodejs npm
  else
    echo "Could not install Node.js automatically. Install Node.js 18+ from https://nodejs.org/ then retry." >&2
    exit 1
  fi

  if ! command -v node >/dev/null 2>&1 || ! command -v npm >/dev/null 2>&1; then
    echo "Node.js / npm still not available after install." >&2
    exit 1
  fi
}

ensure_decktape() {
  cache_dir="${XDG_CACHE_HOME:-$HOME/.cache}/revealjs-pdf"
  mkdir -p "$cache_dir"
  decktape_bin="$cache_dir/node_modules/.bin/decktape"

  if command -v decktape >/dev/null 2>&1; then
    echo "decktape"
    return 0
  fi

  if [[ -x "$decktape_bin" ]]; then
    echo "$decktape_bin"
    return 0
  fi

  echo "decktape not found. Installing locally to $cache_dir ..." >&2
  npm install --prefix "$cache_dir" decktape >&2

  if [[ ! -x "$decktape_bin" ]]; then
    echo "decktape install succeeded but the binary is missing at $decktape_bin" >&2
    exit 1
  fi

  echo "$decktape_bin"
}

is_url() {
  [[ "$1" == http://* || "$1" == https://* || "$1" == file://* ]]
}

to_file_uri() {
  python3 - "$1" <<'PY'
import pathlib, sys
print(pathlib.Path(sys.argv[1]).expanduser().resolve().as_uri())
PY
}

detect_plugin() {
  local path="$1"
  if [[ ! -f "$path" ]]; then
    echo "reveal"
    return 0
  fi
  if grep -qiE 'reveal\.js|Reveal\.initialize|class="reveal"' "$path"; then
    echo "reveal"
  else
    echo "automatic"
  fi
}

install_node
decktape_cmd="$(ensure_decktape)"

url=""
html_dir=""
html_base=""
query=""

# Allow local paths with a query string, e.g. deck.html?export
if ! is_url "$html_source" && [[ "$html_source" == *"?"* ]]; then
  query="${html_source#*?}"
  html_source="${html_source%%\?*}"
fi

if is_url "$html_source"; then
  url="$html_source"
  if [[ -z "$output" ]]; then
    echo "Output PDF path is required when the source is a URL." >&2
    echo "Pass --output /path/to/deck.pdf" >&2
    exit 2
  fi
else
  if [[ ! -e "$html_source" ]]; then
    echo "HTML file not found: $html_source" >&2
    exit 1
  fi
  if [[ -d "$html_source" ]]; then
    echo "Source is a directory, not an HTML file: $html_source" >&2
    echo "Pass the .html file path." >&2
    exit 2
  fi

  html_abs="$(python3 -c 'import pathlib,sys; print(pathlib.Path(sys.argv[1]).expanduser().resolve())' "$html_source")"
  html_dir="$(dirname "$html_abs")"
  html_base="$(basename "$html_abs")"
  url="$(to_file_uri "$html_abs")"
  if [[ -n "$query" ]]; then
    url="${url}?${query}"
  fi

  if [[ -z "$output" ]]; then
    output="${html_dir}/${html_base%.*}.pdf"
  fi

  if [[ -z "$plugin" ]]; then
    plugin="$(detect_plugin "$html_abs")"
  fi
fi

output="$(python3 -c 'import pathlib,sys; print(pathlib.Path(sys.argv[1]).expanduser().resolve())' "$output")"
mkdir -p "$(dirname "$output")"

if [[ -z "$plugin" ]]; then
  plugin="reveal"
fi

cmd=("$decktape_cmd" "$plugin")

if [[ -n "$size" ]]; then
  cmd+=(--size "$size")
fi
if [[ -n "$slides" ]]; then
  cmd+=(--slides "$slides")
fi
if [[ -n "$pause" ]]; then
  cmd+=(--pause "$pause")
fi
if [[ -n "$chrome_path" ]]; then
  cmd+=(--chrome-path "$chrome_path")
fi

# Local files need these Chrome flags so relative CSS/JS/images load and plugins can read stylesheets.
if [[ "$url" == file://* ]]; then
  cmd+=(--chrome-arg=--allow-file-access-from-files)
  cmd+=(--chrome-arg=--disable-web-security)
fi

if [[ "$(uname -s)" == "Linux" ]]; then
  cmd+=(--chrome-arg=--no-sandbox)
fi

cmd+=("${extra_args[@]}")
cmd+=("$url" "$output")

echo "Exporting with plugin '$plugin'"
echo "Source: $url"
echo "Output: $output"
echo "First run may download Chromium; this can take a few minutes."

if [[ -n "$html_dir" ]]; then
  (cd "$html_dir" && "${cmd[@]}")
else
  "${cmd[@]}"
fi

echo "Wrote $output"
