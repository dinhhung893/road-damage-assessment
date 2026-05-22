"""Centralized UI strings — Vietnamese (primary) and English."""

from __future__ import annotations

_STRINGS: dict[str, dict[str, str]] = {
    "vi": {
        # --- Window ---
        "app_title": "Hệ thống Đánh giá Hư hỏng Mặt đường",
        "app_subtitle": "Phát hiện hư hỏng & Tính chỉ số PCI",

        # --- Menu ---
        "menu_file": "Tệp",
        "menu_analysis": "Phân tích",
        "menu_view": "Xem",
        "menu_help": "Trợ giúp",
        "action_open_image": "Mở ảnh",
        "action_open_folder": "Mở thư mục",
        "action_run_detection": "Phát hiện hư hỏng",
        "action_save_image": "Lưu ảnh đã gán nhãn",
        "action_export_report": "Xuất báo cáo",
        "action_settings": "Cài đặt",
        "action_theme_toggle": "Đổi giao diện",
        "action_open_output": "Mở thư mục kết quả",
        "action_exit": "Thoát",
        "action_about": "Giới thiệu",
        "action_prev_image": "Ảnh trước",
        "action_next_image": "Ảnh sau",

        # --- Toolbar ---
        "tb_open_image": "Mở ảnh",
        "tb_open_folder": "Mở thư mục",
        "tb_run": "Phát hiện",
        "tb_save": "Lưu ảnh",
        "tb_export": "Xuất CSV",
        "tb_settings": "Cài đặt",
        "tb_theme": "Giao diện",

        # --- Status bar ---
        "status_ready": "Sẵn sàng",
        "status_detecting": "Đang phát hiện hư hỏng…",
        "status_done": "Hoàn thành — {n} phát hiện, PCI = {pci}",
        "status_error": "Lỗi: {msg}",
        "status_no_image": "Chưa mở ảnh",

        # --- PCI Panel ---
        "pci_title": "Kết quả PCI",
        "pci_score": "Điểm PCI",
        "pci_rating": "Phân loại",
        "pci_cdv": "GT sửa chữa (CDV)",
        "pci_maintenance": "Khuyến nghị bảo dưỡng",
        "pci_no_result": "Chưa chạy phát hiện",

        # --- Damage Table ---
        "table_code": "Mã",
        "table_type": "Loại hư hỏng",
        "table_severity": "Mức độ",
        "table_density": "Mật độ (%)",
        "table_deduct": "GT khấu trừ",
        "table_confidence": "Độ tin cậy",
        "table_summary": "Tổng kết",
        "table_no_data": "Không có dữ liệu",

        # --- Damage type names ---
        "type_D00": "Vết nứt dọc",
        "type_D10": "Vết nứt ngang",
        "type_D20": "Vết nứt da cá",
        "type_D40": "Ổ gà",
        "type_UNKNOWN": "Không xác định",

        # --- Severity ---
        "severity_Low": "Thấp",
        "severity_Medium": "Trung bình",
        "severity_High": "Cao",

        # --- PCI Rating ---
        "rating_Good": "Tốt",
        "rating_Satisfactory": "Hài lòng",
        "rating_Fair": "Trung bình",
        "rating_Poor": "Kém",
        "rating_Very Poor": "Rất kém",
        "rating_Failed": "Hỏng",

        # --- Settings Dialog ---
        "settings_title": "Cài đặt",
        "settings_model_path": "Đường dẫn model",
        "settings_confidence": "Ngưỡng tin cậy",
        "settings_unit_area": "Diện tích đơn vị mẫu (sq ft)",
        "settings_pci_data": "Đường dẫn dữ liệu PCI",
        "settings_language": "Ngôn ngữ",
        "settings_output_dir": "Thư mục xuất",
        "settings_save": "Lưu",
        "settings_cancel": "Hủy",

        # --- File Dialogs ---
        "filter_images": "Ảnh (*.jpg *.jpeg *.png *.bmp)",
        "dialog_open_image": "Chọn ảnh để phân tích",
        "dialog_open_folder": "Chọn thư mục chứa ảnh",
        "dialog_save_image": "Lưu ảnh đã gán nhãn",
        "dialog_save_report": "Xuất báo cáo CSV",

        # --- Messages ---
        "msg_no_detections": "Không phát hiện hư hỏng nào",
        "msg_detection_complete": "Phát hiện hoàn thành",
        "msg_export_success": "Xuất báo cáo thành công: {path}",
        "msg_export_fail": "Xuất báo cáo thất bại",
        "msg_save_success": "Đã lưu ảnh: {path}",
        "msg_image_loaded": "Đã tải ảnh: {name}",
        "msg_batch_start": "Xử lý {n} ảnh…",
        "msg_batch_done": "Hoàn thành xử lý {n} ảnh",
        "msg_batch_progress": "Đang xử lý ảnh {i}/{n}: {name}",

        # --- Batch results ---
        "batch_col_image": "Ảnh",
        "batch_col_pci": "PCI",
        "batch_col_rating": "Phân loại",
        "batch_col_detections": "Số phát hiện",
        "batch_section_pci": "PCI đoạn đường (trung bình)",
    },
    "en": {
        # --- Window ---
        "app_title": "Road Damage Assessment System",
        "app_subtitle": "Damage Detection & PCI Calculation",

        # --- Menu ---
        "menu_file": "File",
        "menu_analysis": "Analysis",
        "menu_view": "View",
        "menu_help": "Help",
        "action_open_image": "Open Image",
        "action_open_folder": "Open Folder",
        "action_run_detection": "Run Detection",
        "action_save_image": "Save Annotated Image",
        "action_export_report": "Export Report",
        "action_settings": "Settings",
        "action_theme_toggle": "Toggle Theme",
        "action_open_output": "Open Output Folder",
        "action_exit": "Exit",
        "action_about": "About",
        "action_prev_image": "Previous Image",
        "action_next_image": "Next Image",

        # --- Toolbar ---
        "tb_open_image": "Open",
        "tb_open_folder": "Folder",
        "tb_run": "Detect",
        "tb_save": "Save",
        "tb_export": "CSV",
        "tb_settings": "Settings",
        "tb_theme": "Theme",

        # --- Status bar ---
        "status_ready": "Ready",
        "status_detecting": "Detecting damage…",
        "status_done": "Done — {n} detections, PCI = {pci}",
        "status_error": "Error: {msg}",
        "status_no_image": "No image loaded",

        # --- PCI Panel ---
        "pci_title": "PCI Results",
        "pci_score": "PCI Score",
        "pci_rating": "Rating",
        "pci_cdv": "Corrected Deduct Value",
        "pci_maintenance": "Maintenance Recommendation",
        "pci_no_result": "No detection run yet",

        # --- Damage Table ---
        "table_code": "Code",
        "table_type": "Damage Type",
        "table_severity": "Severity",
        "table_density": "Density (%)",
        "table_deduct": "Deduct Value",
        "table_confidence": "Confidence",
        "table_summary": "Summary",
        "table_no_data": "No data",

        # --- Damage type names ---
        "type_D00": "Longitudinal Crack",
        "type_D10": "Transverse Crack",
        "type_D20": "Alligator Crack",
        "type_D40": "Pothole",
        "type_UNKNOWN": "Unknown",

        # --- Severity ---
        "severity_Low": "Low",
        "severity_Medium": "Medium",
        "severity_High": "High",

        # --- PCI Rating ---
        "rating_Good": "Good",
        "rating_Satisfactory": "Satisfactory",
        "rating_Fair": "Fair",
        "rating_Poor": "Poor",
        "rating_Very Poor": "Very Poor",
        "rating_Failed": "Failed",

        # --- Settings Dialog ---
        "settings_title": "Settings",
        "settings_model_path": "Model Path",
        "settings_confidence": "Confidence Threshold",
        "settings_unit_area": "Sample Unit Area (sq ft)",
        "settings_pci_data": "PCI Data Path",
        "settings_language": "Language",
        "settings_output_dir": "Output Directory",
        "settings_save": "Save",
        "settings_cancel": "Cancel",

        # --- File Dialogs ---
        "filter_images": "Images (*.jpg *.jpeg *.png *.bmp)",
        "dialog_open_image": "Select Image to Analyze",
        "dialog_open_folder": "Select Image Folder",
        "dialog_save_image": "Save Annotated Image",
        "dialog_save_report": "Export CSV Report",

        # --- Messages ---
        "msg_no_detections": "No damage detected",
        "msg_detection_complete": "Detection complete",
        "msg_export_success": "Report exported: {path}",
        "msg_export_fail": "Export failed",
        "msg_save_success": "Image saved: {path}",
        "msg_image_loaded": "Image loaded: {name}",
        "msg_batch_start": "Processing {n} images…",
        "msg_batch_done": "Finished processing {n} images",
        "msg_batch_progress": "Processing image {i}/{n}: {name}",

        # --- Batch results ---
        "batch_col_image": "Image",
        "batch_col_pci": "PCI",
        "batch_col_rating": "Rating",
        "batch_col_detections": "Detections",
        "batch_section_pci": "Section PCI (average)",
    },
}

# Default language
_DEFAULT_LANG = "vi"


def get_string(key: str, lang: str = "", **kwargs) -> str:
    """Get a UI string by key, with optional format arguments.

    Args:
        key: String key (e.g. "app_title", "status_done")
        lang: Language code ("vi" or "en"). Defaults to config or "vi".
        **kwargs: Format arguments (e.g. n=5, pci=92.2)

    Returns:
        Formatted string in requested language, or key itself if not found.
    """
    if not lang:
        lang = _DEFAULT_LANG

    strings = _STRINGS.get(lang, {})
    text = strings.get(key, _STRINGS.get("vi", {}).get(key, key))

    if kwargs:
        try:
            return text.format(**kwargs)
        except (KeyError, IndexError):
            return text

    return text


def set_default_language(lang: str) -> None:
    """Set the default language for get_string() calls."""
    global _DEFAULT_LANG
    if lang in _STRINGS:
        _DEFAULT_LANG = lang


def get_damage_type_name(code: str, lang: str = "") -> str:
    """Get localized damage type name from ASTM code.

    Args:
        code: ASTM damage code (e.g. "D00", "D10", "D20", "D40")
        lang: Language code. Defaults to current default.

    Returns:
        Localized damage type name.
    """
    return get_string(f"type_{code}", lang)


def get_severity_name(severity: str, lang: str = "") -> str:
    """Get localized severity name.

    Args:
        severity: Severity level ("Low", "Medium", "High")
        lang: Language code. Defaults to current default.

    Returns:
        Localized severity name.
    """
    return get_string(f"severity_{severity}", lang)


def get_rating_name(rating: str, lang: str = "") -> str:
    """Get localized PCI rating name.

    Args:
        rating: PCI rating ("Good", "Satisfactory", "Fair", "Poor", "Very Poor", "Failed")
        lang: Language code. Defaults to current default.

    Returns:
        Localized rating name.
    """
    return get_string(f"rating_{rating}", lang)
