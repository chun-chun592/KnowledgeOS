import re

from .errors import ValidationError

def _find_section(body: str, heading: str) -> tuple[int, int] | None:
    """Return the (start, end) char span of the first level-2 ``## heading`` section.

    start points right after the heading line's newline; end points at the next
    unfenced heading of any level (or the end of the body content). Fenced code
    blocks are skipped so a ``#`` comment inside a fence never counts as a
    heading. Matching ignores case and trailing hashes.
    """
    heading = heading.strip().lstrip("#").strip()
    pattern = re.compile(rf"^##\s+{re.escape(heading)}\s*#*\s*$", re.IGNORECASE)
    fence_pattern = re.compile(r"^\s*(```|~~~)")
    heading_pattern = re.compile(r"^#{1,6}\s+\S")
    lines = body.split("\n")
    offset = 0
    target_start: int | None = None
    target_line = -1
    in_fence = False
    for idx, line in enumerate(lines):
        if fence_pattern.match(line):
            in_fence = not in_fence
        elif not in_fence and target_start is None and pattern.match(line):
            target_start = offset + len(line) + 1  # position just after the newline
            target_line = idx
        offset += len(line) + 1
    if target_start is None:
        return None
    in_fence = False
    offset = target_start
    end = len(body.rstrip())
    for line in lines[target_line + 1 :]:
        if fence_pattern.match(line):
            in_fence = not in_fence
        elif not in_fence and heading_pattern.match(line):
            end = offset
            break
        offset += len(line) + 1
    return target_start, end


def _append_section(body: str, heading: str, content: str) -> str:
    heading = heading.strip().lstrip("#").strip()
    if not heading:
        raise ValidationError("Section heading must not be empty.")
    if not content.strip():
        raise ValidationError("Section content must not be empty (use --content or stdin).")
    span = _find_section(body, heading)
    if span is None:
        return body.rstrip() + f"\n\n## {heading}\n\n{content.strip()}\n"
    start, end = span
    existing = body[start:end].strip()
    # start-1 is the heading line's own newline; find the newline before the
    # heading line to recover the heading text itself.
    head_line_end = body.rfind("\n", 0, start - 1)
    head_line = body[head_line_end + 1 : start - 1].rstrip()
    merged = head_line + "\n\n"
    if existing:
        merged += existing + "\n\n"
    merged += content.strip() + "\n"
    tail = body[end:]
    if tail.strip():
        merged += "\n" + tail.rstrip()
        if not merged.endswith("\n"):
            merged += "\n"
    # Everything before the target heading (document H1 title, summary line and
    # all earlier sections) must survive the merge. Regression-tested after a
    # live multi-agent QA run found whole pages reduced to their last section.
    prefix = body[: head_line_end + 1]
    return prefix + merged
