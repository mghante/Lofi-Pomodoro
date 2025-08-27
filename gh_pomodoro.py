import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QPushButton, QSpinBox, QDoubleSpinBox, QLabel, QHBoxLayout, QAction, QMessageBox, QWidgetAction, QMenuBar, QDialog

)
from PyQt5.QtCore import Qt, QTimer, QUrl, QTime, QSize
from PyQt5.QtGui import QPainter, QPen, QFont, QColor, QIcon, QPixmap, QPalette, QBrush
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent, QSoundEffect

# for custom font, need to download a ttf file
from PyQt5.QtGui import QFont, QFontDatabase

#must install python and pip, then run "install pyqt5"
#install w icon to desktop:  pyinstaller --onefile --windowed --icon= "pathway to icon" pomodoro.py

class CircularCountdown(QWidget):
    def __init__(self, total_seconds=1500, finished_callback=None):  # default 25 min
        super().__init__()
        self.total_seconds = total_seconds
        self.remaining_seconds = total_seconds
        self.finished_callback = finished_callback
        self.arc_color = QColor(233, 174, 130, 220)  # R, G, B, Alpha arc color of clock

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_timer)
        self.setMinimumSize(300, 300)  # size of clock circle

    def start(self, seconds=None):
        if seconds:
            self.total_seconds = seconds
            self.remaining_seconds = seconds
        self.timer.start(1000)    #times out every 1000 milliseconds or 1 second
        self.update()

    def pause(self):
        self.timer.stop()

    def reset(self, seconds=None):
        if seconds:
            self.total_seconds = seconds            #if specified, will reset to new "seconds"
            self.remaining_seconds = seconds
        else:
            self.remaining_seconds = self.total_seconds        #if not specified, will reset to last-set total seconds
        self.timer.stop()
        self.update()       #updates with new information

    def update_timer(self):
        if self.remaining_seconds > 0:
            self.remaining_seconds -= 1  #when timeout is called (set up to be run every second), decreases remaining seconds by 1
        else:
            self.timer.stop()
            if self.finished_callback:
                self.finished_callback()   #in Main Window this calls session_finished which switches from work <-> break
        self.update()  #reflect new time remaining

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        rect = self.rect().adjusted(10, 10, -10, -90)  #padding of arc and timer from window sides

        # background circle
        pen_bg = QPen(QColor(222, 165, 122, 110), 20)  #color of second arc (when time has elapsed)
        painter.setPen(pen_bg)
        painter.drawArc(rect, 0, 360 * 16)

        # progress arc
        if self.total_seconds > 0:
            angle_span = int(360 * (self.remaining_seconds / self.total_seconds))
        else:
            angle_span = 0
        pen_fg = QPen(self.arc_color, 15)
        painter.setPen(pen_fg)
        painter.drawArc(rect, 90 * 16, -angle_span * 16)

        # countdown text
        painter.setPen(QColor(249, 186, 94))  #color of timer font
        font_id = QFontDatabase.addApplicationFont("DS-DIGIT.TTF")  #replace with file path
        font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
        painter.setFont(QFont(font_family, 40))  # size of timer font
        minutes = self.remaining_seconds // 60
        seconds = self.remaining_seconds % 60
        text = f"{minutes:02}:{seconds:02}"
        text_rect = rect.adjusted(0, 0, 0, 0)  # move text inside circle
        painter.drawText(text_rect, Qt.AlignCenter, text)

#based on a tutorial by Brocode on YouTube
class DigitalClock(QWidget):
    def __init__(self):
        super().__init__()
        self.time_label = QLabel(self)  # display time
        self.timer = QTimer(self)  # add timer and time to clock

        vbox = QVBoxLayout()  # arranges widgets vertically
        vbox.addWidget(self.time_label)
        self.setLayout(vbox)

        self.time_label.setAlignment(Qt.AlignCenter)  # centers the time
        self.time_label.setStyleSheet(
            "color: rgba(235, 152, 162, 250);")     #Color of clock font

        # custom font
        font_id = QFontDatabase.addApplicationFont("DS-DIGIT.TTF")   #replace with file path
        font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
        my_font = QFont(font_family, 35)  # second param is font size
        self.time_label.setFont(my_font)

        self.timer.timeout.connect(self.update_time)  # trigger timeout every second
        self.timer.start(1000)  # 1000 miliseconds

        self.update_time()  # used to display time when program started

    def update_time(self):
        current_time = QTime.currentTime().toString(
            "hh:mm AP")  # design layout of time; AP turns from 24hr to 12hr with AM/PM label
        # hh mm ss are format specifiers
        self.time_label.setText(current_time)

# used for when work and break cycles finish
class CustomMessage(QDialog):
    def __init__(self, title, message, parent=None, icon=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)  # block input until closed
        self.setGeometry(2473, 197, 400, 230)   #position of work/break popup on screen
        self.setFixedSize(400, 230)             #locks dimensions of popup window


        #setting background of popup message (custom jpg to match background)
        og_pixmap = QPixmap("trains_popup_msg.jpg") #replace with file path
        custom_bkgrnd = QLabel(self)
        custom_bkgrnd.setPixmap(og_pixmap)
        custom_bkgrnd.setScaledContents(True)
        custom_bkgrnd.setGeometry(0, 0, self.width(), self.height())   #scales to fit QDialog dimensions defined above (400 x 230)

        if icon:
            self.setWindowIcon(QIcon(icon))         #sets the icon; can use the same as Main Window or None

        #Layout
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)

        # message label
        label = QLabel(message)
        label.setStyleSheet(
            "font-family: Magneto; font-size: 40px; color: rgba(250, 173, 90, 210); background: transparent;")

        # ok/close button
        ok_button = QPushButton("OK")
        ok_button.setStyleSheet(
            "font-family: Magneto; font-size: 20px; font-weight: bold; padding: 12px 12px; border-radius: 12px; background-color: rgba(255, 255, 255, 180); color: black;")
        ok_button.clicked.connect(self.accept)  #closes the QDialog instance

        #set center-aligned layout of label -> space -> ok button
        layout.addWidget(label, alignment=Qt.AlignCenter)
        layout.addSpacing(10)   #adds spacing between label and button)
        layout.addWidget(ok_button, alignment=Qt.AlignCenter)

        self.setLayout(layout)

#used for setting a custom timer menu (default, spin boxes, ok and cancel buttons)
class CustomTimer(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(" ")
        self.setModal(True)  # block input until closed
        self.setGeometry(2473, 197, 400, 270)    #sets position on screen
        self.setFixedSize(400, 270)             #locks dimensions to be 400x270

        #background of set custom timer popup (custom jpg to match background)
        og_pixmap = QPixmap("trains_popup_ct.jpg")  #replace with file path
        custom_bkgrnd = QLabel(self)
        custom_bkgrnd.setPixmap(og_pixmap)
        custom_bkgrnd.setScaledContents(True)
        custom_bkgrnd.setGeometry(0, 0, self.width(), self.height())   #scales background to Dialog defined size (400x270)

        # Labels for time inputs
        work_label = QLabel("Work:")
        break_label = QLabel("Break:")
        work_label.setStyleSheet(
            "border-radius: 10px; padding: 6px 12px; color: black; background-color: rgba(255, 255, 255, 180); font-family: Georgia; font-size: 20px; font-weight: bold")
        break_label.setStyleSheet(
            "border-radius: 10px; padding: 6px 12px; color: black; background-color: rgba(255, 255, 255, 180); font-family: Georgia; font-size: 20px; font-weight: bold")

        # Spin boxes for custom time
        self.work_spin = QSpinBox()  # for easy testing, switch to QDoubleSpinBox (can input seconds)
        self.work_spin.setRange(0, 180)
        self.work_spin.setSuffix(" min")
        self.work_spin.setSpecialValueText(" ")  # sets min val of 0 to " "
        self.work_spin.setValue(0)

        self.break_spin = QSpinBox()       # for easy testing, switch to QDoubleSpinBox (can input seconds)
        self.break_spin.setRange(0, 60)
        self.break_spin.setSuffix(" min")
        self.break_spin.setSpecialValueText(" ")  # sets min val of 0 to " "
        self.break_spin.setValue(0)

        #buttons
        defaultpom_button = QPushButton("Default (25 : 5)")
        defaultpom_button.clicked.connect(lambda: self.work_spin.setValue(25))  #Lambda needed so function call does not run until btn clicked
        defaultpom_button.clicked.connect(lambda: self.break_spin.setValue(5))
        defaultpom_button.clicked.connect(self.accept)      #should also accept to uphold condition in set_custom_time method in MainWindow

        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.accept)  # closes dialog with success
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)  # closes dialog without changes

        #layout of inputs and buttons
        layout = QVBoxLayout()
        # Work input
        work_input_layout = QHBoxLayout()
        work_input_layout.addWidget(work_label)
        work_input_layout.addWidget(self.work_spin)
        # Break input
        break_input_layout = QHBoxLayout()
        break_input_layout.addWidget(break_label)
        break_input_layout.addWidget(self.break_spin)
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)

        layout.addWidget(defaultpom_button)
        layout.addLayout(work_input_layout)
        layout.addLayout(break_input_layout)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def get_work_value(self):
        return self.work_spin.value()   #returns value from work spin box or overriden value by default pomodoro
    def get_break_value(self):
        return self.break_spin.value()  #returns value from work spin box or overriden value by default pomodoro


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # styling for buttons (set custom timer, play, pause, restart)
        self.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 180);  /* semi-transparent white */
                color: black;
                font-family: "Georgia";
                font-weight: bold;
                border-radius: 10px;
                padding: 6px 12px;
                font-size: 20px;
                }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 220);  /* less transparent on hover */
                }
            QPushButton:pressed {
                background-color: rgba(235, 152, 162, 200);   /*color when clicked */
                color: white;
                }
            """)

        self.setWindowIcon(QIcon("clock_ring.png"))  #replace with file path
        self.setWindowTitle("Pomodoro")
        self.setGeometry(2473, 140, 400, 540)       #set to top right of screen with min size needed
        self.setFixedSize(400, 540)                 #locks size (cannot use expand window button)

        # set background image
        og_pixmap = QPixmap("trains.jpg")   #replace with file path
        custom_bkgrnd = QLabel(self)
        custom_bkgrnd.setPixmap(og_pixmap)
        custom_bkgrnd.setScaledContents(True)
        custom_bkgrnd.setGeometry(0, 0, self.width(), self.height())  #background image fits defined Window dimensions (400 x 540)

        # State: "work" or "break"
        self.mode = "work"
        self.work_minutes = 25
        self.break_minutes = 5

        # alarm sound for when mode switches
        self.alarm = QSoundEffect()  # use this instead of Player so that music is not interrupted
        self.alarm.setSource(QUrl.fromLocalFile("alarm_sound.wav")) #replace with file path
        self.alarm.setVolume(0.5)

        # Countdown circle
        self.countdown = CircularCountdown(
            self.work_minutes * 60,
            finished_callback=self.session_finished

        )

        # Clock
        self.clock = DigitalClock()

        # Long Buttons
        setcustomtime_button = QPushButton("Set Custom Timer")
        setcustomtime_button.clicked.connect(self.set_custom_time)

        # Left column: Start Pomodoro
        start_button = QPushButton()
        start_button.setIcon(QIcon("play.png"))  #replace with file path
        start_button.setIconSize(QSize(32, 32))
        start_button.clicked.connect(lambda: self.countdown.start())
        left_layout = QVBoxLayout()
        left_layout.addWidget(start_button)

        # Middle Column: pause Pomodoro
        pause_button = QPushButton()
        pause_button.setIcon(QIcon("pause.png"))  #replace with file path
        pause_button.setIconSize(QSize(32, 32))
        pause_button.clicked.connect(self.countdown.pause)
        middle_layout = QVBoxLayout()
        middle_layout.addWidget(pause_button)

        # Right Column: reset Pomodoro
        reset_button = QPushButton()
        reset_button.setIcon(QIcon("restart.png"))  #replace with file path
        reset_button.setIconSize(QSize(32, 32))
        reset_button.clicked.connect(self.reset_timer)
        right_layout = QVBoxLayout()
        right_layout.addWidget(reset_button)

        # Combine left, middle, and right layouts
        button_layout = QHBoxLayout()
        button_layout.addLayout(left_layout)
        button_layout.addLayout(middle_layout)
        button_layout.addLayout(right_layout)

        # Main layout
        layout = QVBoxLayout()

        layout.addWidget(self.countdown)  # pomodoro countdown obj
        layout.addWidget(setcustomtime_button)  # button to set custom time
        layout.addLayout(button_layout)  # start, pause, reset pomodoro buttons
        layout.addWidget(self.clock)  # clock

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)  #in QMainWindow can't set a layout directly. Have to add a widget to the central widget area

        # Menu bar → Always on Top -> self.mode -> lofi
        menubar = self.menuBar()

        #styling
        self.menuBar().setStyleSheet("""
            QMenuBar {
                background-color: rgba(255, 255, 255, 100);
                font-family: Magneto;
                font-size: 27px;
                font-weight: bold;
            }
            QMenu {
                background: white;        /* dropdown menus stay white */
                color: black;             /* text color */
                font-family: Georgia;
                font-size: 20px;

            }
            QMenu::item:selected {
                background: rgba(235, 152, 162, 100);      /* highlight color */
                color: white;             /* text when hovered */
            }
        """)

        #View Menu (top left)
        view_menu = menubar.addMenu(QIcon("view_window.png"), "View")    #replace with file path
        #Drop down control for app location
        self.always_on_top_action = QAction("Always on Top", self, checkable=True)
        self.always_on_top_action.triggered.connect(self.toggle_always_on_top)
        view_menu.addAction(self.always_on_top_action)

        #Mode Label (middle)
        self.mode_menu = menubar.addMenu(f"   ~~~~~{self.mode}~~~~~  ")

        #Lofi Player (top right)
        self.player = QMediaPlayer()
        lofi_menu = menubar.addMenu(QIcon("music.png"), "Lofi")  #replace with file path

        #Drop down controls for Lofi
        self.play_lofi_btn = QAction("Play Lofi", self)
        self.play_lofi_btn.triggered.connect(self.play_lofi)
        lofi_menu.addAction(self.play_lofi_btn)

        self.pause_lofi_btn = QAction("Pause Lofi", self)
        self.pause_lofi_btn.triggered.connect(self.player.pause)
        lofi_menu.addAction(self.pause_lofi_btn)

        self.resume_lofi_btn = QAction("Resume Lofi", self)
        self.resume_lofi_btn.triggered.connect(self.player.play)
        lofi_menu.addAction(self.resume_lofi_btn)

        self.restart_lofi_btn = QAction("Restart Lofi", self)
        self.restart_lofi_btn.triggered.connect(self.player.stop)
        self.restart_lofi_btn.triggered.connect(self.player.play)  # should restart lofi from start
        lofi_menu.addAction(self.restart_lofi_btn)

    #Called by set custom timer button on Main Central Widget -> if QSpin boxes + ok OR default button on Dialog pressed, dialog.exec_() == QDialog.Accepted is true
    def set_custom_time(self):
        dialog = CustomTimer(self)
        if dialog.exec_() == QDialog.Accepted:
            self.work_minutes = dialog.get_work_value()         #functions at end of CustomTimer class
            self.break_minutes = dialog.get_break_value()
            # reset timer
            self.mode = "work"
            self.mode_menu.setTitle(f"   ~~~~~{self.mode}~~~~~  ")  # special for setting work title on menu
            self.countdown.reset(self.work_minutes * 60)

    #Called by reset button on Main Central Widget
    def reset_timer(self):
        if self.mode == "work":
            self.countdown.reset(self.work_minutes * 60)   #does not start the clock
        else:
            self.countdown.reset(self.break_minutes * 60)

    #Called when remaining_seconds == 0, should call a CustomMessage Dialog popup, change mode Label, and set new total_seconds
    def session_finished(self):
        self.alarm.play()
        if self.mode == "work":
            # Switch to break
            break_popup = CustomMessage("Session Over!", "~~take a break~~", self, "clock_ring.png")  #replace with file path
            break_popup.exec_()
            self.mode = "break"
            self.countdown.start(self.break_minutes * 60)           #after work, DOES start break timer
            self.mode_menu.setTitle(f"  ~~~~~{self.mode}~~~~~  ")   #special for setting break title on menu

        else:
            # Switch back to work
            work_popup = CustomMessage("Break Over!", "~~back to work~~", self, "clock_ring.png")   #replace with file path
            work_popup.exec_()
            self.mode = "work"
            self.countdown.reset(self.work_minutes * 60)        #after one cycle, does NOT start work timer
            self.mode_menu.setTitle(f"   ~~~~~{self.mode}~~~~~  ")    #special for setting work title on menu

    #Called by plan lofi in menubar (ensures music cannot be paused, restarted, or resumed before lofi starts)
    def play_lofi(self):
        # add music wav file
        url = QUrl.fromLocalFile("lofi.wav")  #replace with file path
        content = QMediaContent(url)
        self.player.setMedia(content)
        self.player.setVolume(50)
        self.player.play()

    #called by View menu in menubar
    def toggle_always_on_top(self, checked):
        if checked:
            self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        else:
            self.setWindowFlags(self.windowFlags() & ~Qt.WindowStaysOnTopHint)
        self.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
