import customtkinter as ctk
import tkintermapview
import tkinter.messagebox as messagebox
import random
import time


# =========================================================
# CONFIG
# =========================================================

APP_TITLE = "Advance Maps - Real-time Satellite"
WINDOW_WIDTH = 1450
WINDOW_HEIGHT = 850

BANGKOK_LAT = 13.7576
BANGKOK_LNG = 100.5651

SATELLITE_URL = (
    "https://mt1.google.com/vt/"
    "lyrs=s&x={x}&y={y}&z={z}"
)

STREET_URL = (
    "https://mt1.google.com/vt/"
    "lyrs=m&x={x}&y={y}&z={z}"
)


# =========================================================
# APPEARANCE
# =========================================================

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


# =========================================================
# MAIN APPLICATION
# =========================================================

class AdvanceMaps(ctk.CTk):

    def __init__(self):

        super().__init__()

        self.title(APP_TITLE)

        self.geometry(
            f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}"
        )

        self.minsize(1100, 700)

        # -------------------------------------------------
        # State
        # -------------------------------------------------

        self.current_map = "satellite"

        self.bus_markers = {}

        self.bus_data = {

            "137": {
                "name": "สาย 137",
                "route": "พระราม 9 - ห้วยขวาง",
                "lat": 13.7590,
                "lng": 100.5651,
                "speed": 32,
                "status": "กำลังเคลื่อนที่",
                "color": "#22c55e"
            },

            "73": {
                "name": "สาย 73",
                "route": "สะพานพุทธ - พระราม 9",
                "lat": 13.7560,
                "lng": 100.5645,
                "speed": 0,
                "status": "จอดรับผู้โดยสาร",
                "color": "#ef4444"
            },

            "168": {
                "name": "สาย 168",
                "route": "อนุสาวรีย์ชัย - มีนบุรี",
                "lat": 13.7615,
                "lng": 100.5680,
                "speed": 25,
                "status": "กำลังเคลื่อนที่",
                "color": "#3b82f6"
            }
        }

        # -------------------------------------------------
        # Layout
        # -------------------------------------------------

        self.create_sidebar()

        self.create_map()

        self.create_bus_markers()

        self.update_clock()

        self.update_bus_positions()


    # =====================================================
    # SIDEBAR
    # =====================================================

    def create_sidebar(self):

        self.sidebar = ctk.CTkFrame(
            self,
            width=330,
            corner_radius=0
        )

        self.sidebar.pack(
            side="left",
            fill="y"
        )

        self.sidebar.pack_propagate(False)


        # -------------------------------------------------
        # Header
        # -------------------------------------------------

        title = ctk.CTkLabel(
            self.sidebar,
            text="🌐 Advance Maps",
            font=ctk.CTkFont(
                size=25,
                weight="bold"
            ),
            text_color="#00d9ff"
        )

        title.pack(
            pady=(25, 3)
        )


        subtitle = ctk.CTkLabel(
            self.sidebar,
            text="REAL-TIME SATELLITE MAP",
            font=ctk.CTkFont(
                size=11,
                weight="bold"
            ),
            text_color="#777777"
        )

        subtitle.pack(
            pady=(0, 20)
        )


        # -------------------------------------------------
        # Status
        # -------------------------------------------------

        status_frame = ctk.CTkFrame(
            self.sidebar,
            fg_color="#1c222b",
            corner_radius=10
        )

        status_frame.pack(
            fill="x",
            padx=15,
            pady=(0, 12)
        )


        ctk.CTkLabel(
            status_frame,
            text="● SYSTEM ONLINE",
            text_color="#22c55e",
            font=ctk.CTkFont(
                size=12,
                weight="bold"
            )
        ).pack(
            anchor="w",
            padx=15,
            pady=(10, 2)
        )


        self.clock_label = ctk.CTkLabel(
            status_frame,
            text="เวลา: --:--:--",
            text_color="#888888",
            font=ctk.CTkFont(size=11)
        )

        self.clock_label.pack(
            anchor="w",
            padx=15,
            pady=(0, 10)
        )


        # -------------------------------------------------
        # Map controls
        # -------------------------------------------------

        map_panel = ctk.CTkFrame(
            self.sidebar,
            fg_color="#1c222b",
            corner_radius=10
        )

        map_panel.pack(
            fill="x",
            padx=15,
            pady=8
        )


        ctk.CTkLabel(
            map_panel,
            text="🗺️ MAP CONTROL",
            font=ctk.CTkFont(
                size=13,
                weight="bold"
            )
        ).pack(
            anchor="w",
            padx=15,
            pady=(12, 8)
        )


        self.satellite_button = ctk.CTkButton(
            map_panel,
            text="🛰️ Satellite",
            height=38,
            command=self.show_satellite
        )

        self.satellite_button.pack(
            fill="x",
            padx=12,
            pady=4
        )


        self.street_button = ctk.CTkButton(
            map_panel,
            text="🗺️ Street Map",
            height=38,
            fg_color="#303640",
            command=self.show_street
        )

        self.street_button.pack(
            fill="x",
            padx=12,
            pady=4
        )


        ctk.CTkButton(
            map_panel,
            text="📍 Bangkok",
            height=38,
            fg_color="#303640",
            command=self.go_bangkok
        ).pack(
            fill="x",
            padx=12,
            pady=4
        )


        ctk.CTkButton(
            map_panel,
            text="🔍 Zoom +",
            height=35,
            fg_color="#303640",
            command=self.zoom_in
        ).pack(
            fill="x",
            padx=12,
            pady=(4, 12)
        )


        # -------------------------------------------------
        # Bus panel
        # -------------------------------------------------

        bus_panel = ctk.CTkFrame(
            self.sidebar,
            fg_color="#1c222b",
            corner_radius=10
        )

        bus_panel.pack(
            fill="both",
            expand=True,
            padx=15,
            pady=8
        )


        ctk.CTkLabel(
            bus_panel,
            text="🚌 LIVE BUS TRACKING",
            font=ctk.CTkFont(
                size=13,
                weight="bold"
            )
        ).pack(
            anchor="w",
            padx=15,
            pady=(12, 8)
        )


        self.bus_labels = {}


        for bus_id in self.bus_data:

            data = self.bus_data[bus_id]

            card = ctk.CTkFrame(
                bus_panel,
                fg_color="#252b35",
                corner_radius=8
            )

            card.pack(
                fill="x",
                padx=10,
                pady=5
            )


            name = ctk.CTkLabel(
                card,
                text=f"🚌 {data['name']}",
                text_color=data["color"],
                font=ctk.CTkFont(
                    size=13,
                    weight="bold"
                )
            )

            name.pack(
                anchor="w",
                padx=10,
                pady=(8, 2)
            )


            info = ctk.CTkLabel(
                card,
                text="กำลังโหลด...",
                text_color="#aaaaaa",
                justify="left",
                font=ctk.CTkFont(size=11)
            )

            info.pack(
                anchor="w",
                padx=10,
                pady=(0, 8)
            )


            self.bus_labels[bus_id] = info


        # -------------------------------------------------
        # Footer
        # -------------------------------------------------

        ctk.CTkLabel(
            self.sidebar,
            text="Python 3.14  •  TkinterMapView",
            text_color="#555555",
            font=ctk.CTkFont(size=10)
        ).pack(
            pady=10
        )


    # =====================================================
    # MAP
    # =====================================================

    def create_map(self):

        self.map_frame = ctk.CTkFrame(
            self,
            corner_radius=0
        )

        self.map_frame.pack(
            side="right",
            fill="both",
            expand=True
        )


        # -------------------------------------------------
        # Map title
        # -------------------------------------------------

        self.map_title = ctk.CTkFrame(
            self.map_frame,
            fg_color="#161a20",
            corner_radius=10
        )

        self.map_title.place(
            x=20,
            y=20
        )


        ctk.CTkLabel(
            self.map_title,
            text="REAL-TIME MAP",
            font=ctk.CTkFont(
                size=15,
                weight="bold"
            ),
            text_color="#00d9ff"
        ).pack(
            padx=15,
            pady=(8, 0)
        )


        ctk.CTkLabel(
            self.map_title,
            text="Bangkok, Thailand",
            font=ctk.CTkFont(size=11),
            text_color="#888888"
        ).pack(
            padx=15,
            pady=(0, 8)
        )


        # -------------------------------------------------
        # Map widget
        # -------------------------------------------------

        self.map_widget = tkintermapview.TkinterMapView(
            self.map_frame,
            corner_radius=0
        )

        self.map_widget.pack(
            fill="both",
            expand=True
        )


        # Satellite
        self.map_widget.set_tile_server(
            SATELLITE_URL,
            max_zoom=20
        )


        self.map_widget.set_position(
            BANGKOK_LAT,
            BANGKOK_LNG
        )


        self.map_widget.set_zoom(15)


        # -------------------------------------------------
        # Bangkok marker
        # -------------------------------------------------

        self.bangkok_marker = (
            self.map_widget.set_marker(
                BANGKOK_LAT,
                BANGKOK_LNG,
                text="📍 กรุงเทพมหานคร"
            )
        )


    # =====================================================
    # BUS MARKERS
    # =====================================================

    def create_bus_markers(self):

        for bus_id, data in self.bus_data.items():

            marker = self.map_widget.set_marker(

                data["lat"],

                data["lng"],

                text=(
                    f"🚌 {data['name']}\n"
                    f"{data['status']}\n"
                    f"{data['speed']} km/h"
                )

            )

            self.bus_markers[bus_id] = marker


    # =====================================================
    # SATELLITE
    # =====================================================

    def show_satellite(self):

        self.map_widget.set_tile_server(
            SATELLITE_URL,
            max_zoom=20
        )

        self.current_map = "satellite"

        self.satellite_button.configure(
            fg_color="#00a8cc"
        )

        self.street_button.configure(
            fg_color="#303640"
        )


    # =====================================================
    # STREET
    # =====================================================

    def show_street(self):

        self.map_widget.set_tile_server(
            STREET_URL,
            max_zoom=20
        )

        self.current_map = "street"

        self.street_button.configure(
            fg_color="#00a8cc"
        )

        self.satellite_button.configure(
            fg_color="#303640"
        )


    # =====================================================
    # BANGKOK
    # =====================================================

    def go_bangkok(self):

        self.map_widget.set_position(
            BANGKOK_LAT,
            BANGKOK_LNG
        )

        self.map_widget.set_zoom(15)


    # =====================================================
    # ZOOM
    # =====================================================

    def zoom_in(self):

        current_zoom = self.map_widget.zoom

        self.map_widget.set_zoom(
            min(current_zoom + 1, 20)
        )


    # =====================================================
    # UPDATE CLOCK
    # =====================================================

    def update_clock(self):

        current_time = time.strftime(
            "%H:%M:%S"
        )

        self.clock_label.configure(
            text=f"เวลา: {current_time}"
        )

        self.after(
            1000,
            self.update_clock
        )


    # =====================================================
    # UPDATE GPS
    # =====================================================

    def update_bus_positions(self):

        for bus_id, data in self.bus_data.items():

            # ---------------------------------------------
            # จำลองรถที่กำลังวิ่ง
            # ---------------------------------------------

            if data["speed"] > 0:

                data["lat"] += random.uniform(
                    0.000005,
                    0.000035
                )

                data["lng"] += random.uniform(
                    0.000003,
                    0.000020
                )


                # ป้องกันรถวิ่งไกลเกินพื้นที่ Demo

                if data["lat"] > 13.770:

                    data["lat"] = 13.755


                if data["lng"] > 100.580:

                    data["lng"] = 100.560


            # ---------------------------------------------
            # ย้าย Marker
            # ---------------------------------------------

            marker = self.bus_markers.get(
                bus_id
            )

            if marker:

                marker.set_position(
                    data["lat"],
                    data["lng"]
                )

                marker.set_text(
                    f"🚌 {data['name']}\n"
                    f"{data['status']}\n"
                    f"{data['speed']} km/h"
                )


            # ---------------------------------------------
            # Update Sidebar
            # ---------------------------------------------

            label = self.bus_labels.get(
                bus_id
            )

            if label:

                label.configure(
                    text=(
                        f"สถานะ: {data['status']}\n"
                        f"ความเร็ว: {data['speed']} กม./ชม.\n"
                        f"GPS: "
                        f"{data['lat']:.6f}, "
                        f"{data['lng']:.6f}"
                    )
                )


        # อัปเดตทุก 3 วินาที

        self.after(
            3000,
            self.update_bus_positions
        )


# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":

    app = AdvanceMaps()

    app.mainloop()