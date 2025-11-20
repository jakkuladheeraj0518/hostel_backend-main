from app.repositories.fee_structure_repositorys import FeeStructureRepository
from app import models

class FeeStructureService:
    def __init__(self, db):
        self.repo = FeeStructureRepository(db)

    def create_hostel(self, data):
        return self.repo.create(models.Hostel, data)

    def list_hostels(self):
        return self.repo.list(models.Hostel)

    def create_fee_plan(self, data):
        return self.repo.create(models.FeePlan, data)

    def create_deposit(self, data):
        return self.repo.create(models.SecurityDeposit, data)

    def create_mess_charge(self, data):
        return self.repo.create(models.MessCharge, data)

    def create_service(self, data):
        return self.repo.create(models.AdditionalService, data)
