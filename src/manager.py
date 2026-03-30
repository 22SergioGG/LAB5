from src.models import Apartment, Bill, Parameters, Tenant, Transfer


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