from __future__ import annotations

from app.core.config import settings
from app.storage.json_repository import JsonRepository
from app.storage.repository import Repository
from app.storage.supabase_repository import SupabaseRepository


def get_repository() -> Repository:
    if settings.storage_mode.lower() == "supabase":
        return SupabaseRepository(settings.supabase_url, settings.supabase_service_key)
    return JsonRepository(settings.data_dir)
