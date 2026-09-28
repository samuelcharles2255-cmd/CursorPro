import html
import re
from html.parser import HTMLParser


class JobHTMLSanitizer(HTMLParser):
    """
    Sanitizes HTML job descriptions.
    - Discards unsafe elements (<script>, <style>, <iframe>, <form>, etc.)
    - Unwraps layout/vendor container tags (<div>, <span>, <section>, etc.)
      to strip arbitrary vendor class names and emojis (e.g. '⚙ ⚙1opjj73')
    - Preserves semantic formatting: headings, paragraphs, lists, bold, italics, links
    - Sanitizes links (allows only safe http/https/mailto, adds target/rel)
    - Normalizes headings (downgrades <h1> to <h2> so it doesn't conflict with role title)
    """

    ALLOWED_TAGS = {
        "h2", "h3", "h4", "h5", "h6",
        "p", "br", "hr",
        "ul", "ol", "li",
        "strong", "b", "em", "i", "u", "mark",
        "blockquote", "code", "pre",
        "a",
    }

    DISCARD_TAGS = {
        "script", "style", "iframe", "frame", "object", "embed",
        "applet", "form", "input", "button", "textarea", "select",
        "meta", "link", "svg", "canvas", "noscript",
    }

    UNWRAP_TAGS = {
        "div", "span", "section", "article", "header", "footer",
        "main", "aside", "nav", "figure", "figcaption", "font", "center",
    }

    def __init__(self):
        super().__init__()
        self.output = []
        self.discard_depth = 0
        self.tag_stack = []

    def handle_starttag(self, tag, attrs):
        tag = tag.lower()

        if tag in self.DISCARD_TAGS:
            self.discard_depth += 1
            return

        if self.discard_depth > 0:
            return

        if tag in self.UNWRAP_TAGS:
            return

        # Downgrade h1 to h2 so it doesn't collide with page title h1
        if tag == "h1":
            tag = "h2"

        if tag in self.ALLOWED_TAGS:
            clean_attrs = []
            if tag == "a":
                href = ""
                for k, v in attrs:
                    if k.lower() == "href" and v:
                        v = v.strip()
                        if v.startswith(("http://", "https://", "mailto:")):
                            href = v
                if href:
                    clean_attrs.append(f'href="{html.escape(href)}"')
                    clean_attrs.append('target="_blank"')
                    clean_attrs.append('rel="noopener noreferrer"')

            attr_str = (" " + " ".join(clean_attrs)) if clean_attrs else ""
            self.output.append(f"<{tag}{attr_str}>")
            if tag not in ("br", "hr"):
                self.tag_stack.append(tag)

    def handle_endtag(self, tag):
        tag = tag.lower()

        if tag in self.DISCARD_TAGS:
            if self.discard_depth > 0:
                self.discard_depth -= 1
            return

        if self.discard_depth > 0:
            return

        if tag in self.UNWRAP_TAGS:
            return

        if tag == "h1":
            tag = "h2"

        if tag in self.ALLOWED_TAGS and tag not in ("br", "hr"):
            if tag in self.tag_stack:
                while self.tag_stack:
                    popped = self.tag_stack.pop()
                    self.output.append(f"</{popped}>")
                    if popped == tag:
                        break

    def handle_data(self, data):
        if self.discard_depth == 0:
            # Escape data to prevent raw tag injection while keeping text clean
            self.output.append(html.escape(data))

    def handle_entityref(self, name):
        if self.discard_depth == 0:
            if name == "nbsp":
                self.output.append(" ")
            else:
                char = html.unescape(f"&{name};")
                self.output.append(html.escape(char))

    def handle_charref(self, name):
        if self.discard_depth == 0:
            char = html.unescape(f"&#{name};")
            if char == "\xa0":
                self.output.append(" ")
            else:
                self.output.append(html.escape(char))

    def close(self):
        super().close()
        while self.tag_stack:
            popped = self.tag_stack.pop()
            self.output.append(f"</{popped}>")

    def get_clean_html(self):
        raw = "".join(self.output)

        # Strip bullet prefixes inside <li>: <li>* 8+ years -> <li>8+ years
        raw = re.sub(r"<li>\s*[*•\-~]\s*", "<li>", raw)

        # Clean empty paragraphs or paragraphs containing only spaces / &nbsp;
        raw = re.sub(r"<p>\s*(?:&nbsp;|\s)*</p>", "", raw)

        # Collapse excessive <br> tags
        raw = re.sub(r"(?:<br\s*/?>\s*){3,}", "<br><br>", raw)

        return raw.strip()


def is_html_content(text):
    """
    Checks if text contains structural HTML tags like <p>, <div>, <ul>, etc.
    Avoids classifying plain text with isolated tags (like search highlight <b>) as HTML.
    """
    if not text:
        return False
    return bool(
        re.search(
            r"<(?:p|div|ul|ol|li|h[1-6]|table|section|article|blockquote)\b",
            text,
            re.IGNORECASE,
        )
    )


def clean_search_snippet(text):
    """
    Cleans up search snippet text (e.g. from Jooble or search APIs).
    - Strips search term highlight tags (<b>Python</b> -> Python)
    - Decodes HTML entities and non-breaking spaces
    - Cleans excerpt ellipses and dot sequences
    - Groups adjacent bullet points into single <ul> / <ol> blocks
    - Structures section headings into clean semantic HTML
    """
    if not text:
        return ""

    # Decode HTML entities (handles double-encoded entities like &amp;nbsp;)
    decoded = html.unescape(text)
    decoded = html.unescape(decoded)

    # Strip search keyword highlight tags like <b>Python,</b> or <b>Python </b>
    decoded = re.sub(r"</?b\b[^>]*>", "", decoded, flags=re.IGNORECASE)

    # Normalize non-breaking spaces
    decoded = decoded.replace("\xa0", " ").replace("&nbsp;", " ")

    # Convert long runs of periods (e.g. ..........................) into section breaks
    decoded = re.sub(r"\.{4,}", "\n\n", decoded)

    # Convert discontinuous ellipsis markers (e.g. '... ...' or '...   ...') into section breaks
    decoded = re.sub(r"(?:\.\.\.|…)\s*(?:\.\.\.|…)+", "\n\n", decoded)

    # Clean markdown escapes and formatting
    decoded = re.sub(r"(\d+)\\\.", r"\1.", decoded)
    decoded = re.sub(r"_([^_]+)_", r"\1", decoded)

    raw_lines = decoded.split("\n")
    html_parts = []
    current_list = []
    current_list_type = "ul"

    def flush_list():
        nonlocal current_list, current_list_type
        if current_list:
            items = "".join(f"<li>{item}</li>" for item in current_list)
            html_parts.append(f"<{current_list_type}>{items}</{current_list_type}>")
            current_list = []
            current_list_type = "ul"

    for raw_line in raw_lines:
        line = raw_line.strip()
        if not line:
            # Blank line does not break list; wait for next content line
            continue

        # Strip leading/trailing ellipsis from snippet line
        clean_line = re.sub(r"^(?:\.\.\.|…)\s*", "", line)
        clean_line = re.sub(r"\s*(?:\.\.\.|…)$", "", clean_line).strip()
        if not clean_line:
            continue

        # Check for bullet points: ~, *, -, •, or numbered list: 1., 2.
        num_match = re.match(r"^(\d+)\.\s+(.+)$", clean_line)
        bullet_match = re.match(r"^(?:[~*\-•])\s*(.+)$", clean_line)

        if num_match:
            item_text = num_match.group(2).strip()
            item_text = re.sub(r"\s*(?:\.\.\.|…)$", "", item_text).strip()
            if item_text:
                if current_list and current_list_type != "ol":
                    flush_list()
                current_list_type = "ol"
                current_list.append(html.escape(item_text))
            continue
        elif bullet_match:
            item_text = bullet_match.group(1).strip()
            item_text = re.sub(r"\s*(?:\.\.\.|…)$", "", item_text).strip()
            if item_text:
                if current_list and current_list_type != "ul":
                    flush_list()
                current_list_type = "ul"
                current_list.append(html.escape(item_text))
            continue

        # Line is not a bullet item — flush pending list
        flush_list()

        # Heading detection:
        # e.g. "SKILLS & EXPERIENCE REQUIRED", "Skills & Tools:", "Required Skills", "Role Overview"
        is_heading = False
        lower_line = clean_line.lower().rstrip(":")
        common_heading_phrases = {
            "skills & tools", "skills and tools",
            "skills & experience required", "skills and experience required",
            "required skills", "core technical skills",
            "role overview", "about the job", "job details",
            "responsibilities", "requirements", "qualifications",
            "what you will do", "what you'll do", "who you are",
            "benefits", "perks", "work model",
        }

        if lower_line in common_heading_phrases:
            is_heading = True
        elif clean_line.isupper() and 3 < len(clean_line) < 60 and not clean_line.endswith("."):
            is_heading = True
        elif clean_line.endswith(":") and len(clean_line) < 45 and " " in clean_line:
            is_heading = True

        if is_heading:
            title_text = clean_line.rstrip(":")
            html_parts.append(f"<h3>{html.escape(title_text)}</h3>")
        else:
            html_parts.append(f"<p>{html.escape(clean_line)}</p>")

    flush_list()
    return "\n".join(html_parts)


def format_plain_text(text):
    """
    Formats a plain text job description (e.g. from Lever or plain text feeds)
    into clean semantic HTML paragraphs and lists.
    """
    if not text:
        return ""

    decoded = html.unescape(text).replace("\xa0", " ").replace("&nbsp;", " ")
    paragraphs = re.split(r"\n\s*\n+", decoded.strip())
    html_parts = []

    for para in paragraphs:
        lines = [l.strip() for l in para.split("\n") if l.strip()]
        if not lines:
            continue

        # Check if this paragraph is a list of bullet points
        is_list = all(re.match(r"^(?:[~*\-•]|\d+\.)\s+", l) for l in lines)
        if is_list:
            items = []
            for l in lines:
                clean_item = re.sub(r"^(?:[~*\-•]|\d+\.)\s+", "", l)
                items.append(f"<li>{html.escape(clean_item)}</li>")
            html_parts.append(f"<ul>{''.join(items)}</ul>")
        else:
            joined = "<br>".join(html.escape(l) for l in lines)
            html_parts.append(f"<p>{joined}</p>")

    return "\n".join(html_parts)


def clean_job_description(content, source=""):
    """
    Main entry point for cleaning any job description.
    Handles HTML, search snippets, and plain text descriptions.
    Returns clean, safe, valid HTML ready to be rendered in templates.
    """
    if not content or not str(content).strip():
        return ""

    raw = str(content).strip()

    # If the content is encoded HTML (e.g. &lt;h2&gt;Who we are&lt;/h2&gt;), unescape it
    if "&lt;" in raw and ("&lt;h" in raw or "&lt;p" in raw or "&lt;div" in raw or "&lt;ul" in raw):
        raw = html.unescape(raw)

    if is_html_content(raw):
        parser = JobHTMLSanitizer()
        parser.feed(raw)
        parser.close()
        clean = parser.get_clean_html()
        return clean

    # If it came from an API (e.g. Jooble snippet) or looks like a search snippet:
    if source == "api" or "..." in raw or "…" in raw or "<b>" in raw.lower() or "&nbsp;" in raw:
        return clean_search_snippet(raw)

    # Otherwise plain text
    return format_plain_text(raw)
