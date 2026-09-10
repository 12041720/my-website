#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import re
from pathlib import Path

OUTPUT_DIR = Path("content/posts/economics")

BLOCK_RE = re.compile(
    r"^## ChatGPT 回答 (?P<number>\d+)\s*$"
    r"(?P<body>.*?)(?=^---\s*$\n+(?:^## 用户提问 \d+\s*$|^## ChatGPT 回答 \d+\s*$)|\Z)",
    re.MULTILINE | re.DOTALL,
)
LESSON_TITLE_RE = re.compile(
    r"^第[〇零一二三四五六七八九十百两0-9]+课[：:].+$",
    re.MULTILINE,
)


def load_source() -> str:
    source_file = os.environ.get("ECONOMICS_SOURCE_FILE")
    if not source_file:
        raise RuntimeError(
            "Set ECONOMICS_SOURCE_FILE to an assistant-only economics Markdown export."
        )

    path = Path(source_file)
    if not path.is_file():
        raise RuntimeError(f"Economics source file not found: {path}")

    source = path.read_text(encoding="utf-8")
    if "## 用户提问" in source:
        raise RuntimeError("Refusing to publish a source that still contains user prompts.")
    return source


def yaml_string(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def normalize_math(markdown: str) -> str:
    markdown = markdown.replace("\\[", "$$").replace("\\]", "$$")
    lines = markdown.splitlines()
    output: list[str] = []
    i = 0

    while i < len(lines):
        if lines[i].strip() == "[":
            j = i + 1
            block: list[str] = []
            while j < len(lines) and lines[j].strip() != "]":
                block.append(lines[j])
                j += 1
            if j < len(lines) and block and any(line.strip() for line in block):
                output.append("$$")
                output.extend(block)
                output.append("$$")
                i = j + 1
                continue

        output.append(lines[i])
        i += 1

    return "\n".join(output).strip() + "\n"


def strip_markdown(text: str) -> str:
    text = re.sub(r"`([^`]+)`", r"\1", text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)
    text = re.sub(r"\*([^*]+)\*", r"\1", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def extract_title_and_body(answer_number: int, raw_body: str) -> tuple[str, str, int]:
    body = raw_body.strip()
    lesson_title = LESSON_TITLE_RE.search(body)

    if lesson_title:
        title = lesson_title.group(0).strip()
        body = body[lesson_title.end():].lstrip()
        course_order = max(1, answer_number - 1)
        return title, normalize_math(body), course_order

    if answer_number == 1:
        return (
            "经济学总地图：从理论、历史、制度到金融市场",
            normalize_math(body),
            0,
        )

    first_heading = re.search(r"^#\s+(.+)$", body, re.MULTILINE)
    if first_heading:
        title = first_heading.group(1).strip()
        body = body[first_heading.end():].lstrip()
    else:
        title = f"经济学总地图 · 第 {answer_number - 1} 课"

    return title, normalize_math(body), max(1, answer_number - 1)


def make_description(title: str, body: str, course_order: int) -> str:
    paragraphs = [
        strip_markdown(part)
        for part in re.split(r"\n\s*\n", body)
        if part.strip()
        and not part.lstrip().startswith(("#", "-", "*", ">", "$$", "```"))
    ]
    summary = paragraphs[0] if paragraphs else title
    summary = summary[:115].rstrip("，。；：,. ") + ("…" if len(summary) > 115 else "")
    prefix = "课程总览" if course_order == 0 else f"第 {course_order} 课"
    return f"{prefix}｜{summary}"


def write_post(
    answer_number: int,
    title: str,
    body: str,
    course_order: int,
) -> None:
    description = make_description(title, body, course_order)
    filename = "00-map.md" if course_order == 0 else f"{course_order:02d}-lesson.md"
    front_matter = "\n".join(
        [
            "---",
            f"title: {yaml_string(title)}",
            "date: 2026-09-07T12:00:00+08:00",
            "draft: false",
            'layout: "chatgpt"',
            "chatgptStyle: true",
            "math: true",
            f"weight: {course_order}",
            f"courseOrder: {course_order}",
            f"sourceAnswer: {answer_number}",
            'tags: ["经济学", "金融学", "政治经济学", "经济学总地图"]',
            f"description: {yaml_string(description)}",
            "showtoc: false",
            "ShowBreadCrumbs: false",
            "hideMeta: true",
            "disableShare: true",
            "---",
            "",
            "<!-- Generated from the assistant-only course snapshot. User prompts are intentionally omitted. -->",
            "",
        ]
    )
    (OUTPUT_DIR / filename).write_text(front_matter + body, encoding="utf-8")


def write_index(post_count: int) -> None:
    index = (
        '---\n'
        'title: "经济学总地图"\n'
        'description: "把经济学、金融学、政治经济学放进同一张理论—历史—制度—数据—市场地图中。"\n'
        'layout: "economics-index"\n'
        'chatgptStyle: true\n'
        '---\n\n'
        f'当前收录 {post_count} 篇课程文章：1 篇总地图 + {post_count - 1} 节课程。\n'
    )
    (OUTPUT_DIR / "_index.md").write_text(index, encoding="utf-8")


def main() -> None:
    source = load_source()
    matches = list(BLOCK_RE.finditer(source))
    if not matches:
        raise RuntimeError("No 'ChatGPT 回答 N' blocks found in source markdown.")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for path in OUTPUT_DIR.glob("*-lesson.md"):
        path.unlink()
    map_file = OUTPUT_DIR / "00-map.md"
    if map_file.exists():
        map_file.unlink()

    for match in matches:
        answer_number = int(match.group("number"))
        title, body, course_order = extract_title_and_body(
            answer_number, match.group("body")
        )
        write_post(answer_number, title, body, course_order)

    write_index(len(matches))
    print(f"Generated {len(matches)} economics posts in {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
