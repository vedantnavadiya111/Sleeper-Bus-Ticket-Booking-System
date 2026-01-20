# Sleeper Bus Ticket Booking System

## Project Title & Description
The Sleeper Bus Ticket Booking System is a prototype application for booking sleeper seats on the Ahmedabad → Mumbai Express route with meal preference integration. It includes a FastAPI backend for seat availability and booking operations, a single-file HTML design prototype for the booking experience, and a mock machine learning workflow that estimates booking confirmation probability using a simple logistic regression model.

## Features
- Seat and station listing endpoints (30-seat sleeper layout plus intermediate stops)
- Booking creation with pickup/drop station selection, passenger name, and optional meal preference
- Meal preference update for an existing booking
- Booking cancellation by seat identifier
- Mock confirmation prediction pipeline (dataset generation, model training, probability output)

## Test Cases

| ID | Scenario | Expected Result |
|---:|---|---|
| TC-01 | List seats via `GET /seats` | Returns 30 seats with stable identifiers and accurate booked/available status |
| TC-02 | Book an available seat via `POST /book` | Creates a booking and marks the seat as booked for subsequent reads |
| TC-03 | Add or update meal via `POST /meal` for an existing booking | Updates the booking meal preference and returns the updated booking |
| TC-04 | Cancel an existing booking via `DELETE /cancel/{seat_id}` | Removes the booking and the seat becomes available again |
| TC-05 (Edge) | Booking a seat that was just taken (two clients book the same seat) | One request succeeds; the other returns an HTTP 409 conflict indicating the seat is already booked |
| TC-06 (UI/UX) | Seat state visual validation in the prototype | Available seats render in a light tone, booked seats render in dark grey and are non-interactive, selected seat renders in blue |
| TC-07 (UI/UX) | Booking Summary panel interaction | Selecting an available seat displays the summary and shows the selected seat label; deselecting hides the summary |
| TC-08 (UI/UX) | Meal dropdown usability | Meal dropdown is visible within the summary and can be changed without layout shift or visual glitches |

## Prototype Link
https://vedantnavadiya111.github.io/Sleeper-Bus-Ticket-Booking-System/

## Tech Stack
- Backend: Python (FastAPI)
- ML: Scikit-learn (LogisticRegression)
- Frontend Prototype: Single HTML file with embedded CSS and minimal JavaScript for UI interactivity
