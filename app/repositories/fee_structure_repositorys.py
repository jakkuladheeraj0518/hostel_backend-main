from sqlalchemy.orm import Session
from app import models

class FeeStructureRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, model, data):
        obj = model(**data.dict())
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def list(self, model):
        return self.db.query(model).all()

    def get(self, model, id: int):
        return self.db.query(model).filter(model.id == id).first()

    def delete(self, model, id: int):
        obj = self.get(model, id)
        if obj:
            self.db.delete(obj)
            self.db.commit()
            return True
        return False
