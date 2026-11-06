---
name: video-compilation-to-shorts
description: Analyze large travel-video collections and turn them into timecoded, chronological or story-driven short-form edit plans, using lightweight proxies and sampled visual/audio review when appropriate.
---

# Video Compilation to Shorts

Use this skill when the user wants to understand, organize, select, sequence, or assemble travel footage into a Reel, Short, TikTok, or other short-form travel summary. It supports plan-only analysis as well as media processing when the user explicitly asks for it.

## Operating principles

- Keep the original media untouched. Work in a separate analysis/proxy/output area.
- Treat filenames as identifiers, not proof of chronology or content. Use creation metadata, GPS, itinerary information, and visible/audio evidence together.
- Never describe a shot that has not actually been inspected. Mark uncertain interpretations as uncertain.
- Preserve exact source filename and proxy/original timecodes in every recommendation.
- When multiple recurring people appear, aim to give them reasonably balanced, recognizable exposure across the selected moments. This does not need to be strict equality: use group shots when they represent several people well, do not force weak or redundant footage, and do not count incidental passers-by as participants unless they are part of the story.
- During visual review, explicitly identify outstanding scenery and special moments—such as landmarks, views, animals, reactions, interactions, or unexpected events—alongside people coverage, so the final edit preserves memorable visual and story highlights.
- Do not include frames dominated by a close-up face. Prefer medium, wide, or group compositions that show context, and trim away close-up face frames at shot handles whenever possible.
- If the footage is inaccessible, ask for lightweight proxies, contact sheets, or representative uploads rather than guessing from filenames.
- If the request is ambiguous, default to a plan and ask only for decisions that materially change the edit, such as target platform, duration, aspect ratio, music, or narration.

## Recommended workflow

### 1. Establish the edit brief

Infer sensible defaults but state them: vertical 9:16, roughly 20–60 seconds, a clear travel arc, and a mix of visual highlights and natural sound. Confirm alternatives when relevant, such as a longer 90-second recap, landscape output, a quiet cinematic style, or a narrated itinerary.

### 2. Inventory the footage

For each video, record:

| Field | Purpose |
|---|---|
| Source filename | Stable reference to the original |
| Duration, resolution, orientation, frame rate | Editing and output decisions |
| Recording date/time | Initial chronological ordering |
| GPS/location/device metadata | Location and continuity clues |
| Proxy filename | Fast review reference |
| Notes | People, places, actions, audio, quality |

Use local media inspection tools such as `ffprobe` when available. If camera clocks conflict, prefer a supplied itinerary and visible sequence clues; document the chronology assumption.

### 3. Create time-aligned proxies for large files

Create proxies only when needed. A good default for visual analysis is 480p H.264 with AAC audio. Keep the original duration, frame timing, orientation, and audio; do not trim, speed up, or otherwise alter the proxy. Use 720p when faces, signs, or fine detail need closer inspection.

With FFmpeg, run this from the folder containing the originals. It handles common landscape and portrait files and writes separate outputs without replacing existing proxies:

```bash
mkdir -p proxies
for f in ./*.MP4 ./*.mp4 ./*.MOV ./*.mov; do
  [ -e "$f" ] || continue
  filename="${f##*/}"
  base="${filename%.*}"
  ffmpeg -hide_banner -n -i "$f" \
    -map 0:v:0 -map 0:a? -map_metadata 0 \
    -vf "scale=if(gt(iw,ih),-2,480):if(gt(iw,ih),480,-2)" \
    -c:v libx264 -preset veryfast -crf 28 -pix_fmt yuv420p \
    -c:a aac -b:a 96k -movflags +faststart \
    "proxies/${base}_proxy.mp4"
done
```

If FFmpeg is unavailable, use HandBrake with `Fast 480p30`, H.264, `Same as source` frame rate, RF 27–29, and AAC around 96 kbps. Keep a consistent suffix such as `_proxy.mp4` so original and proxy files are easy to pair.

### Proxy and segment reliability checks

Proxy creation and segment reading are not automatically reliable just because a proxy file exists. Treat them as a small data pipeline with an explicit manifest:

- Inventory originals first and assign each source a stable record containing the absolute or project-relative path, duration, stream presence, orientation, frame rate, and proxy path. Do not rely on shell glob order or filename numbering for sequence order.
- After creating proxies, validate each one with `ffprobe`: confirm that it opens, has the expected video stream, retains approximately the original duration, preserves portrait/landscape orientation, and has audio when the source has audio. Record missing, truncated, or unexpectedly short proxies instead of silently using them.
- Keep source and proxy timecodes aligned. Do not trim, speed up, change frame rate, or alter orientation while creating analysis proxies. If a proxy must be normalized for a tool, retain the original time mapping and document the conversion.
- Read candidate segments from the validated proxy/source pair using explicit filename and in/out timecodes. Generate timecoded contact sheets for broad review, then extract targeted frames around the exact candidate range; never infer a segment's content from its filename or from a single neighboring frame.
- Before a full render, run a small smoke test containing the first, middle, and last planned segments. Check that every trim produces non-empty video, that audio/video stream assumptions match across inputs, and that the test output opens before rendering the complete sequence.
- Build the final edit from the current plan and original sources (or validated time-aligned proxies), not from a previous rendered output. This prevents an old hook, omitted segment, or prior ordering decision from being carried into a recreation unintentionally.
- Normalize inputs at the concat boundary when needed: explicitly select the intended video/audio streams, reset timestamps after trimming, and make frame rate, sample rate, channel layout, pixel format, dimensions, and sample aspect ratio compatible. A visually valid clip can still fail at concat if these properties differ.
- After rendering, compare the measured output duration with the sum of the selected ranges, inspect representative frames at the opening, transitions, special moments, and ending, and run a complete decode check. Treat a successful encode alone as insufficient validation.

### 4. Perform a two-pass visual and audio review

First make a broad scan: sample frames every few seconds, generate contact sheets with visible timecodes, and use scene changes or shot boundaries to find candidate ranges. Tag unusable material such as darkness, severe blur, accidental recording, duplicates, or long static sections.

Then inspect promising ranges more closely, frame-by-frame when necessary. Evaluate:

- recognizability of the place or activity;
- focus, exposure, stability, horizon, and motion quality;
- faces, signs, landmarks, food, transport, or other story information;
- usable beginning and end points, including clean handles for cuts;
- redundancy with stronger shots;
- whether the shot works vertically, can be cropped safely, or should remain landscape.

Review audio separately. Note dialogue, reactions, narration, distinctive ambience, wind, clipping, and opportunities for J-cuts or L-cuts. Transcribe useful speech when transcription is available, but do not discard a strong silent visual solely because it lacks dialogue.

### 5. Build a timecoded clip log

Use one row per candidate segment, not merely one row per file:

| Source | In–out | What is visible/heard | Quality | Story role | Decision |
|---|---:|---|---|---|---|
| `clip.MP4` | `00:07–00:13` | Arrival sign and station ambience | Good | Establishing/context | Keep |

Story-role labels should be useful for editing, such as `hook`, `establishing`, `movement`, `human moment`, `detail`, `landmark`, `payoff`, `transition`, or `ending`. Prefer specific time ranges and explain why a segment is selected. Flag clips that need stabilization, reframing, audio repair, or manual confirmation.

### 6. Design the short-form sequence

Create a chronological skeleton first, then improve pacing without losing the travel arc. A reliable structure is:

1. **Hook:** a brief teaser of the peak/payoff moment in the first 1–3 seconds. Show enough of the strongest later highlight to create anticipation without giving away the full payoff too early.
2. **Orientation:** quickly establish where the viewer is and what the trip is about.
3. **Progression:** move through places or activities with varied shot sizes and motion.
4. **Peak/payoff:** reserve the strongest landmark, view, meal, encounter, or emotional moment.
5. **Landing:** end with a memorable wide shot, human reaction, departure, or concise location card.

Before locking the sequence, make a people-balance pass: check that each clearly recurring person has at least one strong or shared-group appearance where the footage supports it, and trade some scenery-only coverage for underrepresented people when that improves the edit without making the pacing feel forced.

Use chronological order when the journey itself is the story. Use a story-driven order when it creates a stronger hook, but label non-chronological choices and retain the actual recording order in the clip log. Favor short, purposeful segments; avoid repeating the same view, camera move, or transition. Let natural sound bridge scenes when it adds place or emotion.

### 7. Deliver an edit plan or rough cut

For a plan-only request, provide:

- the chosen concept and target format;
- an ordered edit-decision list with source filenames and in/out timecodes;
- estimated duration of each selected segment and the total runtime;
- notes for crop/reframe, stabilization, speed changes, captions, narration, music, and audio transitions;
- rejected or held-back highlights and the reason for exclusion;
- assumptions about chronology and any unresolved choices.

For an explicitly requested rough cut, use the approved clip list and keep an export or project file separate from the source media. Do not silently replace footage, invent captions, or apply irreversible edits. Unless the user specifies otherwise, render short-form output as vertical 1080×1920 H.264/AAC while preserving the source frame rate where practical.

## Quality bar

A useful result is traceable: every recommended moment points to a real source and exact timecode; the ordering has a stated narrative reason; the final sequence has a clear opening, progression, payoff, and ending; and technical limitations are visible rather than hidden. When evidence is incomplete, return a partial catalogue and the smallest next input needed to continue.
