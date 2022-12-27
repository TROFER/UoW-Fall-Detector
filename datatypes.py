import datetime


# Objective Emergency Contact Record
class EmergencyContact:
    def __init__(
        self,
        firstname: str,
        lastname: str,
        relationship: str,
        phonenumber: str,
    ) -> None:
        self.firstname = firstname
        self.lastname = lastname
        self.relationship = relationship
        self.phonenumber = phonenumber

    def __str__(self) -> str:
        string = f"[{self.relationship}] - "
        string += f"{self.firstname} {self.lastname} - "
        return string + f"{self.phonenumber}"


# Objective Patient Record
class Patient:
    def __init__(
        self,
        id: int,
        firstname: str,
        lastname: str,
        address: str,
        postcode: str,
        allergies: list = [],
        emergency_contacts: list = [],
        heartrate: int = None,
        longitude: str = None,
        latitude: str = None,
    ) -> None:
        self.id = id
        self.firstname = firstname
        self.lastname = lastname
        self.address = address
        self.postcode = postcode
        self.allergies = allergies
        self.emergency_contacts = emergency_contacts
        self.heartrate = heartrate
        self.longitude = longitude
        self.latitude = latitude


class Alert:
    def __init__(
        self, patient: Patient, timestamp: float, location: tuple = None
    ) -> None:
        self.patient = patient
        self.timestamp = timestamp

    def get_datetime_object(self) -> datetime.datetime:
        return datetime.datetime.utcfromtimestamp(self.timestamp)

    def get_location_url(self) -> str:
        URL = "https://maps.google.co.uk/"

        if self.location is None:
            address = self.patient.address.replace(" ", "+")
            return f"{URL}/place/{address}"
        else:
            return f"{URL}/?q=<{self.location[0]}>,<{self.location[1]}>"

    def __str__(self) -> str:
        time = self.get_datetime_object().strftime("%H:%M")
        return f"[{time}] - {self.patient.firstname} {self.patient.lastname}"
