import logging
import random
import string
import reflex as rx
from pathlib import Path

try:
    from PIL import Image
except Exception:
    logging.exception("PIL import")
    Image = None

try:
    import pytesseract
except Exception:
    logging.exception("pytesseract import")
    pytesseract = None

try:
    from pyzbar.pyzbar import decode as qr_decode
except Exception:
    logging.exception("pyzbar import")
    qr_decode = None


SCREENSHOT_UPLOAD_ID = "fraudradar_screenshot"
QR_UPLOAD_ID = "fraudradar_qr"
ALLOWED_IMAGE_TYPES = {
    "image/png": [".png"],
    "image/jpeg": [".jpg", ".jpeg"],
    "image/webp": [".webp"],
    "image/bmp": [".bmp"],
}
MAX_IMAGE_BYTES = 6 * 1024 * 1024  # 6MB


def _random_filename(original: str) -> str:
    suffix = Path(original).suffix.lower() or ".png"
    rand = "".join(random.choices(string.ascii_letters + string.digits, k=10))
    return f"{rand}{suffix}"


class UploadState(rx.State):
    is_processing: bool = False
    upload_error: str = ""
    upload_success: str = ""
    last_screenshot_file: str = ""
    last_qr_file: str = ""
    extracted_text: str = ""
    decoded_qr_value: str = ""

    @rx.event
    def reset_upload_messages(self):
        self.upload_error = ""
        self.upload_success = ""

    @rx.event
    async def handle_screenshot_upload(self, files: list[rx.UploadFile]):
        from fraudradar_ai_scam_detection_v2.states.scan_state import ScanState

        self.upload_error = ""
        self.upload_success = ""
        self.extracted_text = ""

        if not files:
            self.upload_error = "No file selected."
            return

        if Image is None or pytesseract is None:
            self.upload_error = (
                "Image OCR is not available on the server. "
                "Please paste the suspicious text manually."
            )
            return

        file = files[0]
        try:
            data = await file.read()
        except Exception as e:
            logging.exception(f"read upload: {e}")
            self.upload_error = "Could not read uploaded file."
            return

        if not data:
            self.upload_error = "Uploaded file is empty."
            return

        if len(data) > MAX_IMAGE_BYTES:
            self.upload_error = "File too large. Maximum size is 6MB."
            return

        original_name = (file.name or "screenshot.png").lower()
        if not any(
            original_name.endswith(ext)
            for exts in ALLOWED_IMAGE_TYPES.values()
            for ext in exts
        ):
            self.upload_error = (
                "Unsupported file type. Use PNG, JPG, WEBP, or BMP."
            )
            return

        self.is_processing = True

        try:
            upload_dir = rx.get_upload_dir()
            upload_dir.mkdir(parents=True, exist_ok=True)
            safe_name = _random_filename(original_name)
            file_path = upload_dir / safe_name
            with file_path.open("wb") as f:
                f.write(data)
            self.last_screenshot_file = safe_name
        except Exception as e:
            logging.exception(f"save upload: {e}")
            self.upload_error = "Could not save uploaded file."
            self.is_processing = False
            return

        try:
            with Image.open(file_path) as img:
                img.load()
                if img.mode not in ("RGB", "L"):
                    img = img.convert("RGB")
                text = pytesseract.image_to_string(img) or ""
        except Exception as e:
            logging.exception(f"OCR: {e}")
            self.upload_error = (
                "Could not read text from this image. "
                "Try a clearer screenshot or paste the text manually."
            )
            self.is_processing = False
            return

        cleaned = " ".join(text.split()).strip()
        if not cleaned or len(cleaned) < 4:
            self.upload_error = (
                "No readable text found in this image. "
                "Try a clearer screenshot or paste the text manually."
            )
            self.is_processing = False
            return

        self.extracted_text = cleaned
        self.upload_success = "Text extracted successfully. Analyzing..."
        self.is_processing = False

        scan = await self.get_state(ScanState)
        scan.input_text = cleaned
        scan.input_type = "image"
        return ScanState.analyze(cleaned, "image")

    @rx.event
    async def handle_qr_upload(self, files: list[rx.UploadFile]):
        from fraudradar_ai_scam_detection_v2.states.scan_state import ScanState

        self.upload_error = ""
        self.upload_success = ""
        self.decoded_qr_value = ""

        if not files:
            self.upload_error = "No file selected."
            return

        if Image is None or qr_decode is None:
            self.upload_error = (
                "QR decoding is not available on the server. "
                "Please paste the QR's URL manually."
            )
            return

        file = files[0]
        try:
            data = await file.read()
        except Exception as e:
            logging.exception(f"read upload: {e}")
            self.upload_error = "Could not read uploaded file."
            return

        if not data:
            self.upload_error = "Uploaded file is empty."
            return

        if len(data) > MAX_IMAGE_BYTES:
            self.upload_error = "File too large. Maximum size is 6MB."
            return

        original_name = (file.name or "qr.png").lower()
        if not any(
            original_name.endswith(ext)
            for exts in ALLOWED_IMAGE_TYPES.values()
            for ext in exts
        ):
            self.upload_error = (
                "Unsupported file type. Use PNG, JPG, WEBP, or BMP."
            )
            return

        self.is_processing = True

        try:
            upload_dir = rx.get_upload_dir()
            upload_dir.mkdir(parents=True, exist_ok=True)
            safe_name = _random_filename(original_name)
            file_path = upload_dir / safe_name
            with file_path.open("wb") as f:
                f.write(data)
            self.last_qr_file = safe_name
        except Exception as e:
            logging.exception(f"save upload: {e}")
            self.upload_error = "Could not save uploaded file."
            self.is_processing = False
            return

        decoded_value = ""
        try:
            with Image.open(file_path) as img:
                img.load()
                results = qr_decode(img)
                if results:
                    raw = results[0].data
                    if isinstance(raw, bytes):
                        decoded_value = raw.decode(
                            "utf-8", errors="replace"
                        ).strip()
                    else:
                        decoded_value = str(raw).strip()
        except Exception as e:
            logging.exception(f"QR decode: {e}")
            self.upload_error = (
                "Could not decode this QR code. "
                "Try a sharper image or paste the URL manually."
            )
            self.is_processing = False
            return

        if not decoded_value:
            self.upload_error = (
                "No QR code detected in this image. "
                "Make sure the QR is fully visible and clear."
            )
            self.is_processing = False
            return

        self.decoded_qr_value = decoded_value
        self.upload_success = f"QR decoded: {decoded_value[:80]}"
        self.is_processing = False

        # Determine if it's a URL/UPI link or other content
        lower = decoded_value.lower()
        if (
            lower.startswith("http://")
            or lower.startswith("https://")
            or lower.startswith("upi://")
        ):
            input_type = "url"
        else:
            input_type = "text"

        scan = await self.get_state(ScanState)
        scan.input_text = decoded_value
        scan.input_type = input_type
        return ScanState.analyze(decoded_value, input_type)