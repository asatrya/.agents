---
name: video-transcript
description: Download or generate a transcript from a YouTube or Instagram URL. Use this skill whenever the user provides a social-media video, Reel, Short, or post link and asks for a transcript, subtitles, captions, transcription, or the spoken text—even if they do not mention yt-dlp or Whisper. Prefer captions downloaded with yt-dlp; only download media and run Whisper when no usable captions are available.
compatibility: Requires shell access to yt-dlp, Whisper CLI, ffmpeg, and Python 3 for caption cleanup. The skill checks these dependencies before doing any network or media work.
---

# Video transcript

Turn a public or user-authorized YouTube or Instagram link into a readable transcript. Use the cheapest reliable source first: platform captions are faster, smaller, and usually preserve the creator's wording better than a new transcription. Use Whisper only when the platform does not expose usable captions.

## Output contract

Unless the user gives an output path, create a directory in the current working directory named `video-transcript-<short-slug>/` and leave these files there:

- `transcript.txt` — the clean, readable transcript.
- `captions.srt` or `captions.vtt` — the downloaded caption file when captions were available.
- `metadata.json` — optional source metadata if `yt-dlp --dump-single-json` succeeds.

Keep downloaded media in a temporary directory and remove it after a successful transcript unless the user explicitly asks to keep the video/audio. Preserve the source caption file because it makes the result auditable. If the user asks for timestamps, also keep or generate an SRT/VTT file and do not return only plain text.

## Workflow

### 1. Validate the request and preflight every dependency

Accept a single YouTube or Instagram URL. Use `--no-playlist` so a link to a collection does not unexpectedly download many items. Do not bypass access controls or ask the user to paste passwords/cookies into chat.

Run this check before attempting the URL. The check is intentionally first because a missing tool should be reported before spending time on network requests:

```bash
set -eu

for tool in yt-dlp whisper ffmpeg python3; do
  if ! command -v "$tool" >/dev/null 2>&1; then
    echo "Missing required tool: $tool" >&2
    exit 1
  fi
done

yt-dlp --version
whisper --help >/dev/null
ffmpeg -version >/dev/null
python3 --version
```

If `yt-dlp` or `whisper` is missing, stop and tell the user exactly which executable is missing. Do not silently install packages. If Whisper's CLI is present but its help command fails, treat Whisper as unusable and report that. `ffmpeg` is required for audio extraction and some subtitle conversions.

### 2. Create an isolated work area and inspect the source

Use a temporary directory for intermediate files and an explicit output directory for deliverables. Quote the URL and every path because titles and temporary directories can contain spaces.

```bash
WORK="$(mktemp -d "${TMPDIR:-/tmp}/video-transcript.XXXXXX")"
OUT="$(pwd)/video-transcript-<short-slug>"
mkdir -p "$OUT"

if ! yt-dlp --no-playlist --dump-single-json --skip-download \
  --output "$WORK/source.%(ext)s" \
  "<URL>" >"$OUT/metadata.json"; then
  rm -f "$OUT/metadata.json"
fi

yt-dlp --no-playlist --list-subs --skip-download "<URL>" || \
  echo "Subtitle listing unavailable; continue with the caption probes and authorized fallback."
```

Use the subtitle listing to choose a language. Prefer the user's requested language. Otherwise prefer English (`en`, `en.*`) and, if English is not listed, use the first available language and clearly report that choice. Do not silently translate a transcript.

### 3. Try downloadable manual captions first

Set `SUB_LANGS` to the selected language code(s), for example `en.*,en` or `de,de.*`. Download captions without downloading the media:

```bash
SUB_LANGS="en.*,en"
yt-dlp --no-playlist --skip-download \
  --write-subs \
  --sub-langs "$SUB_LANGS" \
  --sub-format "srt/vtt/best" \
  --convert-subs srt \
  --output "$WORK/caption.%(ext)s" \
  "<URL>"
```

Look for a newly created `.srt` or `.vtt` file under `$WORK`. A successful exit code alone is not proof that a caption file was created. If a manual caption file exists, use it and skip the auto-caption and Whisper branches.

### 4. If needed, try platform-generated captions

Only if the manual-caption attempt produced no caption file, retry with auto-generated captions:

```bash
yt-dlp --no-playlist --skip-download \
  --write-auto-subs \
  --sub-langs "$SUB_LANGS" \
  --sub-format "srt/vtt/best" \
  --convert-subs srt \
  --output "$WORK/caption.%(ext)s" \
  "<URL>"
```

Treat an auto-caption file as a valid transcript source, but label the result as auto-generated. If the preferred language is unavailable and the listing shows another usable language, retry with that exact language code before falling back to Whisper.

### 5. Normalize a downloaded caption file

When a caption file exists, copy it to the output directory as `captions.srt` (or preserve `.vtt` if conversion was not possible), then run the bundled helper to remove cue numbers, timestamps, markup, and adjacent duplicate cues:

```bash
cp "$CAPTION_FILE" "$OUT/captions.${CAPTION_FILE##*.}"
python3 "/Users/autama/.agents/skills/video-transcript/scripts/captions_to_text.py" \
  "$CAPTION_FILE" --output "$OUT/transcript.txt"
```

If the skill is copied or packaged elsewhere, resolve the helper relative to the skill's own directory rather than hard-coding the example path. Verify that `transcript.txt` is non-empty before declaring success.

### 6. Fall back to Whisper only when no usable captions exist

Download the best available audio track first. This is faster and uses much less disk than downloading video; it still satisfies the transcription need. If the user explicitly requests the video, or audio-only download fails, use the best combined video/audio format instead.

```bash
yt-dlp --no-playlist \
  --format "ba[ext=m4a]/ba/best/b" \
  --output "$WORK/media.%(ext)s" \
  "<URL>"
```

Find the actual media file under `$WORK` rather than assuming its extension. Run Whisper with `--task transcribe` and a sensible model:

```bash
whisper "$MEDIA_FILE" \
  --model small \
  --task transcribe \
  --output_dir "$WORK/whisper" \
  --output_format txt
```

Use `base` for a quick draft, `small` as the default quality/speed balance, and `medium` or `large` when the user prioritizes accuracy and accepts more download time and memory use. If the language is known, pass `--language <code>`; otherwise let Whisper detect it. If Whisper fails on a CPU because of half-precision, retry once with `--fp16 False`.

Copy the generated `.txt` file to `$OUT/transcript.txt`. If timestamps were requested, run Whisper with `--output_format srt` (or `all`) and copy the resulting SRT as well.

### 7. Report provenance and limitations

Before finishing:

1. Confirm that `transcript.txt` exists and is not empty.
2. State the method: manual captions, auto-generated captions, or Whisper, including the language and Whisper model when applicable.
3. Mention if the transcript may be imperfect because the source was auto-captioned, noisy, music-heavy, multilingual, or inaccessible.
4. Remove temporary media after the output is verified unless the user asked to retain it.
5. If access is denied or login is required, explain that the public/authorized download could not proceed. If the user explicitly authorizes use of an existing browser session, use the platform-supported `yt-dlp` cookie option without exposing credentials; otherwise stop rather than attempting to bypass the restriction.

Use this concise final structure:

```text
Transcript created: <absolute path>
Method: <manual captions | auto-generated captions | Whisper <model>>
Language: <language or detected language>
Notes: <only relevant caveats>
```

## Common failure handling

- **No subtitles listed:** proceed directly to the Whisper fallback.
- **Caption download returns no file:** do not infer success from exit status; try the auto-caption branch, then Whisper.
- **Instagram login/age/location restriction:** report the restriction and ask for an authorized, already-available access method; never request credentials in the transcript workflow.
- **Playlist or carousel unexpectedly appears:** keep `--no-playlist` and ask the user which individual URL they want.
- **Whisper model download is blocked:** report that the model is unavailable and return any downloaded caption file; do not claim that transcription completed.
