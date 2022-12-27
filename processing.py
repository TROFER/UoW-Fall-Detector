import queue
import threading
from math import sqrt

from database import DatabaseConnection
from paho.mqtt import client as paho

BROKER_URL = "broker.mqttdashboard.com"
BROKER_PORT = 1883

SUBTOPICS = ["acceleration", "latitude", "longitude", "heartrate"]
TOPIC_PREFIX = "BS2203FD"


class MQTT:
    def __init__(self, processor_callback, dashboard_callback) -> None:
        self.client = paho.Client()
        self.client.on_connect = self._on_connect
        self.client.on_subscribe = self._on_subscribe
        self.client.on_message = self._on_message
        self.database_updates = queue.Queue()

        self.processor_callback = processor_callback
        self.dashboard_callback = dashboard_callback

    def begin(self) -> None:
        self.client.connect(BROKER_URL, BROKER_PORT)
        self._subscribe_patients()
        threading.Thread(target=self._database_thread, daemon=True).start()
        self.client.loop_start()

    def _database_thread(self) -> None:
        database = DatabaseConnection()
        while True:
            update = self.database_updates.get()
            database.c.execute(*update)
            database.db.commit()

    def _subscribe_patients(self) -> None:
        database = DatabaseConnection()
        for patient_id in database.get_patient_ids():
            for subtopic in SUBTOPICS:
                self.client.subscribe(
                    f"{TOPIC_PREFIX}P?{patient_id}/{subtopic}"
                )
            print(f"Subscribing Patient: {TOPIC_PREFIX}P?{patient_id}/Any")

    def _on_connect(self, client, userdata, flags, rc) -> None:
        print(f"Connection Acknowledged with Code: {rc}")

    def _on_subscribe(self, client, userdata, mid, granted_qos) -> None:
        # print(f"MQTT Client Subscribed: {mid} QOS:{granted_qos[0]}")
        pass

    def _on_message(self, client, userdata, message) -> None:
        subtopic = message.topic.split("/")[1]
        patient_id = message.topic.split("?")[1][0]
        payload = message.payload.decode("UTF-8")

        # print(f"Patient {patient_id}", end=" ")
        # print(f"Subtopic: {subtopic}", end=" ")

        if "acceleration" in subtopic:
            acceleration = [float(value) for value in payload.split(",")]
            if self.processor_callback(tuple(acceleration)):
                self.dashboard_callback(int(patient_id))

        elif "longitude" in subtopic:
            # print(f"Longitude: {payload}")
            self.database_updates.put(
                (
                    """UPDATE patients
                       SET longitude = ?
                       WHERE id = ?""",
                    [payload, patient_id],
                )
            )

        elif "latitude" in subtopic:
            # print(f"Latitude: {payload}")
            self.database_updates.put(
                (
                    """UPDATE patients
                       SET latitude = ?
                       WHERE id = ?""",
                    [payload, patient_id],
                )
            )

        elif "heartrate" in subtopic:
            # print(f"Heartrate (BPM): {int(payload)}")
            self.database_updates.put(
                (
                    """UPDATE patients
                       SET heartrate = ?
                       WHERE id = ?""",
                    [payload, patient_id],
                )
            )


class FallDetector:

    THRESHOLD = 10

    @staticmethod
    def analyse(acc: tuple) -> bool:
        try:
            total_acceleration = sqrt(
                (acc[0] * acc[0]) + (acc[1] * acc[1]) + (acc[2] * acc[2])
            )
        except IndexError:
            # Catch if the sample is invalid
            return False

        if total_acceleration > FallDetector.THRESHOLD:
            return True
        else:
            return False
