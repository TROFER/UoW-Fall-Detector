import queue
import threading
import time
import tkinter as tk
from tkinter import font, messagebox, ttk

from database import DatabaseConnection
from datatypes import Alert
from processing import MQTT, FallDetector


class Sidebar(ttk.LabelFrame):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        # Tk Display Variables
        self._variable_name = tk.StringVar()
        self._variable_location_type = tk.StringVar()
        self._variable_location = tk.StringVar()
        self._variable_heartrate = tk.StringVar()
        self._variable_time_of_fall = tk.StringVar()
        self._variable_alergies = tk.StringVar()
        self._variable_emergency_contacts = tk.StringVar()

        self._variable_location_type.set("Address:")

        # Window Consturction
        self._construct()
        self._stylize()
        self._pack()

    def _construct(self) -> None:
        self._title = ttk.Label(self, text="Alert Details")

        self._widgets = [
            ttk.Label(self, text="Patient Name:"),
            ttk.Label(self, textvariable=self._variable_name),
            ttk.Label(self, textvariable=self._variable_location_type),
            ttk.Label(self, textvariable=self._variable_location),
            ttk.Label(self, text="Last Reported Heartrate:"),
            ttk.Label(self, textvariable=self._variable_heartrate),
            ttk.Label(self, text="Time of Fall:"),
            ttk.Label(self, textvariable=self._variable_time_of_fall),
            ttk.Label(self, text="Medication Alergies:"),
            tk.Listbox(self, listvariable=self._variable_alergies),
            ttk.Label(self, text="Emergency Contacts:"),
            tk.Listbox(self, listvariable=self._variable_emergency_contacts),
        ]

    def _stylize(self) -> None:
        subtitle = font.Font(family="Noto Sans", size=12, weight="bold")
        [
            self._widgets[i].configure(font=subtitle)
            for i in [0, 2, 4, 6, 8, 10]
        ]

        self._widgets[9].configure(
            state="disabled", borderwidth=0, relief="solid", width=40, height=5
        )
        self._widgets[11].configure(
            state="disabled", borderwidth=0, relief="solid", width=40, height=10
        )

        self.configure(labelwidget=self._title)

        heading = font.Font(family="Noto Sans", size=14, weight="bold")
        self._title.configure(font=heading)

    def _pack(self) -> None:
        for i, widget in enumerate(self._widgets):
            widget.grid(column=0, row=i, sticky="NESW")

    def set_alert(self, alert: Alert) -> None:
        self._variable_name.set(
            f"{alert.patient.firstname} {alert.patient.lastname}"
        )

        if alert.patient.longitude is None or alert.patient.latitude is None:
            self._variable_location_type.set("Address:")
            self._variable_location.set(
                f"{alert.patient.address}\n{alert.patient.postcode}"
            )
        else:
            self._variable_location_type.set("Location:")
            self._variable_location.set(
                f"Lon: {alert.patient.longitude}, Lat: {alert.patient.latitude}"
            )

        if alert.patient.heartrate is not None:
            self._variable_heartrate.set(f"{alert.patient.heartrate} BPM")
        else:
            self._variable_heartrate.set("- BPM")

        self._variable_time_of_fall.set(
            alert.get_datetime_object().strftime("%d/%m/%Y at %I:%M %p")
        )

        self._variable_alergies.set(alert.patient.allergies)
        self._variable_emergency_contacts.set(
            [str(contact) for contact in alert.patient.emergency_contacts]
        )

    def clear(self) -> None:
        self._variable_name.set("")
        self._variable_location_type.set("Address:")
        self._variable_location.set("")
        self._variable_time_of_fall.set("")
        self._variable_alergies.set("")
        self._variable_emergency_contacts.set("")


class Dashboard(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("BS2203 - Operator Dashboard")

        # Overwrite Default Font
        font_ = font.nametofont("TkDefaultFont")
        font_.configure(family="Noto Sans", size=11)
        self.option_add("*Font", font_)

        # Overwrite Default Window Styles
        self.style = ttk.Style(self)
        self.configure(background="#FFFFFF")
        self.style.configure("TLabel", background="#FFFFFF")
        self.style.configure("TLabelframe", background="#FFFFFF")
        self.style.configure("TFrame", background="#FFFFFF")
        self.style.configure("Accent.TFrame", background="#00A6FF")

        # Window Variables
        self._alerts_buffer = []
        self._alerts_queue = queue.Queue()

        # Tk Display Variables
        self._variable_alerts = tk.StringVar()

        # Window Construction
        self._construct()
        self._stylize()
        self._pack()

    def _construct(self) -> None:
        # Menu Bar
        self._menubar = tk.Menu(self, bg="#FFFFFF", activebackground="#00A6FF")

        file_menu = tk.Menu(
            self._menubar, tearoff=0, bg="#FFFFFF", activebackground="#00A6FF"
        )
        edit_menu = tk.Menu(
            self._menubar, tearoff=0, bg="#FFFFFF", activebackground="#00A6FF"
        )

        file_menu.add_command(label="Quit", command=self._quit)
        edit_menu.add_command(
            label="Dismiss Selected Alert", command=self._remove_alert
        )
        edit_menu.add_separator()
        edit_menu.add_command(
            label="Dismiss All Alerts", command=self._clear_alerts
        )

        self._menubar.add_cascade(label="File", menu=file_menu)
        self._menubar.add_cascade(label="Edit", menu=edit_menu)
        self.config(menu=self._menubar)

        # Frames
        self._left_frame = ttk.LabelFrame(self, padding=12)
        self._sidebar = Sidebar(self, padding=12)

        # Widgets
        self._widgets = [
            ttk.Label(self._left_frame, text="Patient Alerts"),
            tk.Listbox(self._left_frame, listvariable=self._variable_alerts),
        ]

    def _stylize(self) -> None:
        self._widgets[0].configure(
            font=font.Font(family="Noto Sans", size=14, weight="bold")
        )
        self._widgets[1].configure(
            width=95, height=30, borderwidth=0, relief="solid"
        )

        self._left_frame.configure(labelwidget=self._widgets[0])

    def _pack(self) -> None:
        self._widgets[1].grid(sticky="NESW")

        self._left_frame.grid(column=0, row=0, sticky="NESW", padx=7, pady=12)
        self._sidebar.grid(column=1, row=0, sticky="NESW", padx=7, pady=12)

    def _synchronise(self) -> None:
        database = DatabaseConnection()
        while True:
            try:
                index = self._widgets[1].curselection()[0]
                self._sidebar.set_alert(self._alerts_buffer[index])
            except IndexError:
                self._sidebar.clear()

            if not self._alerts_queue.empty():
                patient = database.get_patient(
                    self._alerts_queue.get(timeout=1)
                )
                self._alerts_buffer.append(Alert(patient, time.time()))

            self._variable_alerts.set(
                [str(alert) for alert in self._alerts_buffer]
            )

            for alert in self._alerts_buffer:
                alert.patient = database.get_patient(alert.patient.id)

            time.sleep(0.3)

    def _quit(self) -> None:
        if messagebox.askyesno(
            title="Quit", message="Are you sure you want to quit?"
        ):
            self.quit()

    def _remove_alert(self) -> None:
        try:
            index = self._widgets[1].curselection()[0]
            self._alerts_buffer.pop(index)
        except IndexError:
            messagebox.showerror("Dashboard", "No alert selected")

    def _clear_alerts(self) -> None:
        self._alerts_buffer.clear()

    def show(self) -> None:
        threading.Thread(target=self._synchronise, daemon=True).start()
        self.mainloop()

    def add_alert(self, patient_id: int) -> None:
        print(f"Alert for patient: {patient_id}")
        self._alerts_queue.put(patient_id)


if __name__ == "__main__":
    dashboard = Dashboard()

    client = MQTT(FallDetector.analyse, dashboard.add_alert)
    client.begin()

    dashboard.show()
