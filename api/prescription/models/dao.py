from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String

db = SQLAlchemy()


def init_db(app: Flask):
    """
    Initialises the SqlAlchemy with the Flask app
    :param app: A Flask application
    :return: the SqlAlchemy object binded with the Flask app
    """
    db.init_app(app)
    return db


class Prescription(db.Model):
    __tablename__ = "Prescriptions"
    id = Column(Integer, primary_key=True, autoincrement=True)
    clinic_id = Column(Integer)
    physician_id = Column(Integer)
    patient_id = Column(Integer)
    text = Column(String)

    def __init__(self, physician: int, patient: int, clinic: int, text: str):
        """
        Model of the Prescription request
        """
        self.text = text
        self.clinic_id = clinic
        self.physician_id = physician
        self.patient_id = patient

    def save(self):
        """
        Saves this object in the database
        """
        db.session.add(self)
        db.session.flush()

    def commit(self):
        """
        Commits pending changes to the database
        """
        db.session.commit()

    def rollback(self):
        """
        Deletes this object from the database
        """
        db.session.delete(self)
        db.session.commit()
