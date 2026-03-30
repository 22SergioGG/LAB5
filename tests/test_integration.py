from src.models import Apartment
from src.manager import Manager
from src.models import Parameters
from src.models import ApartmentSettlement


def test_load_data():
    parameters = Parameters()
    manager = Manager(parameters)
    assert isinstance(manager.apartments, dict)
    assert isinstance(manager.tenants, dict)
    assert isinstance(manager.transfers, list)
    assert isinstance(manager.bills, list)

    for apartment_key, apartment in manager.apartments.items():
        assert isinstance(apartment, Apartment)
        assert apartment.key == apartment_key

def test_tenants_in_manager():
    parameters = Parameters()
    manager = Manager(parameters)
    assert len(manager.tenants) > 0
    names = [tenant.name for tenant in manager.tenants.values()]
    for tenant in ['Jan Nowak', 'Adam Kowalski', 'Ewa Adamska']:
        assert tenant in names

def test_if_tenants_have_valid_apartment_keys():
    parameters = Parameters()
    manager = Manager(parameters)
    assert manager.check_tenants_apartment_keys() == True

    manager.tenants['tenant-1'].apartment = 'invalid-key'
    assert manager.check_tenants_apartment_keys() == False

def test_create_apartment_settlement_with_and_without_bills():
    parameters = Parameters()
    manager = Manager(parameters)

    apartment_key = list(manager.apartments.keys())[0]

    year = 2023
    month = 1

    expected_bills = 0.0
    for bill in manager.bills:
        if (
            bill.apartment == apartment_key
            and bill.settlement_year == year
            and bill.settlement_month == month
        ):
            expected_bills += bill.amount_pln

    settlement = manager.create_apartment_settlement(apartment_key, year, month)

    assert settlement is not None
    assert isinstance(settlement, ApartmentSettlement)
    assert settlement.apartment == apartment_key
    assert settlement.year == year
    assert settlement.month == month
    assert settlement.total_bills_pln == expected_bills
    assert settlement.total_rent_pln == 0.0
    assert settlement.total_due_pln == -expected_bills
    assert settlement.total_due_pln <= 0
    assert settlement.total_bills_pln >= 0

    empty_year = 1999
    empty_month = 12

    settlement_empty = manager.create_apartment_settlement(
        apartment_key, empty_year, empty_month
    )

    assert settlement_empty is not None
    assert settlement_empty.total_bills_pln == 0.0
    assert settlement_empty.total_due_pln == 0.0
    assert settlement_empty.year == empty_year
    assert settlement_empty.month == empty_month

def test_create_tenant_settlements():
    parameters = Parameters()
    manager = Manager(parameters)

    apartment_key = list(manager.apartments.keys())[0]
    year = 2023
    month = 1

    apartment_settlement = manager.create_apartment_settlement(
        apartment_key, year, month
    )

    tenant_settlements = manager.create_tenant_settlements(
        apartment_settlement
    )

    tenants_in_apartment = [
        (key, t) for key, t in manager.tenants.items()
        if t.apartment == apartment_key
    ]

    tenants_count = len(tenants_in_apartment)
    total_bills = apartment_settlement.total_bills_pln

    if tenants_count == 0:
        assert tenant_settlements == []

    elif tenants_count == 1:
        assert len(tenant_settlements) == 1
        ts = tenant_settlements[0]

        assert ts.tenant == tenants_in_apartment[0][0]
        assert ts.apartment_settlement == apartment_key
        assert ts.year == year
        assert ts.month == month
        assert ts.bills_pln == total_bills
        assert ts.total_due_pln == -total_bills
        assert ts.rent_pln == 0.0
        assert ts.balance_pln == 0.0

    else:
        assert len(tenant_settlements) == tenants_count

        expected_share = total_bills / tenants_count

        for ts in tenant_settlements:
            assert ts.apartment_settlement == apartment_key
            assert ts.year == year
            assert ts.month == month
            assert ts.bills_pln == expected_share
            assert ts.total_due_pln == -expected_share
            assert ts.rent_pln == 0.0
            assert ts.balance_pln == 0.0
            assert ts.bills_pln >= 0

        total_split = sum(ts.bills_pln for ts in tenant_settlements)
        assert round(total_split, 2) == round(total_bills, 2)

        tenant_keys = [key for key, _ in tenants_in_apartment]
        settlement_keys = [ts.tenant for ts in tenant_settlements]

        for key in tenant_keys:
            assert key in settlement_keys