from app.domains.bookings.state_machine import BookingAction, BookingState, can_transition, transition


def test_booking_state_machine_allows_happy_path():
    s = BookingState.CREATED
    assert can_transition(s, BookingAction.SUBMIT)
    s = transition(s, BookingAction.SUBMIT)
    assert s == BookingState.PENDING_SUPPLIER_APPROVAL

    s = transition(s, BookingAction.ACCEPT)
    assert s == BookingState.ACCEPTED

    s = transition(s, BookingAction.START)
    assert s == BookingState.IN_PROGRESS

    s = transition(s, BookingAction.COMPLETE)
    assert s == BookingState.COMPLETED


def test_booking_state_machine_blocks_illegal_transition():
    try:
        transition(BookingState.CREATED, BookingAction.ACCEPT)
        assert False, "Expected illegal transition to raise"
    except ValueError:
        assert True

