from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    app_name: str = "Bahi-SCAFF API"
    app_version: str = "0.1.0"
    environment: str = os.getenv("BAHI_ENV", "dev")
    allow_origin: str = os.getenv("BAHI_ALLOW_ORIGIN", "*")
    max_error_tolerance_m: float = 0.02
    target_runtime_seconds: float = 5.0
    default_vat_rate: float = 0.2


settings = Settings()
