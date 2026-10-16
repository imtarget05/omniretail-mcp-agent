"""
Input Guardrail: Prompt Injection & Business Policy Violation Check
Blocks attacks attempting to manipulate prices to 0đ, override system instructions, or discuss off-topic domains.
"""

import re
from typing import Tuple

INJECTION_PATTERNS = [
    r"ignore previous instructions",
    r"quên hết",
    r"giảm giá .* về 0",
    r"đổi giá .* về 0",
    r"về 0đ",
    r"giá 0đ",
    r"bán với giá 0",
    r"hạ giá xuống 0",
    r"hãy đóng vai hacker",
    r"act as dan",
    r"jailbreak"
]

def check_input_guardrail(text: str) -> Tuple[bool, str]:
    """
    Returns (is_safe: bool, message: str)
    """
    lowered = text.lower()
    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, lowered):
            return False, "Cảnh báo bảo mật: Yêu cầu của bạn vi phạm chính sách bán hàng của Thế Giới Di Động (ngăn chặn thao túng giá hoặc tấn công Prompt Injection)."
    return True, "Safe"
