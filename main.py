import sys
import os
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QToolBar, QLineEdit, QAction, QTabWidget, QTabBar, QLabel, QVBoxLayout, QSizePolicy, QFrame

class SafariTabBar(QTabBar):
    def tabSizeHint(self, index):
        size = super().tabSizeHint(index)
        size.setWidth(200)  # Set fixed tab width
        return size

    def tabInserted(self, index):
        super().tabInserted(index)
        self.updateCloseButton(index)

    def tabRemoved(self, index):
        super().tabRemoved(index)
        self.updateCloseButton(index)

    def updateCloseButton(self, index):
        for i in range(self.count()):
            close_button = QPushButton('❌')
            close_button.setStyleSheet("background: transparent; border: none;")
            close_button.clicked.connect(lambda _, i=i: self.parent().parent().close_tab(i))
            self.setTabButton(i, QTabBar.RightSide, close_button)

class TransparentBrowser(QMainWindow):
    def __init__(self):
        super().__init__()

        # Set up the main window
        self.setWindowTitle('Decimal Browser')
        self.setGeometry(50, 50, 1700, 1000)  # Adjusted window size
        self.setWindowFlags(Qt.FramelessWindowHint)
        
        # Set window to be semi-transparent
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setStyleSheet("background: rgba(28, 28, 30, 0.8); border-radius: 15px;")

        # Create tab widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(False)
        self.tab_widget.setTabBar(SafariTabBar())
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border-top: 2px solid lightgray;
                background: rgba(28, 28, 30, 0.8);
                border-radius: 10px;
            }
            QTabBar::tab {
                background: rgba(58, 58, 60, 0.8);
                color: white;
                border: 1px solid rgba(58, 58, 60, 0.8);
                border-bottom-color: transparent;
                border-top-left-radius: 10px;
                border-top-right-radius: 10px;
                padding: 10px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background: rgba(28, 28, 30, 0.8);
                color: white;
                border: 1px solid rgba(28, 28, 30, 0.8);
                border-bottom: 2px solid rgba(28, 28, 30, 0.8);
            }
            QTabBar::close-button {
                image: url(close_icon.png);  # Make sure to have a close icon image
            }
        """)
        self.tab_widget.tabCloseRequested.connect(self.close_tab)
        self.add_new_tab()  # Create initial tab

        # Create navigation bar
        navbar = QToolBar()
        navbar.setStyleSheet("""
            QToolBar {
                background: rgba(28, 28, 30, 0.8);
                border: none;
                border-radius: 10px;
            }
            QToolButton {
                background: transparent;
                color: white;
                font-size: 18px;
                padding: 5px;
            }
            QLineEdit {
                background: rgba(58, 58, 60, 0.8);
                border: none;
                border-radius: 15px;
                padding: 10px;
                color: white;
                font-size: 18px;
                min-width: 300px;  # Adjusted min-width for URL bar
            }
        """)
        navbar.setIconSize(QSize(24, 24))  # Adjust icon size

        # Add close button
        close_btn = QAction('❌', self)
        close_btn.triggered.connect(self.close)
        navbar.addAction(close_btn)

        # Add navigation buttons
        back_btn = QAction('⬅️', self)  # Emoji for back
        back_btn.triggered.connect(self.current_browser().back)
        navbar.addAction(back_btn)

        forward_btn = QAction('➡️', self)  # Emoji for forward
        forward_btn.triggered.connect(self.current_browser().forward)
        navbar.addAction(forward_btn)

        reload_btn = QAction('🔄', self)  # Emoji for reload
        reload_btn.triggered.connect(self.current_browser().reload)
        navbar.addAction(reload_btn)

        home_btn = QAction('🏠', self)  # Emoji for home
        home_btn.triggered.connect(self.navigate_home)
        navbar.addAction(home_btn)

        # Add URL bar
        self.url_bar = QLineEdit()
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        navbar.addWidget(self.url_bar)

        # Add new tab button on the right side
        new_tab_btn = QAction('➕', self)  # Emoji for plus
        new_tab_btn.triggered.connect(self.add_new_tab)
        navbar.addAction(new_tab_btn)

        # Add full screen button
        fullscreen_btn = QAction('🖥️', self)  # Emoji for full screen
        fullscreen_btn.triggered.connect(self.toggle_fullscreen)
        navbar.addAction(fullscreen_btn)

        self.addToolBar(navbar)

        # Set tab widget as the central widget
        self.setCentralWidget(self.tab_widget)

        # Update URL bar as we browse
        self.current_browser().urlChanged.connect(self.update_url)

        # For dragging functionality
        self.oldPos = self.pos()

    def add_new_tab(self):
        browser = QWebEngineView()
        browser.setUrl(QUrl.fromLocalFile(os.path.abspath("index.html")))
        index = self.tab_widget.addTab(browser, "New Tab")
        self.tab_widget.setCurrentWidget(browser)
        browser.titleChanged.connect(lambda title: self.update_tab_name(browser, title))
        self.tab_widget.tabBar().updateCloseButton(index)  # Update close button for the new tab
        return browser

    def close_tab(self, index):
        widget = self.tab_widget.widget(index)
        if widget is not None:
            widget.deleteLater()
            self.tab_widget.removeTab(index)
            self.tab_widget.tabBar().updateCloseButton(index)  # Update close buttons after closing

    def current_browser(self):
        return self.tab_widget.currentWidget()

    def navigate_to_url(self):
        url = self.url_bar.text()
        if not url.startswith('http'):
            url = 'http://' + url
        self.current_browser().setUrl(QUrl(url))

    def update_url(self, q):
        self.url_bar.setText(q.toString())

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.oldPos = event.globalPos()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            delta = QPoint(event.globalPos() - self.oldPos)
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.oldPos = event.globalPos()
            event.accept()

    def navigate_home(self):
        self.current_browser().setUrl(QUrl.fromLocalFile(os.path.abspath("index.html")))

    def update_tab_name(self, browser, title):
        index = self.tab_widget.indexOf(browser)
        if index >= 0:
            self.tab_widget.setTabText(index, title)

        # Check if YouTube is loaded in the current tab
        if 'youtube.com' in self.current_browser().url().toString():
            # Enable custom full-screen mode for YouTube
            self.current_browser().page().fullScreenRequested.connect(self.enable_youtube_fullscreen)

    def enable_youtube_fullscreen(self, request):
        # Accept the full-screen request
        request.accept()

    def keyPressEvent(self, event):
        # Check for the F key press (for toggling full-screen mode)
        if event.key() == Qt.Key_F:
            # Toggle full-screen mode
            self.toggle_fullscreen()

    def toggle_fullscreen(self):
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()

if __name__ == '__main__':
    app = QApplication(sys.argv)

    # Set application style for better appearance
    app.setStyle('Fusion')

    window = TransparentBrowser()
    window.show()
    
    sys.exit(app.exec_())
