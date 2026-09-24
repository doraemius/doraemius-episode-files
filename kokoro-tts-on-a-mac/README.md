# Kokoro TTS on a Mac: why my AI voice sounded like a robot

Files for the Doraemius video of the same name. Kokoro-82M narrates the whole video, running
locally on an Apple M1 CPU: no GPU, no cloud, no API key.

## What's here

| file | what it does |
|---|---|
| `narration.md` | every spoken line, with the joke `{H}` and human-touch `{U}` tags |
| `voice.py` | renders the narration the way the video does: one sentence per call, padding trimmed, a beat before punchlines, asides a bit faster |
| `script-knobs.py` | counts the Humor and Human share of a script (this one: 32% and 10%) |
| `speech-rhythm.py` | measures any narration: words per minute, pauses, and (with `--pitch`) how alike its phrase melodies are |
| `data/kokoro-curves.json` | the pitch curves behind the "same tune" graphic, taken from this channel's own Kokoro narration |

## Run it

```bash
pip install kokoro soundfile numpy
python voice.py                                   # -> out/voices/s01.wav ... s08.wav + timing.json
python script-knobs.py narration.md --humor 33 --human 10

pip install faster-whisper librosa                # for the measuring tool
python speech-rhythm.py out/voices/s05.wav --pitch
```

## The numbers in the video

| claim | measured |
|---|---|
| speed on an M1 CPU | 5.0-5.9x faster than real time, on two different scripts, 2 runs each |
| speed setting 1.15 vs 1.0 | audio 8% shorter (106.5 s vs 115.7 s), not 15% |
| words per minute, default speed | up to 223; this video targets 173-200, checked per section (174-189) |
| listen-back check | on one earlier episode, 21 of 24 scenes transcribed back almost word for word; the rest differed on digits |
| pace and pauses | inside the range of experienced human speakers |
| melody sameness (0 = every phrase different) | human speakers about 0.05; the old narration 0.70 |
| rewriting the script to be said out loud | sameness 0.50 to 0.38; adding pauses and fillers scored worse (0.58) but sounded best by ear |

## Sources

- Kokoro-82M model card (hexgrad, Hugging Face): Apache 2.0, 82M parameters, 8 languages, 54 voices.
- Average conversational speaking rate, about 150 words per minute: National Center for Voice and Speech.

Everything runs locally. MIT licence for these scripts (see the repo's `LICENSE`); Kokoro and the
Python packages keep their own licences.
