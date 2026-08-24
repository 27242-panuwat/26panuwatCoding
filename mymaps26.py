import sys
import json
import urllib.parse
import urllib.request

from PySide6.QtCore import QUrl, QObject, Slot
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLineEdit,
    QLabel,
    QListWidget,
    QMessageBox
)
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebChannel import QWebChannel


HTML = r"""
<!DOCTYPE html>
<html>
<head>

<meta charset="UTF-8">

<title>Advance Maps</title>

<link
rel="stylesheet"
href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css">

<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>

<style>

html, body {
    margin: 0;
    width: 100%;
    height: 100%;
    overflow: hidden;
}

#map {
    width: 100%;
    height: 100%;
}

.bus-icon {
    width: 34px;
    height: 34px;
    border-radius: 50%;
    background: #1976d2;
    border: 3px solid white;
    box-shadow: 0 2px 8px black;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 18px;
}

</style>

</head>

<body>

<div id="map"></div>

<script>

let map;

let searchMarkers = [];

let busMarkers = [];


// ===============================
// สร้างแผนที่
// ===============================

map = L.map("map", {
    worldCopyJump: true
}).setView([13.7563, 100.5018], 12);


// ===============================
// ภาพดาวเทียม
// ===============================

const satellite = L.tileLayer(
    "https://server.arcgisonline.com/ArcGIS/rest/services/" +
    "World_Imagery/MapServer/tile/{z}/{y}/{x}",
    {
        maxZoom: 19,
        attribution: "Esri"
    }
);

satellite.addTo(map);


// ===============================
// แผนที่ถนน
// ===============================

const street = L.tileLayer(
    "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
    {
        maxZoom: 19,
        attribution: "OpenStreetMap"
    }
);


// ===============================
// Layers
// ===============================

L.control.layers({
    "🛰 Satellite": satellite,
    "🗺 Street": street
}).addTo(map);


// ===============================
// คลิกแผนที่
// ===============================

map.on("click", function(e) {

    if (window.bridge) {

        window.bridge.mapClicked(
            e.latlng.lat,
            e.latlng.lng
        );

    }

});


// ===============================
// เพิ่มจุดค้นหา
// ===============================

function addSearchPoint(lat, lon, name) {

    const marker = L.marker([
        lat,
        lon
    ])
    .addTo(map)
    .bindPopup(
        "<b>" +
        escapeHtml(name) +
        "</b><br>" +
        lat.toFixed(6) +
        ", " +
        lon.toFixed(6)
    );

    searchMarkers.push(marker);

    map.setView([
        lat,
        lon
    ], 16);

    marker.openPopup();
}


// ===============================
// ลบจุดค้นหา
// ===============================

function clearSearchPoints() {

    searchMarkers.forEach(
        function(marker) {
            map.removeLayer(marker);
        }
    );

    searchMarkers = [];
}


// ===============================
// เพิ่มป้ายรถ
// ===============================

function addBusStop(lat, lon, name) {

    const icon = L.divIcon({

        className: "",

        html:
            '<div class="bus-icon">🚌</div>',

        iconSize: [
            40,
            40
        ],

        iconAnchor: [
            20,
            20
        ]

    });


    const marker = L.marker(
        [
            lat,
            lon
        ],
        {
            icon: icon
        }
    )
    .addTo(map);


    marker.bindPopup(
        "<b>🚌 " +
        escapeHtml(name) +
        "</b><br><br>" +
        "Latitude: " +
        lat.toFixed(6) +
        "<br>" +
        "Longitude: " +
        lon.toFixed(6)
    );


    busMarkers.push(marker);
}


// ===============================
// แสดงป้ายรถ
// ===============================

function showBusStops(stops) {

    clearBusStops();


    for (
        let i = 0;
        i < stops.length;
        i++
    ) {

        addBusStop(
            stops[i].lat,
            stops[i].lon,
            stops[i].name
        );

    }


    if (stops.length > 0) {

        const group =
            L.featureGroup(busMarkers);

        map.fitBounds(
            group.getBounds(),
            {
                padding: [
                    40,
                    40
                ]
            }
        );

    }

}


// ===============================
// ลบป้ายรถ
// ===============================

function clearBusStops() {

    busMarkers.forEach(
        function(marker) {

            map.removeLayer(marker);

        }
    );

    busMarkers = [];

}


// ===============================
// HTML protection
// ===============================

function escapeHtml(text) {

    const div =
        document.createElement("div");

    div.textContent = text;

    return div.innerHTML;
}

</script>

</body>
</html>
"""


class Bridge(QObject):

    def __init__(self, window):
        super().__init__()
        self.window = window


    @Slot(float, float)
    def mapClicked(
        self,
        lat,
        lon
    ):

        self.window.latitude.setText(
            f"{lat:.6f}"
        )

        self.window.longitude.setText(
            f"{lon:.6f}"
        )


class AdvanceMaps(QMainWindow):

    def __init__(self):

        super().__init__()

        self.setWindowTitle(
            "Advance Maps"
        )

        self.resize(
            1400,
            850
        )


        # ===========================
        # Main widget
        # ===========================

        central = QWidget()

        self.setCentralWidget(
            central
        )

        main_layout = QHBoxLayout(
            central
        )


        # ===========================
        # Sidebar
        # ===========================

        sidebar = QWidget()

        sidebar.setFixedWidth(
            330
        )

        sidebar_layout = QVBoxLayout(
            sidebar
        )


        title = QLabel(
            "ADVANCE MAPS"
        )

        title.setStyleSheet("""
        QLabel {
            font-size: 25px;
            font-weight: bold;
            color: #00bcd4;
            padding: 10px;
        }
        """)

        sidebar_layout.addWidget(
            title
        )


        # ===========================
        # Search
        # ===========================

        self.search = QLineEdit()

        self.search.setPlaceholderText(
            "ค้นหาสถานที่ทั่วโลก..."
        )

        sidebar_layout.addWidget(
            self.search
        )


        search_button = QPushButton(
            "🔎 ค้นหาสถานที่"
        )

        search_button.clicked.connect(
            self.search_place
        )

        sidebar_layout.addWidget(
            search_button
        )


        # ===========================
        # Coordinates
        # ===========================

        sidebar_layout.addWidget(
            QLabel(
                "ตำแหน่งที่เลือก"
            )
        )


        self.latitude = QLineEdit()

        self.latitude.setPlaceholderText(
            "Latitude"
        )

        self.latitude.setReadOnly(
            True
        )

        sidebar_layout.addWidget(
            self.latitude
        )


        self.longitude = QLineEdit()

        self.longitude.setPlaceholderText(
            "Longitude"
        )

        self.longitude.setReadOnly(
            True
        )

        sidebar_layout.addWidget(
            self.longitude
        )


        # ===========================
        # Bus search
        # ===========================

        bus_button = QPushButton(
            "🚌 ค้นหาป้ายรถเมล์"
        )

        bus_button.setMinimumHeight(
            45
        )

        bus_button.clicked.connect(
            self.search_bus_stops
        )

        sidebar_layout.addWidget(
            bus_button
        )


        # ===========================
        # Clear search
        # ===========================

        clear_button = QPushButton(
            "❌ ลบจุดค้นหา"
        )

        clear_button.clicked.connect(
            self.clear_search
        )

        sidebar_layout.addWidget(
            clear_button
        )


        # ===========================
        # Clear buses
        # ===========================

        clear_bus_button = QPushButton(
            "🚌 ลบป้ายรถทั้งหมด"
        )

        clear_bus_button.clicked.connect(
            self.clear_bus
        )

        sidebar_layout.addWidget(
            clear_bus_button
        )


        # ===========================
        # Results
        # ===========================

        sidebar_layout.addWidget(
            QLabel(
                "ผลการค้นหา"
            )
        )


        self.results = QListWidget()

        sidebar_layout.addWidget(
            self.results
        )


        # ===========================
        # Map
        # ===========================

        self.map = QWebEngineView()


        self.channel = QWebChannel()

        self.bridge = Bridge(
            self
        )

        self.channel.registerObject(
            "bridge",
            self.bridge
        )

        self.map.page().setWebChannel(
            self.channel
        )


        self.map.setHtml(
            HTML,
            QUrl(
                "https://localhost/"
            )
        )


        # ===========================
        # Layout
        # ===========================

        main_layout.addWidget(
            sidebar
        )

        main_layout.addWidget(
            self.map,
            1
        )


    # =================================================
    # SEARCH PLACE
    # =================================================

    def search_place(self):

        text = (
            self.search.text()
            .strip()
        )


        if not text:

            QMessageBox.warning(
                self,
                "แจ้งเตือน",
                "กรุณาพิมพ์สถานที่"
            )

            return


        try:

            url = (
                "https://nominatim.openstreetmap.org/search"
                "?q="
                +
                urllib.parse.quote(text)
                +
                "&format=json"
                "&limit=5"
            )


            request = urllib.request.Request(
                url,
                headers={
                    "User-Agent":
                    "AdvanceMaps/1.0"
                }
            )


            with urllib.request.urlopen(
                request,
                timeout=15
            ) as response:

                data = json.loads(
                    response.read().decode(
                        "utf-8"
                    )
                )


            self.results.clear()


            if not data:

                QMessageBox.information(
                    self,
                    "ไม่พบ",
                    "ไม่พบสถานที่"
                )

                return


            for item in data:

                name = item.get(
                    "display_name",
                    "Unknown"
                )

                lat = float(
                    item["lat"]
                )

                lon = float(
                    item["lon"]
                )


                self.results.addItem(
                    name
                )


                js = (
                    "addSearchPoint("
                    +
                    str(lat)
                    +
                    ","
                    +
                    str(lon)
                    +
                    ","
                    +
                    json.dumps(
                        name,
                        ensure_ascii=False
                    )
                    +
                    ");"
                )


                self.map.page().runJavaScript(
                    js
                )


        except Exception as e:

            QMessageBox.critical(
                self,
                "ค้นหาไม่ได้",
                str(e)
            )


    # =================================================
    # SEARCH BUS STOPS
    # =================================================

    def search_bus_stops(self):

        lat_text = (
            self.latitude.text()
            .strip()
        )

        lon_text = (
            self.longitude.text()
            .strip()
        )


        if not lat_text or not lon_text:

            QMessageBox.warning(
                self,
                "ยังไม่ได้เลือกตำแหน่ง",
                "ให้คลิกบนแผนที่ก่อน\n\n"
                "จากนั้นกดปุ่ม 🚌 ค้นหาป้ายรถเมล์"
            )

            return


        try:

            lat = float(
                lat_text
            )

            lon = float(
                lon_text
            )


            # =====================================
            # Overpass query
            # =====================================

            query = f"""
[out:json][timeout:25];

(
    node
    ["highway"="bus_stop"]
    (around:10000,{lat},{lon});

    node
    ["public_transport"="platform"]
    (around:10000,{lat},{lon});

    node
    ["public_transport"="stop_position"]
    (around:10000,{lat},{lon});

    way
    ["highway"="bus_stop"]
    (around:10000,{lat},{lon});
);

out center;
"""


            encoded_query = (
                urllib.parse.quote(
                    query
                )
            )


            # =====================================
            # ลองหลาย Server
            # =====================================

            servers = [

                "https://overpass-api.de/api/interpreter",

                "https://overpass.kumi.systems/api/interpreter",

                "https://overpass.private.coffee/api/interpreter"

            ]


            data = None

            last_error = None


            for server in servers:

                try:

                    url = (
                        server
                        +
                        "?data="
                        +
                        encoded_query
                    )


                    request = urllib.request.Request(
                        url,
                        headers={
                            "User-Agent":
                            "AdvanceMaps/2.0"
                        }
                    )


                    with urllib.request.urlopen(
                        request,
                        timeout=30
                    ) as response:

                        raw = response.read()

                        data = json.loads(
                            raw.decode(
                                "utf-8"
                            )
                        )


                    if data is not None:

                        break


                except Exception as e:

                    last_error = e

                    continue


            if data is None:

                QMessageBox.critical(
                    self,
                    "เซิร์ฟเวอร์ค้นหาป้ายรถมีปัญหา",
                    "ลองใหม่อีกครั้ง\n\n"
                    +
                    str(last_error)
                )

                return


            # =====================================
            # อ่านข้อมูล
            # =====================================

            stops = []

            used = set()


            for element in data.get(
                "elements",
                []
            ):

                tags = element.get(
                    "tags",
                    {}
                )


                # -----------------------------
                # Node
                # -----------------------------

                if (
                    "lat" in element
                    and
                    "lon" in element
                ):

                    stop_lat = float(
                        element["lat"]
                    )

                    stop_lon = float(
                        element["lon"]
                    )


                # -----------------------------
                # Way
                # -----------------------------

                elif "center" in element:

                    stop_lat = float(
                        element["center"]["lat"]
                    )

                    stop_lon = float(
                        element["center"]["lon"]
                    )

                else:

                    continue


                # -----------------------------
                # Name
                # -----------------------------

                name = (
                    tags.get("name")
                    or
                    tags.get("name:th")
                    or
                    tags.get("name:en")
                    or
                    "ป้ายรถเมล์"
                )


                # -----------------------------
                # Duplicate protection
                # -----------------------------

                key = (
                    round(stop_lat, 6),
                    round(stop_lon, 6)
                )


                if key in used:

                    continue


                used.add(key)


                stops.append({

                    "lat":
                        stop_lat,

                    "lon":
                        stop_lon,

                    "name":
                        name

                })


            # =====================================
            # ส่งเข้าแผนที่
            # =====================================

            javascript = (
                "showBusStops("
                +
                json.dumps(
                    stops,
                    ensure_ascii=False
                )
                +
                ");"
            )


            self.map.page().runJavaScript(
                javascript
            )


            # =====================================
            # Result
            # =====================================

            self.results.clear()


            for stop in stops:

                self.results.addItem(
                    "🚌 "
                    +
                    stop["name"]
                )


            if len(stops) == 0:

                QMessageBox.information(
                    self,
                    "ไม่พบป้ายรถ",
                    "บริเวณนี้ไม่มีข้อมูลป้ายรถใน OpenStreetMap\n\n"
                    "ลองเลื่อนไปยังบริเวณที่มีระบบขนส่งสาธารณะ"
                )

            else:

                QMessageBox.information(
                    self,
                    "ค้นหาสำเร็จ",
                    f"พบป้ายรถ {len(stops)} จุด"
                )


        except Exception as e:

            QMessageBox.critical(
                self,
                "เกิดข้อผิดพลาด",
                str(e)
            )


    # =================================================
    # CLEAR SEARCH
    # =================================================

    def clear_search(self):

        self.map.page().runJavaScript(
            "clearSearchPoints();"
        )

        self.results.clear()


    # =================================================
    # CLEAR BUS
    # =================================================

    def clear_bus(self):

        self.map.page().runJavaScript(
            "clearBusStops();"
        )

        self.results.clear()


# =====================================================
# START PROGRAM
# =====================================================

if __name__ == "__main__":

    app = QApplication(
        sys.argv
    )

    window = AdvanceMaps()

    window.show()

    sys.exit(
        app.exec()
    )