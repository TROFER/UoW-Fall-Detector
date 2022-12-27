from database import DatabaseConnection

PREFIX_INSERT_PATIENT = """INSERT INTO patients (firstname, lastname, address, postcode)
                           VALUES (?, ?, ?, ?)"""

PREFIX_INSERT_ALLERGY = """INSERT INTO allergies (patient_id, name)
                           VALUES (?, ?)"""

PREFIX_INSERT_EMERGENCY_CONTACT = """INSERT INTO emergency_contacts (patient_id, firstname, lastname, relationship, phonenumber)
                                     VALUES (?, ?, ?, ?, ?)"""

if __name__ == "__main__":
    database = DatabaseConnection()
    database.rebuild()

    # Create Some Patients
    database.c.execute(
        PREFIX_INSERT_PATIENT,
        [
            "Hennifer",
            "Robinson",
            "2726 George Street, Headdington, Oxford",
            "IV3 6LF",
        ],
    )

    database.c.execute(
        PREFIX_INSERT_PATIENT,
        [
            "Daisy",
            "Riley",
            "6 Jedburgh Road, Arbury, Cambridgeshire",
            "EH46 7AD",
        ],
    )

    database.c.execute(
        PREFIX_INSERT_PATIENT,
        ["Eve", "Watkins", "2225 Princes Street, Twerton, Bath", "ER46 7FD"],
    )

    database.c.execute(
        PREFIX_INSERT_PATIENT,
        [
            "Rosie",
            "Sims",
            "12 Kings Cross, Shepton Mallet, Somerset",
            "IV3 6LF",
        ],
    )

    database.c.execute(
        PREFIX_INSERT_PATIENT,
        [
            "Zak",
            "Davey",
            "53 Prestwick Road, Eastleigh, Hampshire",
            "DD10 4SG",
        ],
    )

    database.c.execute(
        PREFIX_INSERT_PATIENT,
        [
            "Francesca",
            "Houghton",
            "77 Gloddaeth Street, East Cowes, Isle of Wight",
            "RG42 6RL",
        ],
    )

    # Create Some Allergies
    database.c.execute(PREFIX_INSERT_ALLERGY, [1, "Penicilin"])
    database.c.execute(PREFIX_INSERT_ALLERGY, [2, "Sulfonamides "])
    database.c.execute(PREFIX_INSERT_ALLERGY, [2, "Anticonvulsants"])
    database.c.execute(PREFIX_INSERT_ALLERGY, [4, "Aspirin"])
    database.c.execute(PREFIX_INSERT_ALLERGY, [3, "Ibuprofen"])

    # Create Some Emergency Contacts
    database.c.execute(
        PREFIX_INSERT_EMERGENCY_CONTACT,
        [1, "Callum", "Leonard", "Son", "+44 07707313497"],
    )
    database.c.execute(
        PREFIX_INSERT_EMERGENCY_CONTACT,
        [1, "Zoe", "Jackson", "Neighbour", "+44 07756391172"],
    )
    database.c.execute(
        PREFIX_INSERT_EMERGENCY_CONTACT,
        [2, "Daniel", "Griffiths", "Son", "+44 07009321533"],
    )
    database.c.execute(
        PREFIX_INSERT_EMERGENCY_CONTACT,
        [3, "Imogen", "Evans", "Brother", "+44 07961659078"],
    )
    database.c.execute(
        PREFIX_INSERT_EMERGENCY_CONTACT,
        [4, "Lewis", "Webb", "Private Care Provider", "+44 07849758226"],
    )
    database.c.execute(
        PREFIX_INSERT_EMERGENCY_CONTACT,
        [4, "Eve", "Ali", "Daughter", "+44 07003606637"],
    )
    database.c.execute(
        PREFIX_INSERT_EMERGENCY_CONTACT,
        [5, "Rachel", "Clark", "Daughter", "+44 07032370112"],
    )
    database.c.execute(
        PREFIX_INSERT_EMERGENCY_CONTACT,
        [5, "Naomi", "Clark", "Daughter", "+44 07982542821"],
    )
    database.c.execute(
        PREFIX_INSERT_EMERGENCY_CONTACT,
        [6, "Joshua", "Harding", "Son", "+44 07837834577"],
    )
    database.c.execute(
        PREFIX_INSERT_EMERGENCY_CONTACT,
        [6, "Paige ", "Harding", "Daughter", "+44 07717440282"],
    )

    database.db.commit()
