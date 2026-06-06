import os
import uuid
import logging
from fastapi import UploadFile, HTTPException

logger = logging.getLogger(__name__)

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".pdf", ".doc", ".docx"}
MAX_FILE_SIZE = 4 * 1024 * 1024

BLOB_TOKEN = os.environ.get("BLOB_READ_WRITE_TOKEN")


def _safe_filename(original: str) -> str:
    ext = ""
    if "." in original:
        ext = original.rsplit(".", 1)[-1].lower()
        ext = "".join(c for c in ext if c.isalnum())
        ext = f".{ext}" if ext else ""
    return f"{uuid.uuid4().hex}{ext}"


def upload_file(file: UploadFile, prefix: str = "uploads") -> str:
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename is required")

    ext = "." + file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"File type '{ext}' not allowed. Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}"
        )

    content = file.file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File exceeds {MAX_FILE_SIZE // (1024 * 1024)}MB limit"
        )

    safe_name = _safe_filename(file.filename)

    if BLOB_TOKEN:
        logger.info("upload_file: using Vercel Blob storage")
        try:
            from vercel.blob import put as blob_put
            blob_path = f"{prefix}/{safe_name}"
            result = blob_put(
                blob_path,
                content,
                access="public",
                content_type=file.content_type or "application/octet-stream",
                token=BLOB_TOKEN,
            )
            return result.url
        except HTTPException:
            raise
        except ImportError as exc:
            logger.error("Blob upload failed — SDK import error: %s", exc)
            raise HTTPException(status_code=500, detail="File upload to storage failed")
        except Exception as exc:
            logger.error("Blob upload failed: %s: %s", type(exc).__name__, exc)
            raise HTTPException(status_code=500, detail="File upload to storage failed")

    logger.info("Blob upload unavailable, using local fallback — BLOB_READ_WRITE_TOKEN not set")
    local_dir = os.path.join(os.getcwd(), prefix)
    os.makedirs(local_dir, exist_ok=True)
    local_path = os.path.join(local_dir, safe_name)
    with open(local_path, "wb") as f:
        f.write(content)
    return f"{prefix}/{safe_name}"


def delete_file(url_or_path: str) -> None:
    if not url_or_path:
        return
    if BLOB_TOKEN and url_or_path.startswith("http"):
        try:
            from vercel.blob import delete as blob_delete
            blob_delete(url_or_path, token=BLOB_TOKEN)
        except Exception as exc:
            logger.warning("Blob delete failed: %s: %s", type(exc).__name__, exc)
    elif not url_or_path.startswith("http"):
        local_path = os.path.join(os.getcwd(), url_or_path)
        if os.path.exists(local_path):
            os.remove(local_path)
