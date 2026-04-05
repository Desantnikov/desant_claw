import argparse
import asyncio
import re
from typing import Any

from bs4 import BeautifulSoup
from readability import Document

from src.storage.postgres.session import SessionFactory
from src.storage.postgres.repositories.email_repository import EmailRepository


# =========================
# Cleaning logic
# =========================
import re
import unicodedata
from collections import Counter

from bs4 import BeautifulSoup
from readability import Document


def clean_email_html_advanced(html: str) -> str:
    """
    Clean email HTML and keep only meaningful email text.

    This function is intentionally heuristic and somewhat aggressive.
    It aims to improve embedding quality, not preserve exact formatting.
    """

    if not html or not html.strip():
        return ""

    precleaned_html = _preclean_raw_html(html)
    extracted_html = _extract_main_html(precleaned_html)
    extracted_html = _preclean_raw_html(extracted_html)

    soup = BeautifulSoup(extracted_html, "html.parser")

    _remove_garbage_tags(soup)
    _remove_hidden_elements(soup)
    _normalize_block_separators(soup)

    raw_text = soup.get_text(separator="\n")
    normalized_text = _normalize_text(raw_text)
    trimmed_reply_text = _remove_reply_chain(normalized_text)
    filtered_lines = _remove_noise_lines(trimmed_reply_text)
    deduplicated_lines = _remove_duplicate_lines(filtered_lines)

    cleaned_text = "\n".join(deduplicated_lines)
    cleaned_text = _postprocess_text(cleaned_text)

    return cleaned_text.strip()


def _preclean_raw_html(html: str) -> str:
    """
    Remove raw document-level HTML noise before parsing.
    """

    if not html:
        return ""

    cleaned_html = html

    # Remove BOM and invisible characters early
    cleaned_html = _strip_invisible_characters(cleaned_html)
    cleaned_html = _normalize_unicode_spaces(cleaned_html)

    # Remove XML declaration
    cleaned_html = re.sub(
        r"(?is)^\s*<\?xml[^>]*\?>",
        "",
        cleaned_html,
    )

    # Remove DOCTYPE
    cleaned_html = re.sub(
        r"(?is)<!doctype[^>]*>",
        "",
        cleaned_html,
    )

    # Remove HTML comments
    cleaned_html = re.sub(
        r"(?is)<!--.*?-->",
        "",
        cleaned_html,
    )

    # Remove opening/closing html/body tags explicitly
    cleaned_html = re.sub(
        r"(?is)</?(html|body)\b[^>]*>",
        "",
        cleaned_html,
    )

    # Remove xmlns leftovers if they leaked as text
    cleaned_html = re.sub(
        r'(?is)\sxmlns(:\w+)?="[^"]*"',
        "",
        cleaned_html,
    )

    return cleaned_html.strip()


def _extract_main_html(html: str) -> str:
    """
    Try to extract the main content using readability.
    Fallback to original HTML if extraction fails.
    """
    try:
        document = Document(html)
        summary_html = document.summary()
        if summary_html and summary_html.strip():
            return summary_html
    except Exception:
        pass

    return html


def _remove_garbage_tags(soup: BeautifulSoup) -> None:
    """
    Remove tags that never carry useful email content.
    """
    for tag in soup([
        "script",
        "style",
        "head",
        "meta",
        "noscript",
        "svg",
        "canvas",
        "iframe",
        "object",
        "embed",
        "footer",
        "form",
        "input",
        "button",
    ]):
        tag.decompose()


def _remove_hidden_elements(soup: BeautifulSoup) -> None:
    """
    Remove elements hidden via inline styles or common accessibility tricks.
    """
    for element in soup.find_all(style=True):
        style_value = element.get("style", "").lower().replace(" ", "")
        if any(hidden_rule in style_value for hidden_rule in [
            "display:none",
            "visibility:hidden",
            "opacity:0",
            "font-size:0",
            "max-height:0",
            "max-width:0",
            "height:0",
            "width:0",
            "overflow:hidden",
            "mso-hide:all",
        ]):
            element.decompose()

    for element in soup.find_all(attrs={"aria-hidden": "true"}):
        element.decompose()


def _normalize_block_separators(soup: BeautifulSoup) -> None:
    """
    Insert line breaks around block-like elements to preserve readable structure.
    """
    for br_tag in soup.find_all("br"):
        br_tag.replace_with("\n")

    for block_tag_name in [
        "p",
        "div",
        "section",
        "article",
        "li",
        "tr",
        "table",
        "h1",
        "h2",
        "h3",
        "h4",
        "h5",
        "h6",
    ]:
        for block_tag in soup.find_all(block_tag_name):
            block_tag.insert_before("\n")
            block_tag.insert_after("\n")


def _normalize_text(text: str) -> str:
    """
    Normalize whitespace, remove invisible unicode characters,
    and collapse redundant empty lines.
    """
    text = _strip_invisible_characters(text)
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = _normalize_unicode_spaces(text)

    text = re.sub(r"[ \t]+\n", "\n", text)
    text = re.sub(r"\n[ \t]+", "\n", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)

    text_lines = text.split("\n")
    cleaned_lines = [_strip_invisible_characters(line).strip(" ") for line in text_lines]
    cleaned_lines = _trim_and_collapse_empty_lines(cleaned_lines)

    return "\n".join(cleaned_lines).strip()


def _normalize_unicode_spaces(text: str) -> str:
    """
    Replace non-standard unicode spaces with a normal space.
    """
    unicode_spaces_pattern = r"[\u00A0\u1680\u2000-\u200A\u202F\u205F\u3000]"
    return re.sub(unicode_spaces_pattern, " ", text)


def _strip_invisible_characters(text: str) -> str:
    """
    Remove invisible/control/format unicode characters but keep newlines and tabs.
    """
    cleaned_characters = []

    for character in text:
        if character in {"\n", "\t"}:
            cleaned_characters.append(character)
            continue

        unicode_category = unicodedata.category(character)
        if unicode_category.startswith("C"):
            continue

        cleaned_characters.append(character)

    cleaned_text = "".join(cleaned_characters)
    cleaned_text = re.sub(r"[\u200b-\u200f\u2060\ufeff]", "", cleaned_text)

    return cleaned_text


def _remove_reply_chain(text: str) -> str:
    """
    Remove common quoted reply headers and forwarded-message chains.
    """
    reply_cut_patterns = [
        r"(?im)^on .+wrote:$",
        r"(?im)^from:\s.+$",
        r"(?im)^sent:\s.+$",
        r"(?im)^to:\s.+$",
        r"(?im)^subject:\s.+$",
        r"(?im)^-{2,}\s*original message\s*-{2,}$",
        r"(?im)^-{2,}\s*forwarded message\s*-{2,}$",
        r"(?im)^begin forwarded message:$",
    ]

    earliest_cut_index = None

    for pattern in reply_cut_patterns:
        match = re.search(pattern, text)
        if match:
            if earliest_cut_index is None or match.start() < earliest_cut_index:
                earliest_cut_index = match.start()

    if earliest_cut_index is not None:
        return text[:earliest_cut_index].strip()

    return text


def _remove_noise_lines(text: str) -> list[str]:
    """
    Remove footer lines, legal boilerplate, tracking links, and other low-value lines.
    """
    raw_lines = text.split("\n")
    lines = [_strip_invisible_characters(line).strip() for line in raw_lines]
    cleaned_lines = []

    for line in lines:
        if not line:
            cleaned_lines.append("")
            continue

        line_lower = line.lower()

        if re.fullmatch(r"[-_=~*#]{3,}", line):
            continue

        if re.fullmatch(r"\[image.*\]", line_lower):
            continue

        if _looks_like_raw_html_garbage(line_lower):
            continue

        if _is_footer_or_noise_line(line, line_lower):
            continue

        cleaned_lines.append(line)

    return _trim_and_collapse_empty_lines(cleaned_lines)


def _looks_like_raw_html_garbage(line_lower: str) -> bool:
    """
    Detect raw HTML declarations or wrappers that leaked into text.
    """
    raw_html_patterns = [
        r"^<!doctype",
        r"^<html\b",
        r"^</html>$",
        r"^<body\b",
        r"^</body>$",
        r"^<head\b",
        r"^</head>$",
        r"^<meta\b",
        r"^<title\b",
        r"^</title>$",
        r"^xmlns(:\w+)?=",
        r'^public "-//w3c//dtd',
        r"^http://www\.w3\.org/tr/xhtml1/",
    ]

    return any(re.search(pattern, line_lower) for pattern in raw_html_patterns)


def _is_footer_or_noise_line(line: str, line_lower: str) -> bool:
    """
    Decide whether a line looks like footer/legal/subscription/tracking noise.
    """
    footer_patterns = [
        r"unsubscribe",
        r"manage preferences",
        r"email preferences",
        r"update preferences",
        r"privacy policy",
        r"cookie policy",
        r"terms of service",
        r"view in browser",
        r"open in browser",
        r"web version",
        r"all rights reserved",
        r"copyright\s*(©|\(c\))?",
        r"this email was sent to",
        r"you are receiving this email",
        r"add us to your address book",
        r"if you no longer wish to receive",
        r"to stop receiving these emails",
        r"click here to unsubscribe",
        r"do not reply to this email",
        r"please do not reply",
        r"automated message",
        r"this message and any attachments",
        r"confidentiality notice",
        r"virus[- ]free",
        r"environment before printing",
        r"follow us on",
        r"facebook",
        r"instagram",
        r"linkedin",
        r"twitter",
        r"youtube",
    ]

    for pattern in footer_patterns:
        if re.search(pattern, line_lower):
            return True

    if re.fullmatch(r"https?://\S+", line_lower):
        return True

    url_count = len(re.findall(r"https?://\S+", line_lower))
    if url_count >= 2:
        return True

    short_noise_values = {
        "unsubscribe",
        "privacy policy",
        "view online",
        "view in browser",
        "manage preferences",
        "update preferences",
    }
    if line_lower in short_noise_values:
        return True

    return False


def _remove_duplicate_lines(lines: list[str]) -> list[str]:
    """
    Remove duplicate lines:
    - repeated consecutive lines
    - globally repeated short lines that are likely footer noise
    """
    if not lines:
        return []

    normalized_counter = Counter()
    normalized_lines = []

    for line in lines:
        normalized_line = _normalize_line_for_dedup(line)
        normalized_lines.append(normalized_line)

        if normalized_line:
            normalized_counter[normalized_line] += 1

    result_lines = []
    seen_short_lines = set()
    previous_normalized_line = None

    for index, line in enumerate(lines):
        normalized_line = normalized_lines[index]

        if not normalized_line:
            if result_lines and result_lines[-1] != "":
                result_lines.append("")
            previous_normalized_line = None
            continue

        if normalized_line == previous_normalized_line:
            continue

        if len(normalized_line) < 120 and normalized_counter[normalized_line] > 1:
            if normalized_line in seen_short_lines:
                continue
            seen_short_lines.add(normalized_line)

        result_lines.append(line)
        previous_normalized_line = normalized_line

    return _trim_and_collapse_empty_lines(result_lines)


def _normalize_line_for_dedup(line: str) -> str:
    """
    Normalize a line for duplicate detection.
    """
    normalized_line = _strip_invisible_characters(line).lower().strip()
    normalized_line = re.sub(r"\s+", " ", normalized_line)
    return normalized_line


def _trim_and_collapse_empty_lines(lines: list[str]) -> list[str]:
    """
    Remove empty lines at the start/end and collapse repeated empty lines inside.
    """
    normalized_lines = []

    for line in lines:
        cleaned_line = _strip_invisible_characters(line)
        cleaned_line = _normalize_unicode_spaces(cleaned_line)
        cleaned_line = cleaned_line.strip()

        if cleaned_line:
            normalized_lines.append(cleaned_line)
        else:
            normalized_lines.append("")

    start_index = 0
    end_index = len(normalized_lines)

    while start_index < end_index and normalized_lines[start_index] == "":
        start_index += 1

    while end_index > start_index and normalized_lines[end_index - 1] == "":
        end_index -= 1

    trimmed_lines = normalized_lines[start_index:end_index]

    result_lines = []
    previous_was_empty = False

    for line in trimmed_lines:
        is_empty = line == ""

        if is_empty:
            if previous_was_empty:
                continue
            result_lines.append("")
            previous_was_empty = True
        else:
            result_lines.append(line)
            previous_was_empty = False

    return result_lines


def _postprocess_text(text: str) -> str:
    """
    Final cleanup after line-level filtering.
    """
    text = _strip_invisible_characters(text)
    text = _normalize_unicode_spaces(text)

    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r" *\n *", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)

    garbage_patterns = [
        r"(?im)^powered by .+$",
        r"(?im)^sent from my .+$",
        r"(?im)^download the app.*$",
        r"(?im)^get the app.*$",
        r"(?im)^<!doctype.*$",
        r"(?im)^<html.*$",
        r"(?im)^</html>$",
        r"(?im)^<body.*$",
        r"(?im)^</body>$",
    ]

    for pattern in garbage_patterns:
        text = re.sub(pattern, "", text)

    text = re.sub(r"\n{3,}", "\n\n", text)

    final_lines = text.split("\n")
    final_lines = _trim_and_collapse_empty_lines(final_lines)

    return "\n".join(final_lines).strip()


# =========================
# Batch processing
# =========================

DEFAULT_BATCH_SIZE = 100


async def process_batch(
    batch_index: int,
    batch_size: int,
) -> int:
    offset = batch_index * batch_size

    async with SessionFactory() as session:
        repo = EmailRepository(session=session)

        result = await repo.get_emails(limit=batch_size, offset=offset)
        rows = result.all()

        if not rows:
            print(f"[Batch {batch_index}] No emails found")
            return 0

        updated_count = 0

        for row in rows:
            email = row[0]

            cleaned = clean_email_html_advanced(email.body_cleaned or "")

            # Important: update only if changed
            if cleaned != email.body_cleaned:
                email.body_cleaned = cleaned
                updated_count += 1

        # Commit per batch (critical!)
        await session.commit()

        print(
            f"[Batch {batch_index}] "
            f"Processed {len(rows)} emails, updated {updated_count}"
        )

        return len(rows)


async def main(
    batch_size: int,
    start_batch_index: int,
) -> None:

    if batch_size <= 0:
        raise ValueError("batch_size must be > 0")

    current_batch = start_batch_index

    total_processed = 0

    while True:
        print(f"\n=== Batch {current_batch} ===")

        processed = await process_batch(
            batch_index=current_batch,
            batch_size=batch_size,
        )

        if processed == 0:
            print("No more emails. Stopping.")
            break

        total_processed += processed
        current_batch += 1

    print("\n=== DONE ===")
    print(f"Total processed: {total_processed}")


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--batch-size", type=int, default=DEFAULT_BATCH_SIZE)
    parser.add_argument("--start-batch-index", type=int, default=0)
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    asyncio.run(
        main(
            batch_size=args.batch_size,
            start_batch_index=args.start_batch_index,
        )
    )