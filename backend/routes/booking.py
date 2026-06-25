from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from utils.mock_data import get_flights, get_hotels
import uuid
from datetime import datetime
from db.supabase_client import insert_booking, get_all_bookings, delete_booking

router = APIRouter()

class BookingConfirmRequest(BaseModel):
    flight_no: str
    airline: str
    origin: str
    destination: str
    departure: str
    arrival: str
    duration: str
    price: float
    travel_date: str = ""

@router.get("/flights")
def flights():
    return get_flights()

@router.get("/hotels")
def hotels():
    return get_hotels()

@router.post("/confirm")
async def confirm_booking(req: BookingConfirmRequest):
    booking_id = "YT" + str(uuid.uuid4())[:6].upper()
    booking = {
        "booking_id":   booking_id,
        "status":       "confirmed",
        "flight_no":    req.flight_no,
        "airline":      req.airline,
        "origin":       req.origin,
        "destination":  req.destination,
        "route":        f"{req.origin} → {req.destination}",
        "departure":    req.departure,
        "arrival":      req.arrival,
        "duration":     req.duration,
        "price":        req.price,
        "travel_date":  req.travel_date or datetime.now().strftime("%d %b %Y"),
        "booked_at":    datetime.now().strftime("%d %b %Y, %I:%M %p"),
        "seat":         "14C",
        "pnr":          "YT" + str(uuid.uuid4())[:5].upper(),
    }
    saved = await insert_booking(booking)
    return saved

@router.get("/confirmed")
async def get_confirmed():
    return await get_all_bookings()

@router.delete("/confirmed/{booking_id}")
async def cancel(booking_id: str):
    deleted = await delete_booking(booking_id)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Booking {booking_id} not found")
    return {"cancelled": booking_id}
