"""Markdown <-> Tiptap-JSON helpers.

Seeded skills arrive as Markdown; the FastWiki-style editor is canonical on
Tiptap JSON. ``markdown_to_doc`` converts a Markdown string into a Tiptap doc so
seeded skills open cleanly in all three editor modes (rich / block / markdown).
It mirrors the subset implemented client-side in EDITOR_JS.
"""
from __future__ import annotations
import re

_INLINE = re.compile(r"(\*\*[^*]+\*\*|\*[^*]+\*|`[^`]+`|\[[^\]]+\]\([^)]+\))")


def _inline(text: str):
    nodes, at = [], 0

    def push(value, marks=None):
        if value:
            node = {"type": "text", "text": value}
            if marks:
                node["marks"] = marks
            nodes.append(node)

    for m in _INLINE.finditer(text):
        push(text[at:m.start()])
        token = m.group(0)
        if token.startswith("**"):
            push(token[2:-2], [{"type": "bold"}])
        elif token.startswith("*"):
            push(token[1:-1], [{"type": "italic"}])
        elif token.startswith("`"):
            push(token[1:-1], [{"type": "code"}])
        else:
            link = re.match(r"^\[([^\]]+)\]\(([^)]+)\)$", token)
            push(link.group(1), [{"type": "link", "attrs": {"href": link.group(2)}}])
        at = m.end()
    push(text[at:])
    return nodes


def _para(text):
    content = _inline(text)
    node = {"type": "paragraph"}
    if content:
        node["content"] = content
    return node


def markdown_to_doc(md: str) -> dict:
    lines = (md or "").replace("\r\n", "\n").split("\n")
    nodes, i, n = [], 0, len(lines)
    while i < n:
        line = lines[i]
        if not line.strip():
            i += 1
            continue
        if line.startswith("```"):
            body, i = [], i + 1
            while i < n and not lines[i].startswith("```"):
                body.append(lines[i]); i += 1
            if i < n:
                i += 1
            node = {"type": "codeBlock"}
            if body:
                node["content"] = [{"type": "text", "text": "\n".join(body)}]
            nodes.append(node)
            continue
        heading = re.match(r"^(#{1,6})\s+(.*)$", line)
        if heading:
            level = min(3, len(heading.group(1)))
            nodes.append({"type": "heading", "attrs": {"level": level},
                          "content": _inline(heading.group(2))})
            i += 1
            continue
        if re.match(r"^\s*>\s?", line):
            body = []
            while i < n and re.match(r"^\s*>\s?", lines[i]):
                body.append(re.sub(r"^\s*>\s?", "", lines[i])); i += 1
            nodes.append({"type": "blockquote", "content": [_para(" ".join(body))]})
            continue
        if re.match(r"^\s*[-*+]\s+", line) or re.match(r"^\s*\d+[.)]\s+", line):
            ordered = bool(re.match(r"^\s*\d", line))
            matcher = re.compile(r"^\s*\d+[.)]\s+" if ordered else r"^\s*[-*+]\s+")
            items = []
            while i < n and matcher.match(lines[i]):
                items.append({"type": "listItem",
                              "content": [_para(matcher.sub("", lines[i]))]})
                i += 1
            nodes.append({"type": "orderedList" if ordered else "bulletList",
                          "content": items})
            continue
        if re.match(r"^\s*(-{3,}|\*{3,}|_{3,})\s*$", line):
            nodes.append({"type": "horizontalRule"}); i += 1
            continue
        para = []
        while i < n and lines[i].strip() and not re.match(
                r"^(#{1,6}\s|```|\s*>\s?|\s*[-*+]\s+|\s*\d+[.)]\s+|\s*(-{3,}|\*{3,}|_{3,})\s*$)",
                lines[i]):
            para.append(lines[i]); i += 1
        nodes.append(_para(" ".join(para)))
    return {"type": "doc", "content": nodes or [{"type": "paragraph"}]}


def plain_text(doc) -> str:
    parts = []

    def visit(node):
        if isinstance(node, dict):
            if isinstance(node.get("text"), str):
                parts.append(node["text"])
            for child in node.get("content", []):
                visit(child)
        elif isinstance(node, list):
            for child in node:
                visit(child)
    visit(doc)
    return " ".join(parts)
