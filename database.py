import os
import sqlite3

from datatypes import EmergencyContact, Patient

DATABASE_PATH = "./clients.sqlite"


class DatabaseConnection:

    PATH = "./clients.sqlite"

    def __init__(self) -> None:
        if os.path.isfile(DATABASE_PATH):
            self.db = sqlite3.connect(DatabaseConnection.PATH)
            self.c = self.db.cursor()
        else:
            print("ERROR: Patient database file not found.")
            print("!! Please open the project from its root directory. !!")

    # Reconstuct the database
    def rebuild(self) -> None:
        with open(DATABASE_PATH, "w") as file:
            file.write("")

        self.c.execute(
            """CREATE TABLE patients(
            id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            firstname TEXT NOT NULL,
            lastname TEXT NOT NULL,
            address TEXT NOT NULL,
            postcode TEXT NOT NULL,
            heartrate INTEGER,
            longitude TEXT,
            latitude TEXT
        )
        """
        )
        self.c.execute(
            """CREATE TABLE emergency_contacts(
                id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                patient_id INTEGER NOT NULL,
                firstname TEXT NOT NULL,
                lastname TEXT NOT NULL,
                relationship TEXT NOT NULL,
                phonenumber TEXT NOT NULL,
                FOREIGN KEY (patient_id) REFERENCES patients(id)
            )
            """
        )
        self.c.execute(
            """CREATE TABLE allergies(
                id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                patient_id INTEGER NOT NULL,
                name NOT NULL,
                FOREIGN KEY (patient_id) REFERENCES patients(id)
            )
            """
        )

    # Get a list of patient ids from the database
    def get_patient_ids(self) -> list:
        self.c.execute(
            """SELECT id
               FROM patients"""
        )
        return [record[0] for record in self.c.fetchall()]

    # Fetch a patient record from the database
    def get_patient(self, patient_id: int) -> Patient:
        self.c.execute(
            """SELECT id, firstname, lastname, address, postcode, heartrate, longitude, latitude
            FROM patients
            WHERE id = ?""",
            [patient_id],
        )
        patient_record = self.c.fetchone()
        if patient_record is None:
            return None

        self.c.execute(
            """SELECT name
               FROM allergies
               WHERE patient_id = ?""",
            [patient_id],
        )
        allergies = [record[0] for record in self.c.fetchall()]

        self.c.execute(
            """SELECT firstname, lastname, relationship, phonenumber
               FROM emergency_contacts
               WHERE patient_id = ?""",
            [patient_id],
        )
        emergency_contacts = [
            EmergencyContact(*record) for record in self.c.fetchall()
        ]

        return Patient(
            *patient_record[0:5],
            allergies,
            emergency_contacts,
            *patient_record[5:]
        )
