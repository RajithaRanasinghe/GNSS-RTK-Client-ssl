import sys
from PySide2.QtWidgets import QApplication, QMainWindow, QLabel, QTextEdit, QPushButton, QSizePolicy, QWidget, QGridLayout, QProgressBar
from PySide2.QtCore import Qt
from NtripClientSSL import request_mountpoints, parse_mountpoints_info, connect_mountpoint, get_RTCM3_frm_socket, get_RTCM3_frm_host

class CustomGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        # Create widgets
        self.hostname_label = QLabel("Hostname:", self)
        self.hostname_textbox = QTextEdit('rtk2go.com', self)
        self.port_label = QLabel("Port:", self)
        self.port_textbox = QTextEdit('2101', self)
        self.username_label = QLabel("Username:", self)
        self.username_textbox = QTextEdit('yourmail@gmail.com', self)
        self.password_label = QLabel("Password:", self)
        self.password_textbox = QTextEdit('none', self)
        self.mountpoint_label = QLabel("Mountpoint:", self)
        self.mountpoint_textbox = QTextEdit('', self)
        self.lat_label = QLabel("Latitude:", self)
        self.lat_textbox = QTextEdit('-37.914560', self)
        self.lon_label = QLabel("Longitude:", self)
        self.lon_textbox = QTextEdit('145.127381', self)
        self.output_label = QLabel("Output:", self)
        self.output_textbox = QTextEdit(self)
        self.output_textbox.setReadOnly(True)
        self.get_mnt_button = QPushButton("Get Closest Mountpoint", self)
        self.get_rtcmn3_button = QPushButton("Get RTCM3", self)
        self.clear_button = QPushButton("Clear", self)
        self.progressbar = QProgressBar(self)

        self.hostname_label.setMaximumHeight(30)
        self.hostname_textbox.setMaximumHeight(30)
        self.port_label.setMaximumHeight(30)
        self.port_textbox.setMaximumHeight(30)
        self.username_label.setMaximumHeight(30)
        self.username_textbox.setMaximumHeight(30)
        self.password_label.setMaximumHeight(30)
        self.password_textbox.setMaximumHeight(30)
        self.mountpoint_label.setMaximumHeight(30)
        self.mountpoint_textbox.setMaximumHeight(30)
        self.lat_label.setMaximumHeight(30)
        self.lat_textbox.setMaximumHeight(30)
        self.lon_label.setMaximumHeight(30)
        self.lon_textbox.setMaximumHeight(30)
        self.output_label.setMaximumHeight(30)
        #self.output_textbox.setMaximumHeight(30)
        self.get_mnt_button.setMaximumHeight(30)
        self.clear_button.setMaximumHeight(30)
        self.get_rtcmn3_button.setMaximumHeight(30)
        self.progressbar.setMaximumHeight(30)


        # Create layout
        layout = QGridLayout()
        layout.addWidget(self.hostname_label, 0, 0)
        layout.addWidget(self.hostname_textbox, 0, 1)
        layout.addWidget(self.port_label, 1, 0)
        layout.addWidget(self.port_textbox, 1, 1)
        layout.addWidget(self.username_label, 2, 0)
        layout.addWidget(self.username_textbox, 2, 1)
        layout.addWidget(self.password_label, 3, 0)
        layout.addWidget(self.password_textbox, 3, 1)
        layout.addWidget(self.mountpoint_label, 4, 0)
        layout.addWidget(self.mountpoint_textbox, 4, 1)
        layout.addWidget(self.lat_label, 5, 0)
        layout.addWidget(self.lat_textbox, 5, 1)
        layout.addWidget(self.lon_label, 6, 0)
        layout.addWidget(self.lon_textbox, 6, 1)
        layout.addWidget(self.output_label, 7, 0)
        layout.addWidget(self.output_textbox, 7, 1, 4, 1)
        layout.addWidget(self.get_mnt_button, 12, 0, 1, 2)
        layout.addWidget(self.get_rtcmn3_button, 13, 0, 1, 2)
        layout.addWidget(self.clear_button, 14, 0, 1, 2)
        layout.addWidget(self.progressbar, 15, 0, 1, 2)
        

        # Create central widget and set layout
        central_widget = QWidget()
        central_widget.setLayout(layout)

        # Set central widget
        self.setCentralWidget(central_widget)

        # Resize the window to fit its contents
        self.adjustSize()

        # Connect get closest mountpoint button to function
        self.get_mnt_button.clicked.connect(self.get_mountpoints_function)
        # Connect clear button to method
        self.clear_button.clicked.connect(self.clear_textbox)
        # Connect get rtcm3 data button to method
        self.get_rtcmn3_button.clicked.connect(self.get_RTCM3_data)

    def get_UI_values(self):
        # Get input values from text boxes
        self.hostname = self.hostname_textbox.toPlainText()
        self.port = int(self.port_textbox.toPlainText())
        self.username = self.username_textbox.toPlainText()
        self.password = self.password_textbox.toPlainText()
        self.mountpoint = self.mountpoint_textbox.toPlainText()
        self.lat = float(self.lat_textbox.toPlainText())
        self.lon = float(self.lon_textbox.toPlainText())

    def get_mountpoints_function(self):
        # Start the progress bar
        self.progressbar.setValue(0)
        self.progressbar.setRange(0, 100)

        self.get_UI_values()
        self.progressbar.setValue(10)


        self.message = request_mountpoints(self.hostname, self.port, self.username, self.password)
        self.progressbar.setValue(30)

        self.mountpoints = parse_mountpoints_info(self.message, self.lat, self.lon)
        self.progressbar.setValue(60)

        self.append_text("Closest Mountpoint = {}".format(self.mountpoints[0]['name']))
        self.progressbar.setValue(80)

        for mp in self.mountpoints[:10]:
            self.append_text(f"Name: {mp['name']}, Latitude: {mp['lat']:.4f}, Longitude: {mp['lon']:.4f}, Format: {mp['format']}, Distance: {mp['distance']:.2f} km")

        self.mountpoint_textbox.setText(self.mountpoints[0]['name'])

        # Finish the progress bar
        self.progressbar.setValue(100)

    def get_RTCM3_data(self):
        # Start the progress bar
        self.progressbar.setValue(0)
        self.progressbar.setRange(0, 100)

        self.get_UI_values()
        self.progressbar.setValue(10)

        '''
        sock = connect_mountpoint(self.hostname, self.port, self.username, self.password, self.mountpoint)
        self.progressbar.setValue(30)

        for i in range(5):
            self.append_text(str(get_RTCM3_frm_socket(sock, self.hostname, self.username, self.password, self.mountpoint)))
            self.progressbar.setValue(30 + i*20)
        '''
        self.append_text(str(get_RTCM3_frm_host(self.hostname, self.port, self.username, self.password, self.mountpoint)))
            

        # Finish the progress bar
        self.progressbar.setValue(100)


    def append_text(self, text = ''):
        self.output_textbox.append(text)
    def clear_textbox(self):
        self.output_textbox.clear()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = CustomGUI()
    gui.show()
    sys.exit(app.exec_())