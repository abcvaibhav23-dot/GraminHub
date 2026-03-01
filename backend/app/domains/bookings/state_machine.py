"""Booking lifecycle state machine (v2)."""

from __future__ import annotations

from enum import StrEnum


class BookingState(StrEnum):
    CREATED = "CREATED"
    PENDING_SUPPLIER_APPROVAL = "PENDING_SUPPLIER_APPROVAL"
    ACCEPTED = "ACCEPTED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
    DISPUTED = "DISPUTED"
    RESOLVED = "RESOLVED"


class BookingAction(StrEnum):
    CREATE = "CREATE"
    SUBMIT = "SUBMIT"
    ACCEPT = "ACCEPT"
    START = "START"
    COMPLETE = "COMPLETE"
    CANCEL = "CANCEL"
    RAISE_DISPUTE = "RAISE_DISPUTE"
    RESOLVE = "RESOLVE"


_TRANSITIONS: dict[BookingState, dict[BookingAction, BookingState]] = {
    BookingState.CREATED: {BookingAction.SUBMIT: BookingState.PENDING_SUPPLIER_APPROVAL},
    BookingState.PENDING_SUPPLIER_APPROVAL: {
        BookingAction.ACCEPT: BookingState.ACCEPTED,
        BookingAction.CANCEL: BookingState.CANCELLED,
    },
    BookingState.ACCEPTED: {
        BookingAction.START: BookingState.IN_PROGRESS,
        BookingAction.CANCEL: BookingState.CANCELLED,
        BookingAction.RAISE_DISPUTE: BookingState.DISPUTED,
    },
    BookingState.IN_PROGRESS: {
        BookingAction.COMPLETE: BookingState.COMPLETED,
        BookingAction.RAISE_DISPUTE: BookingState.DISPUTED,
    },
    BookingState.DISPUTED: {BookingAction.RESOLVE: BookingState.RESOLVED},
}


def can_transition(current: BookingState, action: BookingAction) -> bool:
    return action in _TRANSITIONS.get(current, {})


def transition(current: BookingState, action: BookingAction) -> BookingState:
    if not can_transition(current, action):
        raise ValueError(f"Illegal transition: {current} + {action}")
    return _TRANSITIONS[current][action]
