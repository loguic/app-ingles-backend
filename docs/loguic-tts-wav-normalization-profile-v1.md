# LOGUIC TTS WAV Normalization Profile v1

Profile version: `loguic-tts-wav-normalization/1.0`.

## Purpose and boundary

This profile reproducibly derives one technical review artifact from an
already-produced TTS raw WAV. It does not generate speech, assess content,
pronunciation, locale, naturalness or pedagogical suitability, and it does not
make a pedagogical decision. Those are separate Quality Gate layers.

The profile applies equally to MeloTTS, Kokoro and any future engine. A human
reviewer must listen to the normalized artifact whose SHA-256 is recorded by
this profile, not to an untracked raw file.

## Existing requirements and precedents

- The A1-U1 resource binding contract requires WAV for its twelve audio
  resources.
- Backend-managed learner audio is declared as `audio/wav` and is structurally
  checked as RIFF/WAVE; that private upload contract does not define the TTS
  profile's codec, sample rate, channels or quality thresholds.
- Historical pedagogical WAV assets used PCM s16le, 22050 Hz, mono and 16-bit.
  That is a precedent, not the authority for this profile.
- The phonetic calibration corpus preserves exact WAV SHA-256 and forbids
  deriving pedagogical thresholds from technical scores.

## Human-Gate decisions adopted in v1

The normalized artifact must contain exactly one audio stream and be:

| Property | Required value |
| --- | --- |
| container | RIFF/WAVE |
| codec | `pcm_s16le` |
| sample format | `s16` |
| sample rate | 24000 Hz |
| channels | 1 (mono) |
| bit depth | 16-bit |
| byte order | little-endian |
| dither | none |

24000 Hz is the approved v1 authority. It deliberately supersedes neither the
historical 22050 Hz pedagogical precedent nor the 16000 Hz calibration corpus;
those remain historical artifacts under their own identities.

## Raw input contract

Raw input must be a regular non-symlink file that is fully decodable and has
exactly one mono audio stream in a RIFF/WAVE container using linear,
uncompressed PCM. A-law and mu-law are not linear PCM for this profile.

Stereo or multichannel input is rejected before FFmpeg runs. The profile never
uses output channel conversion as authorization to downmix.

## Permitted deterministic transformation

The implementation builds an argv equivalent to:

```text
ffmpeg -nostdin -hide_banner -loglevel error -xerror -i RAW.wav
  -map 0:a:0 -vn -sn -dn -map_metadata -1 -map_chapters -1
  -af aresample=24000:resampler=swr:osf=s16:dither_method=none:filter_size=32:phase_shift=10:linear_interp=1:exact_rational=1
  -c:a pcm_s16le -ac 1 -threads 1 -fflags +bitexact -flags:a +bitexact
  -write_bext 0 -write_peak off -rf64 never -f wav NORMALIZED.wav
```

Raw mono is validated before this argv is built. The only signal
transformations are complete decoding, deterministic resampling to 24000 Hz
and conversion to PCM s16le. Metadata and chapters are removed; the output is
written as RIFF/WAVE without BEXT, PEAK or RF64 chunks.

## Prohibited transformations

The profile must not trim silence, normalize loudness or peaks, limit,
compress, correct DC offset, high-pass, denoise, dereverberate, EQ, de-ess,
change tempo/duration/pitch, insert pauses, or apply engine-, voice-, locale-
or sample-specific processing.

## Identity and reproducibility

Each result records exactly:

- `sample_id`;
- `profile_version`;
- raw and normalized SHA-256 over their exact bytes;
- raw and normalized probes and descriptive metrics;
- full runtime FFmpeg and FFprobe version output;
- the actual normalization argv;
- `normalized_at_utc` for audit only.

`sample_id` is an opaque caller-owned correlation key known before
normalization; it is not required to be the final benchmark
`SampleIdentity.sample_id`, whose identity can depend on the normalized
SHA-256 produced by this operation. For TTS Engine Benchmark v1 it is exactly
the already-existing `run_execution_id`. The benchmark runner later binds that
record to the final `SampleIdentity` by requiring equality of the correlation
key, raw SHA-256, normalized SHA-256 and profile version. The record is never
rewritten after publication.

The normalized WAV and its normalization record must share exactly one parent
directory. Both are new immutable outputs of the same normalization operation.

Raw and normalized bytes are separate immutable artifacts. The timestamp is
not an identity input. The initial approved toolchain is `ffmpeg 6.1.1-3ubuntu5`
and `ffprobe 6.1.1-3ubuntu5`; a different toolchain is rejected by v1. The
same raw input must normalize twice to byte-identical output under that
toolchain. A changed toolchain or argv requires a new profile version or an
explicitly verified byte-identical result.

The CLI never overwrites a normalized WAV or its record. It writes temporary
files, verifies them, publishes without overwrite and removes only artifacts
created by its own failed execution.

## Descriptive metrics, not thresholds

The profile records byte size; container; codec; sample format; sample rate;
channels/layout; bit depth; stream count; duration in samples/seconds; decoded
sample count; sample peak; true peak; full-scale sample count; RMS; peak level;
LUFS/LRA when calculable; DC offset; exact-zero leading/trailing runs; and a
noise-floor value only when a named, versioned analyzer exists.

No LUFS, clipping, duration, silence, noise-floor or DC-offset threshold is
defined. Metrics are descriptive technical evidence, not an automatic quality,
accent, phonetic, naturalness or pedagogical decision. Exact-zero runs are not
perceptual silence detection.

## Fair benchmark use

All candidate engines must use this exact profile before blind review IDs are
assigned. No sample may receive post-processing after technical or human
results become known. Changing this profile requires re-normalizing the full
comparison corpus; raw and normalized measurements remain available to expose
the effects of conversion rather than hide them.

## Explicit exclusions

This profile does not install or run TTS engines, generate samples, perform
ASR/alignment, invoke WavLM/GOP as a decision-maker, create expected resource
identities, execute B51/B52, publish A1 resources, activate curriculum, change
the loader or frontend, or resume B181.
