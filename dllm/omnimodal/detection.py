"""
Run:
  source ~/.zshrc && conda activate ~/miniconda3/envs/dllm
  python -c "from dllm.omnimodal.detection import detect_modality; print(detect_modality('/tmp/a.txt').modality)"
"""

import mimetypes
from dataclasses import dataclass
from pathlib import Path

from dllm.omnimodal.contracts import Modality, ModalityDetectionTrace

_EXTENSION_MAP: dict[str, Modality] = {
    ".txt": Modality.TEXT,
    ".md": Modality.TEXT,
    ".pdf": Modality.PDF,
    ".jpg": Modality.IMAGE,
    ".jpeg": Modality.IMAGE,
    ".png": Modality.IMAGE,
    ".webp": Modality.IMAGE,
    ".gif": Modality.IMAGE,
    ".mp4": Modality.VIDEO,
    ".avi": Modality.VIDEO,
    ".webm": Modality.VIDEO,
    ".mp3": Modality.AUDIO,
    ".wav": Modality.AUDIO,
    ".flac": Modality.AUDIO,
    ".mid": Modality.MIDI,
    ".midi": Modality.MIDI,
}


@dataclass(frozen=True)
class DetectionResult:
    modality: Modality
    trace: ModalityDetectionTrace


def _modality_from_mime(path: Path) -> Modality | None:
    mime, _ = mimetypes.guess_type(path.as_posix())
    if not mime:
        return None
    if mime.startswith("text/"):
        return Modality.TEXT
    if mime.startswith("image/"):
        return Modality.IMAGE
    if mime.startswith("video/"):
        return Modality.VIDEO
    if mime.startswith("audio/"):
        return Modality.AUDIO
    if mime == "application/pdf":
        return Modality.PDF
    return None


def detect_modality(
    path: str,
    gif_policy: str = "adaptive",
    gif_frame_count: int | None = None,
    gif_video_frame_threshold: int = 2,
) -> DetectionResult:
    file_path = Path(path)
    ext_guess = _EXTENSION_MAP.get(file_path.suffix.lower(), Modality.UNKNOWN)
    mime_guess = _modality_from_mime(file_path)
    notes: list[str] = []

    modality = ext_guess if ext_guess != Modality.UNKNOWN else (mime_guess or Modality.UNKNOWN)

    if file_path.suffix.lower() == ".gif":
        if gif_policy == "image":
            modality = Modality.IMAGE
            notes.append("gif_policy=image")
        elif gif_policy == "video":
            modality = Modality.VIDEO
            notes.append("gif_policy=video")
        else:
            if gif_frame_count is not None and gif_frame_count >= gif_video_frame_threshold:
                modality = Modality.VIDEO
                notes.append(f"gif_policy=adaptive->video(threshold={gif_video_frame_threshold})")
            else:
                modality = Modality.IMAGE
                notes.append(f"gif_policy=adaptive->image(threshold={gif_video_frame_threshold})")

    trace = ModalityDetectionTrace(
        guessed_by_extension=ext_guess.value if ext_guess != Modality.UNKNOWN else None,
        guessed_by_mime=mime_guess.value if mime_guess else None,
        parser_check="extension+mimetype",
        policy_notes=notes,
    )
    return DetectionResult(modality=modality, trace=trace)
