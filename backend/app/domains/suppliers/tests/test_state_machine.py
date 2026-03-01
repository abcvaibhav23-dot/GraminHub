from app.domains.suppliers.state_machine import SupplierAction, SupplierStatus, transition


def test_supplier_lifecycle_happy_path():
    s = SupplierStatus.REGISTERED
    s = transition(s, SupplierAction.SUBMIT_DOCUMENTS)
    assert s == SupplierStatus.DOCUMENT_SUBMITTED

    s = transition(s, SupplierAction.START_REVIEW)
    assert s == SupplierStatus.UNDER_REVIEW

    s = transition(s, SupplierAction.VERIFY)
    assert s == SupplierStatus.VERIFIED


def test_supplier_lifecycle_blocks_illegal_transition():
    try:
        transition(SupplierStatus.REGISTERED, SupplierAction.VERIFY)
        assert False, "Expected illegal transition to raise"
    except ValueError:
        assert True

