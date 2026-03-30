from src.models import Apartment, ApartmentSettlement, TenantSettlement, Bill, Parameters, Tenant, Transfer


class Manager:
    def __init__(self, parameters: Parameters):
        self.parameters = parameters
        self.apartments = {}
        self.tenants = {}
        self.transfers = []
        self.bills = []
        self.load_data()

    def load_data(self):
        self.apartments = Apartment.from_json_file(self.parameters.apartments_json_path)
        self.tenants = Tenant.from_json_file(self.parameters.tenants_json_path)
        self.transfers = Transfer.from_json_file(self.parameters.transfers_json_path)
        self.bills = Bill.from_json_file(self.parameters.bills_json_path)

    def check_tenants_apartment_keys(self) -> bool:
        for tenant in self.tenants.values():
            if tenant.apartment not in self.apartments:
                return False
        return True

    def get_apartment_costs(self, apartment_key: str, year: int = None, month: int = None):
        if apartment_key not in self.apartments:
            return None

        total_costs = 0.0

        for bill in self.bills:
            if bill.apartment != apartment_key:
                continue

            if year is not None and bill.settlement_year != year:
                continue

            if month is not None and bill.settlement_month != month:
                continue

            total_costs += bill.amount_pln

        return total_costs

    def create_apartment_settlement(self, apartment_key: str, year: int, month: int):
        if apartment_key not in self.apartments:
            return None

        total_bills = self.get_apartment_costs(apartment_key, year=year, month=month) or 0.0

        return ApartmentSettlement(
            apartment=apartment_key,
            month=month,
            year=year,
            total_rent_pln=0.0,
            total_bills_pln=total_bills,
            total_due_pln=0.0 - total_bills,
        )
    
    def create_tenant_settlements(self, apartment_settlement: ApartmentSettlement):
        tenants = [
            (key, t) for key, t in self.tenants.items()
            if t.apartment == apartment_settlement.apartment
        ]

        if len(tenants) == 0:
            return []

        total_bills = apartment_settlement.total_bills_pln
        share = total_bills / len(tenants)

        settlements = []

        for tenant_key, tenant in tenants:
            settlements.append(
                TenantSettlement(
                    tenant=tenant_key,
                    apartment_settlement=apartment_settlement.apartment,
                    month=apartment_settlement.month,
                    year=apartment_settlement.year,
                    rent_pln=0.0,
                    bills_pln=share,
                    total_due_pln=-share,
                    balance_pln=0.0,
                )
            )

        return settlements

   