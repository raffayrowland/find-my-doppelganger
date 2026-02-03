import base64
import re
from urllib.parse import urlparse, parse_qs, urljoin

import requests


class GoogleDriveDownloadError(RuntimeError):
    pass


def _extract_drive_file_id(url: str) -> str:
    """
    Supports:
      - https://drive.google.com/uc?id=FILE_ID
      - https://drive.google.com/open?id=FILE_ID
      - https://drive.google.com/file/d/FILE_ID/view?...
      - plain FILE_ID (fallback)
    """
    url = url.strip()

    # If user passed only an ID
    if re.fullmatch(r"[A-Za-z0-9_-]{10,}", url):
        return url

    parsed = urlparse(url)
    qs = parse_qs(parsed.query)

    if "id" in qs and qs["id"]:
        return qs["id"][0]

    m = re.search(r"/file/d/([^/]+)", parsed.path)
    if m:
        return m.group(1)

    raise ValueError(f"Could not extract Google Drive file id from: {url}")


def drive_image_url_to_b64(
    url: str,
    *,
    timeout: float = 60.0,
    chunk_size: int = 256 * 1024,
    session: requests.Session | None = None,
) -> str:
    """
    Download a Google Drive file (typically an image) and return its base64 string.

    Handles common Google Drive download-warning / confirmation flows.
    Raises GoogleDriveDownloadError on quota / HTML interstitial / other failures.
    """
    file_id = _extract_drive_file_id(url)
    download_url = f"https://drive.google.com/uc?export=download&id={file_id}"

    owns_session = session is None
    s = session or requests.Session()

    try:
        # First request (may return the actual file OR an HTML interstitial)
        r = s.get(download_url, stream=True, timeout=timeout)
        r.raise_for_status()

        # If Drive requires confirmation, it often sets a cookie like "download_warning*"
        confirm_token = None
        for k, v in r.cookies.items():
            if k.startswith("download_warning"):
                confirm_token = v
                break

        # Or it may embed a confirm token/link in HTML
        content_type = (r.headers.get("Content-Type") or "").lower()

        def is_probably_html_interstitial(resp: requests.Response) -> bool:
            # If Drive returns HTML page instead of file, it’s usually small-ish and text/html.
            if "text/html" in (resp.headers.get("Content-Type") or "").lower():
                return True
            # Sometimes headers are odd; try sniffing first bytes without consuming all.
            return False

        if confirm_token or is_probably_html_interstitial(r):
            # Read a small portion of body to parse HTML safely
            # (If it's actually the file, we won't do this branch usually)
            html_text = r.text if "text" in content_type or "html" in content_type else ""

            if not confirm_token:
                m = re.search(r"confirm=([0-9A-Za-z_]+)", html_text)
                if m:
                    confirm_token = m.group(1)

            # Some pages include a direct href containing export=download
            if not confirm_token:
                links = re.findall(r'href="([^"]+)"', html_text)
                for link in links:
                    if "export=download" in link:
                        # Make absolute and request it
                        follow = urljoin("https://drive.google.com/", link.replace("&amp;", "&"))
                        r2 = s.get(follow, stream=True, timeout=timeout)
                        r2.raise_for_status()
                        data = r2.content
                        _raise_if_quota_or_html(data, r2.headers.get("Content-Type"))
                        return base64.b64encode(data).decode("ascii")

            if confirm_token:
                confirmed_url = f"https://drive.google.com/uc?export=download&id={file_id}&confirm={confirm_token}"
                r2 = s.get(confirmed_url, stream=True, timeout=timeout)
                r2.raise_for_status()
                data = r2.content
                _raise_if_quota_or_html(data, r2.headers.get("Content-Type"))
                return base64.b64encode(data).decode("ascii")

            # If we reach here, it likely wasn't a direct file response.
            # Fall through to an error with a helpful message.
            body_preview = (html_text[:400] + "...") if html_text else ""
            raise GoogleDriveDownloadError(
                "Google Drive did not return the file directly and no confirm token/link was found. "
                f"Content-Type={content_type}. Preview: {body_preview}"
            )

        # If it was the file directly, stream it into memory
        chunks = []
        for chunk in r.iter_content(chunk_size=chunk_size):
            if chunk:
                chunks.append(chunk)
        data = b"".join(chunks)

        _raise_if_quota_or_html(data, r.headers.get("Content-Type"))
        return base64.b64encode(data).decode("ascii")

    finally:
        if owns_session:
            s.close()


def _raise_if_quota_or_html(data: bytes, content_type: str | None) -> None:
    ct = (content_type or "").lower()
    # Quota page / interstitials are typically HTML
    if "text/html" in ct or data.lstrip().startswith(b"<!doctype html") or data.lstrip().startswith(b"<html"):
        text = ""
        try:
            text = data.decode("utf-8", errors="ignore")
        except Exception:
            pass
        if "Quota exceeded" in text or "Google Drive - Quota exceeded" in text:
            raise GoogleDriveDownloadError("Google Drive download quota exceeded.")
        raise GoogleDriveDownloadError("Expected file bytes, got an HTML page/interstitial instead.")
