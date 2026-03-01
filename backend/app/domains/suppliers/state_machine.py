"""Supplier verification lifecycle state machine (v2)."""

from __future__ import annotations

from enum import StrEnum


class SupplierStatus(StrEnum):
    REGISTERED = "REGISTERED"
    DOCUMENT_SUBMITTED = "DOCUMENT_SUBMITTED"
    UNDER_REVIEW = "UNDER_REVIEW"
    VERIFIED = "VERIFIED"
    REJECTED = "REJECTED"
    SUSPENDED = "SUSPENDED"


class SupplierAction(StrEnum):
    REGISTER = "REGISTER"
    SUBMIT_DOCUMENTS = "SUBMIT_DOCUMENTS"
    START_REVIEW = "START_REVIEW"
    VERIFY = "VERIFY"
    REJECT = "REJECT"
    SUSPEND = "SUSPEND"
    UNSUSPEND = "UNSUSPEND"


_TRANSITIONS: dict[SupplierStatus, dict[SupplierAction, SupplierStatus]] = {
    SupplierStatus.REGISTERED: {SupplierAction.SUBMIT_DOCUMENTS: SupplierStatus.DOCUMENT_SUBMITTED},
    SupplierStatus.DOCUMENT_SUBMITTED: {SupplierAction.START_REVIEW: SupplierStatus.UNDER_REVIEW},
    SupplierStatus.UNDER_REVIEW: {
        SupplierAction.VERIFY: SupplierStatus.VERIFIED,
        SupplierAction.REJECT: SupplierStatus.REJECTED,
    },
    SupplierStatus.VERIFIED: {SupplierAction.SUSPEND: SupplierStatus.SUSPENDED},
    SupplierStatus.SUSPENDED: {SupplierAction.UNSUSPEND: SupplierStatus.VERIFIED},
}


def transition(current: SupplierStatus, action: SupplierAction) -> SupplierStatus:
    if action not in _TRANSITIONS.get(current, {}):
        raise ValueError(f"Illegal transition: {current} + {action}")
    return _TRANSITIONS[current][action]
