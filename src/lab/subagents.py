"""GUIDE Phần 1 - Định nghĩa subagent (tác tử con).   >>> SINH VIÊN CÀI ĐẶT <<<

Pseudo-code: guides/pseudocode/02_subagents.md
Kiểm tra:    pytest tests/test_02_agent.py
"""


def get_subagents() -> list[dict]:
    """Trả về danh sách subagent (ít nhất 2, tên khác nhau).

    Mỗi phần tử là một dict có các khóa bắt buộc:
      "name":          tên duy nhất (chữ thường, có thể có dấu gạch ngang)
      "description":   khi nào tác tử chính nên giao việc cho subagent này (viết như một hướng dẫn hành động)
      "system_prompt": chỉ dẫn cho subagent
    Gợi ý vai trò: explorer (đọc và báo cáo), implementer (thực hiện), reviewer (kiểm tra độc lập).
    """
    return [
        {
            "name": "explorer",
            "description": (
                "Delegate before implementation when requirements, shared code, or data formats "
                "need investigation. Ask for relevant specifications and evidence."
            ),
            "system_prompt": (
                "You investigate the delegated task without modifying files. Read the supplied "
                "instructions, relevant README files, docstrings, and representative data. "
                "Identify requirements, shared dependencies, and edge cases. You only know the "
                "context supplied in this delegation; report missing information rather than "
                "inventing it. Return one concise report with file references, evidence, and "
                "recommended next steps."
            ),
        },
        {
            "name": "implementer",
            "description": (
                "Delegate when a defined change or data-processing task requires several steps. "
                "Provide all task rules, relevant file paths, and acceptance criteria."
            ),
            "system_prompt": (
                "You implement only the delegated changes. Read the supplied specifications "
                "and relevant files before acting, and address root causes rather than symptoms. "
                "Preserve files outside the assigned scope. Run relevant tests or scripts and "
                "check outputs against the supplied acceptance criteria. You only know the "
                "context supplied in this delegation; report missing requirements explicitly. "
                "Return one concise report of files actually changed, commands run, observed "
                "results, and unresolved issues. Do not claim success without verification."
            ),
        },
        {
            "name": "reviewer",
            "description": (
                "Delegate after implementation when outputs need an independent check against "
                "task requirements, expected formats, and edge cases."
            ),
            "system_prompt": (
                "You independently review the delegated results without modifying files. "
                "Read the supplied task rules and inspect actual outputs rather than relying "
                "on completion claims. Run relevant checks and examine edge cases and formats. "
                "You only know the context supplied in this delegation; distinguish verified "
                "facts from missing information. Return one concise report of checks performed, "
                "observed results, and actionable findings with file references."
            ),
        },
    ]
