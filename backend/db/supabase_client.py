"""
Supabase Database Client + Repository Functions
"""
import os
import logging
from supabase import create_client, Client

logger = logging.getLogger(__name__)
_client: Client | None = None


def get_supabase() -> Client:
    global _client
    if _client is None:
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_SERVICE_KEY")
        if not url or not key:
            raise RuntimeError("SUPABASE_URL and SUPABASE_SERVICE_KEY must be set.")
        _client = create_client(url, key)
        logger.info("Supabase client initialised.")
    return _client


# ── Booking functions ─────────────────────────────────────────

async def insert_booking(booking: dict) -> dict:
    db = get_supabase()
    result = db.table("bookings").insert(booking).execute()
    if result.data:
        return result.data[0]
    raise RuntimeError("Failed to insert booking")


async def get_all_bookings(user_id: str = "default") -> list:
    db = get_supabase()
    result = db.table("bookings").select("*").order("created_at", desc=True).execute()
    return result.data or []


async def delete_booking(booking_id: str) -> bool:
    db = get_supabase()
    result = db.table("bookings").delete().eq("booking_id", booking_id).execute()
    return bool(result.data)


# ── Expense functions ─────────────────────────────────────────

async def insert_expense(expense: dict) -> dict:
    db = get_supabase()
    result = db.table("expenses").insert(expense).execute()
    if result.data:
        return result.data[0]
    raise RuntimeError("Failed to insert expense")


async def get_all_expenses(user_id: str = "default") -> list:
    db = get_supabase()
    result = db.table("expenses").select("*").order("created_at", desc=True).execute()
    return result.data or []


async def delete_expense(expense_id: str) -> bool:
    db = get_supabase()
    result = db.table("expenses").delete().eq("expense_id", expense_id).execute()
    return bool(result.data)
