"""Identifier validation; production authentication/authorization are not implemented."""
from __future__ import annotations
import re
_SAFE_IDENTIFIER = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.:-]{0,119}$")
def validate_identifier(value: str) -> str:
    if not _SAFE_IDENTIFIER.fullmatch(value):
        raise ValueError("identifier must contain only letters, digits, '_', '.', ':', or '-'")
    return value
