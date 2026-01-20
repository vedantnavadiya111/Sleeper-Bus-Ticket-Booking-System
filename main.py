from __future__ import annotations

from typing import Annotated, Literal

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(title="Sleeper Bus Ticket Booking System", version="0.1.0")


TOTAL_SEATS = 30

STATIONS: list[str] = [
    "Ahmedabad (Paldi)",
    "Nadiad",
    "Anand",
    "Vadodara",
    "Bharuch",
    "Surat",
    "Navsari",
    "Valsad",
    "Vapi",
    "Mumbai (Dadar)",
]

DEFAULT_PICKUP_STATION = STATIONS[0]
DEFAULT_DROP_STATION = STATIONS[-1]


class Station(BaseModel):
    sequence: int
    name: str


class Seat(BaseModel):
    seat_id: int
    seat_label: str
    seat_type: Literal["sleeper"] = "sleeper"
    is_booked: bool


class Booking(BaseModel):
    seat_id: int
    passenger_name: str = Field(min_length=2, max_length=80)
    pickup_station: str = Field(default=DEFAULT_PICKUP_STATION, max_length=60)
    drop_station: str = Field(default=DEFAULT_DROP_STATION, max_length=60)
    meal_preference: str | None = Field(default=None, max_length=60)


class BookRequest(BaseModel):
    seat_id: Annotated[int, Field(ge=1, le=TOTAL_SEATS)]
    passenger_name: str = Field(min_length=2, max_length=80)
    pickup_station: str = Field(default=DEFAULT_PICKUP_STATION, max_length=60)
    drop_station: str = Field(default=DEFAULT_DROP_STATION, max_length=60)
    meal_preference: str | None = Field(default=None, max_length=60)


class MealRequest(BaseModel):
    seat_id: Annotated[int, Field(ge=1, le=TOTAL_SEATS)]
    meal_preference: str = Field(min_length=2, max_length=60)


bookings: list[Booking] = []


def _normalize_station_name(station_name: str) -> str:
    return station_name.strip()


def _validate_route_stations(pickup_station: str, drop_station: str) -> tuple[str, str]:
    normalized_pickup = _normalize_station_name(pickup_station)
    normalized_drop = _normalize_station_name(drop_station)

    if normalized_pickup not in STATIONS:
        raise HTTPException(status_code=400, detail="Invalid pickup_station")
    if normalized_drop not in STATIONS:
        raise HTTPException(status_code=400, detail="Invalid drop_station")

    pickup_index = STATIONS.index(normalized_pickup)
    drop_index = STATIONS.index(normalized_drop)
    if pickup_index >= drop_index:
        raise HTTPException(status_code=400, detail="pickup_station must be before drop_station")

    return normalized_pickup, normalized_drop


def _seat_label(seat_id: int) -> str:
    deck = "U" if seat_id <= 15 else "L"
    position = seat_id if seat_id <= 15 else seat_id - 15
    return f"{deck}{position:02d}"


def _find_booking_index(seat_id: int) -> int | None:
    for index, booking in enumerate(bookings):
        if booking.seat_id == seat_id:
            return index
    return None


def _is_seat_booked(seat_id: int) -> bool:
    return _find_booking_index(seat_id) is not None


def _seed_initial_bookings() -> None:
    if bookings:
        return

    # Deterministic seed data keeps the prototype consistent across restarts.
    for seat_id, passenger_name, meal in [
        (2, "Riya Shah", "Vegetarian"),
        (7, "Aarav Mehta", "Jain"),
        (16, "Neha Patel", "Vegetarian"),
        (23, "Kabir Desai", "Non-Vegetarian"),
        (29, "Ishita Joshi", "Vegetarian"),
    ]:
        bookings.append(
            Booking(
                seat_id=seat_id,
                passenger_name=passenger_name,
                pickup_station=DEFAULT_PICKUP_STATION,
                drop_station=DEFAULT_DROP_STATION,
                meal_preference=meal,
            )
        )


_seed_initial_bookings()


@app.get("/seats", response_model=list[Seat])
def list_seats() -> list[Seat]:
    return [
        Seat(
            seat_id=seat_id,
            seat_label=_seat_label(seat_id),
            is_booked=_is_seat_booked(seat_id),
        )
        for seat_id in range(1, TOTAL_SEATS + 1)
    ]


@app.get("/stations", response_model=list[Station])
def list_stations() -> list[Station]:
    return [Station(sequence=index + 1, name=station_name) for index, station_name in enumerate(STATIONS)]


@app.post("/book", response_model=Booking)
def book_seat(request: BookRequest) -> Booking:
    if _is_seat_booked(request.seat_id):
        raise HTTPException(status_code=409, detail="Seat is already booked")

    pickup_station, drop_station = _validate_route_stations(request.pickup_station, request.drop_station)

    booking = Booking(
        seat_id=request.seat_id,
        passenger_name=request.passenger_name.strip(),
        pickup_station=pickup_station,
        drop_station=drop_station,
        meal_preference=request.meal_preference.strip() if request.meal_preference else None,
    )
    bookings.append(booking)
    return booking


@app.post("/meal", response_model=Booking)
def add_meal_to_booking(request: MealRequest) -> Booking:
    booking_index = _find_booking_index(request.seat_id)
    if booking_index is None:
        raise HTTPException(status_code=404, detail="Booking not found for this seat")

    existing_booking = bookings[booking_index]
    updated_booking = existing_booking.model_copy(update={"meal_preference": request.meal_preference.strip()})
    bookings[booking_index] = updated_booking
    return updated_booking


@app.delete("/cancel/{seat_id}")
def cancel_booking(seat_id: Annotated[int, Field(ge=1, le=TOTAL_SEATS)]) -> dict:
    booking_index = _find_booking_index(seat_id)
    if booking_index is None:
        raise HTTPException(status_code=404, detail="No active booking for this seat")

    cancelled_booking = bookings.pop(booking_index)
    return {
        "status": "cancelled",
        "seat_id": seat_id,
        "passenger_name": cancelled_booking.passenger_name,
    }
