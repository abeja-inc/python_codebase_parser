from typing import Any, Generator


def block2markdown(block: dict[str, Any], level: int = 0) -> str:
    """
    Convert a Notion block to markdown format.

    Parameters
    ----------
    block : dict[str, Any]
        The Notion block to convert.
    level : int, optional
        The indentation level of the block, by default 0.

    Returns
    -------
    str
        The markdown representation of the Notion block.

    """
    indent = "  " * level
    markdown = indent
    if block["type"] == "heading_1":
        rich_text = block["heading_1"]["rich_text"]
        if len(rich_text) > 0:
            text = ""
            for text_obj in rich_text:
                text += text_obj["plain_text"]
            markdown += "# " + text
    elif block["type"] == "heading_2":
        rich_text = block["heading_2"]["rich_text"]
        if len(rich_text) > 0:
            text = ""
            for text_obj in rich_text:
                text += text_obj["plain_text"]
            markdown += "## " + text
    elif block["type"] == "heading_3":
        rich_text = block["heading_3"]["rich_text"]
        if len(rich_text) > 0:
            text = ""
            for text_obj in rich_text:
                text += text_obj["plain_text"]
            markdown += "### " + text
    elif block["type"] == "paragraph":
        rich_text = block["paragraph"]["rich_text"]
        if len(rich_text) > 0:
            text = ""
            for text_obj in rich_text:
                if text_obj.get("type") == "text":
                    text = text_obj["plain_text"]
                    markdown += text
                elif text_obj.get("type") == "mention":
                    mention = text_obj["mention"]
                    mention_type = mention["type"]
                    if mention_type == "link_preview":
                        url = mention["link_preview"]["url"]
                        markdown += f"[link_preview]({url})\n"
                    elif mention_type == "page":
                        page_id = mention["page"]["id"]
                        markdown += f"[page_mention:{page_id}]\n"
                    else:
                        pass
            markdown += "\n"
    elif block["type"] == "bulleted_list_item":
        rich_text = block["bulleted_list_item"]["rich_text"]
        if len(rich_text) > 0:
            text = ""
            for text_obj in rich_text:
                text += text_obj["plain_text"]
            markdown += "- " + text + "\n"
    elif block["type"] == "numbered_list_item":
        rich_text = block["numbered_list_item"]["rich_text"]
        if len(rich_text) > 0:
            text = ""
            for text_obj in rich_text:
                text += text_obj["plain_text"]
            markdown += "1. " + text + "\n"
    elif block["type"] == "to_do":
        rich_text = block["to_do"]["rich_text"]
        if len(rich_text) > 0:
            text = ""
            for text_obj in rich_text:
                text += text_obj["plain_text"]
                if block["to_do"]["checked"]:
                    markdown += "- [x] " + text + "\n"
                else:
                    markdown += "- [ ] " + text + "\n"
    elif block["type"] == "toggle":
        rich_text = block["toggle"]["rich_text"]
        if len(rich_text) > 0:
            text = ""
            for text_obj in rich_text:
                text += text_obj["plain_text"]
            markdown = markdown.strip()
            markdown += "<details>\n<summary>" + text + "</summary>\n"
    elif block["type"] == "bookmark":
        url = block["bookmark"]["url"]
        markdown += f"[bookmark]({url})\n"
    elif block["type"] == "code":
        rich_text = block["code"]["rich_text"]
        if len(rich_text) > 0:
            text = ""
            for text_obj in rich_text:
                text += text_obj["plain_text"]
            lang = block["code"]["language"]
        markdown += "```" + lang + "\n" + text + "\n```\n"
    elif block["type"] == "equation":
        expression = block["equation"]["expression"]
        markdown += "$" + expression + "$\n"
    elif block["type"] == "divider":
        markdown += "---\n"

    if block.get("children", []):
        for child in block["children"]:
            markdown += block2markdown(child, level=level + 1)

    if block["type"] == "toggle":
        markdown += "</details>\n"

    if level == 0:
        markdown += "\n"

    return markdown


def blocks2markdown(blocks: list[dict[str, Any]]) -> str:
    markdown = ""
    for block in blocks:
        markdown += block2markdown(block)
    return markdown


def make_batch(
    iterable: list[Any], batch_size: int = 1, overlap: int = 0
) -> Generator[list[Any], None, None]:
    """
    Make batch from iterable. This is useful to avoid the limitation of the number of blocks
    per request in Notion API.

    Parameters
    ----------
    iterable : list
        List of elements
    batch_size : int
        Size of batch
    overlap : int
        Overlap between batches

    Returns
    -------
    Generator
        Generator of batch
    """
    if overlap >= batch_size:
        raise ValueError("overlap must be less than batch_size")

    length = len(iterable)

    st: int = 0
    while st < length:
        en = min(st + batch_size, length)
        batch = iterable[st:en]
        yield batch

        if en == length:
            break

        st += batch_size - overlap
