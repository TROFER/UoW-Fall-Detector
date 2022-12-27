import random
import threading
import time
import tkinter as tk
from tkinter import font, ttk

from paho.mqtt import client as paho

BROKER_URL = "broker.mqttdashboard.com"
BROKER_PORT = 1883

TOPIC_PREFIX = "BS2203FD"


class MQTT:
    def __init__(self) -> None:
        self.client = paho.Client()
        self.client.on_publish = self._on_publish

    def begin(self):
        self.client.connect(BROKER_URL, BROKER_PORT)
        self.client.loop_start()

    def _on_publish(self, client, userdata, mid):
        # print(f"Message Sent, Mid: {mid}")
        pass

    def publish(self, patient_id: str, subtopic: str, payload: str):
        topic = f"{TOPIC_PREFIX}P?{patient_id}/{subtopic}"
        self.client.publish(topic, payload)


class Device(ttk.LabelFrame):
    def __init__(
        self, root: tk.Tk, device_id: int, client: MQTT, *args, **kwargs
    ) -> None:
        super().__init__(root, *args, **kwargs)

        self._client = client
        self._device_id = device_id
        self._state = False

        self._next_acceleration_value = None

        # Tk Display Variables
        self._variable_patient_id = tk.StringVar(value=device_id)
        self._variable_longitude = tk.StringVar()
        self._variable_latitude = tk.StringVar()
        self._variable_heartrate = tk.StringVar(
            value="Reported Heartrate: - BPM"
        )
        self._variable_toggle_button_text = tk.StringVar(value="Enable")

        self._construct()
        self._stylize()
        self._pack()

        threading.Thread(
            target=self._publish_acceleration, daemon=True
        ).start()
        threading.Thread(target=self._publish_heartrate, daemon=True).start()
        threading.Thread(target=self._publish_location, daemon=True).start()

    def _construct(self):
        self._title = ttk.Label(self, text=f"Device {self._device_id}")

        self._widgets = [
            ttk.Label(self, text="Patient ID:"),
            ttk.Entry(self, textvariable=self._variable_patient_id),
            ttk.Label(self, textvariable=self._variable_heartrate),
            ttk.Label(self, text="Reported Location:"),
            ttk.Entry(self, textvariable=self._variable_longitude),
            ttk.Entry(self, textvariable=self._variable_latitude),
            ttk.Button(
                self,
                textvariable=self._variable_toggle_button_text,
                command=self._toggle_state,
            ),
            ttk.Button(
                self,
                text="Simulate Fall",
                command=self._simulate_fall,
            ),
        ]

    def _stylize(self) -> None:
        self.configure(labelwidget=self._title)
        heading = heading = font.Font(
            family="Noto Sans", size=12, weight="bold"
        )
        self._title.configure(font=heading)

    def _pack(self) -> None:
        self._widgets[0].grid(row=0, column=0, sticky="W", padx=4, pady=3)
        self._widgets[1].grid(row=0, column=1, sticky="W", padx=4, pady=3)
        self._widgets[2].grid(row=1, column=0, sticky="W", padx=4, pady=3)
        self._widgets[3].grid(row=2, column=0, sticky="W", padx=4, pady=3)
        self._widgets[4].grid(row=3, column=0, sticky="NESW", padx=4, pady=3)
        self._widgets[5].grid(row=3, column=1, sticky="NESW", padx=4, pady=3)
        self._widgets[6].grid(row=4, column=0, sticky="W", padx=4, pady=5)
        self._widgets[7].grid(row=4, column=1, sticky="W", padx=4, pady=5)

    def _publish_acceleration(self):
        while True:
            while self._state:
                if self._next_acceleration_value is None:
                    payload = ",".join(
                        [
                            str(random.randint(0, 3) + random.random())
                            for i in range(3)
                        ]
                    )
                else:
                    payload = self._next_acceleration_value
                    self._next_acceleration_value = None

                self._client.publish(
                    self._variable_patient_id.get(), "acceleration", payload
                )
                time.sleep(1)
            time.sleep(Dashboard.ACC_INTERVAL)

    def _publish_heartrate(self):
        while True:
            while self._state:
                payload = random.randint(50, 80)
                self._variable_heartrate.set(
                    f"Reported Heartrate: {payload} BPM"
                )
                self._client.publish(
                    self._variable_patient_id.get(), "heartrate", payload
                )
                time.sleep(Dashboard.HEARTRATE_INTERVAL)
            time.sleep(1)

    def _publish_location(self):
        while True:
            while self._state:
                if self._variable_latitude.get():
                    latitude = self._variable_latitude.get()
                    self._client.publish(
                        self._variable_patient_id.get().strip(),
                        "latitude",
                        latitude,
                    )

                if self._variable_longitude.get():
                    longitude = self._variable_longitude.get()
                    self._client.publish(
                        self._variable_patient_id.get().strip(),
                        "longitude",
                        longitude,
                    )
                time.sleep(Dashboard.LOCATION_INTERVAL)
            time.sleep(1)

    def _toggle_state(self):
        self._state = not self._state
        self._variable_toggle_button_text.set(
            "Disable" if self._state else "Enable"
        )

    def _simulate_fall(self):
        self._next_acceleration_value = "10,10,10"


class Dashboard(tk.Tk):

    DEVICES = 4

    ACC_INTERVAL = 1
    HEARTRATE_INTERVAL = 5
    LOCATION_INTERVAL = 30

    def __init__(self, client: MQTT) -> None:
        super().__init__()
        self.title("BS2203 - Client Simulator Dashboard")

        self._client = client

        # Overwrite Default Font
        font_ = font.nametofont("TkDefaultFont")
        font_.configure(family="Noto Sans", size=11)
        self.option_add("*Font", font_)

        # Overwrite Default Window Styles
        self.style = ttk.Style(self)
        self.configure(background="#FFFFFF")
        self.style.configure("TButton", background="#FFFFFF", relief="solid")
        self.style.configure("TLabel", background="#FFFFFF")
        self.style.configure("TLabelframe", background="#FFFFFF")
        self.style.configure("TFrame", background="#FFFFFF")
        self.style.configure("Accent.TFrame", background="#00A6FF")

        self._construct()
        self._stylize()
        self._pack()

    def _construct(self) -> None:
        self._centre_frame = ttk.LabelFrame(self, padding=12)
        self._title = ttk.Label(self._centre_frame, text="Devices")

        self._widgets = [
            Device(self._centre_frame, device_id, client, padding=5)
            for device_id in range(1, 5)
        ]

    def _stylize(self) -> None:
        self._centre_frame.configure(labelwidget=self._title)
        heading = heading = font.Font(
            family="Noto Sans", size=14, weight="bold"
        )
        self._title.configure(font=heading)

    def _pack(self) -> None:
        for i, widget in enumerate(self._widgets):
            widget.grid(row=i, column=0, sticky="NESW", pady=3, padx=3)

        self._centre_frame.grid(row=0, column=0, sticky="NESW", padx=5, pady=5)

    def show(self) -> None:
        self.mainloop()


if __name__ == "__main__":
    client = MQTT()
    client.begin()

    dashboard = Dashboard(client)

    dashboard.show()
