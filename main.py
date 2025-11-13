# main.py
import sys
import os
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QMessageBox, QCheckBox, QProgressBar
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from auth import create_master_password, verify_master_password, MASTER_FILE, check_password_strength
from database import init_db, load_or_create_diary_key
from ui.diary_ui import DiaryWindow


class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("📔 SecureDiary - Login")
        self.setGeometry(600, 300, 420, 350)
        self.setStyleSheet("""
            QWidget { 
                background-color: #0a0a0a; 
                color: #EEEEEE; 
                font-family: 'Segoe UI', Arial;
            }
            QLabel {
                color: #EEEEEE;
                font-size: 14px;
            }
            QLineEdit {
                background-color: #1a1a1a;
                border: 2px solid #2a2a2a;
                border-radius: 8px;
                padding: 12px;
                color: #EEEEEE;
                font-size: 13px;
            }
            QLineEdit:focus {
                border: 2px solid #8b7355;
            }
            QPushButton {
                background-color: #8b7355;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #a0866f;
            }
            QPushButton:pressed {
                background-color: #6b5844;
            }
            QCheckBox {
                color: #AAAAAA;
                spacing: 8px;
            }
            QProgressBar {
                border: 2px solid #2a2a2a;
                border-radius: 5px;
                text-align: center;
                background-color: #1a1a1a;
            }
            QProgressBar::chunk {
                border-radius: 3px;
            }
        """)

        self.attempts = 0
        self.max_attempts = 5
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(30, 30, 30, 30)

        # Title
        self.title_label = QLabel("📔 SecureDiary")
        title_font = QFont("Segoe UI", 24, QFont.Weight.Bold)
        self.title_label.setFont(title_font)
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.title_label)

        # Subtitle
        self.subtitle_label = QLabel("Your Private Encrypted Journal")
        subtitle_font = QFont("Segoe UI", 11)
        self.subtitle_label.setFont(subtitle_font)
        self.subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.subtitle_label.setStyleSheet("color: #888888;")
        layout.addWidget(self.subtitle_label)

        layout.addSpacing(10)

        # Password input
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setPlaceholderText("Master password")
        self.password_input.returnPressed.connect(self.check_password)
        self.password_input.textChanged.connect(self.on_password_change)
        layout.addWidget(self.password_input)

        # Password strength bar (only for creation)
        self.strength_bar = QProgressBar()
        self.strength_bar.setTextVisible(False)
        self.strength_bar.setMaximum(100)
        self.strength_bar.hide()
        layout.addWidget(self.strength_bar)

        self.strength_label = QLabel("")
        self.strength_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.strength_label.hide()
        layout.addWidget(self.strength_label)

        # Show password checkbox
        show_layout = QHBoxLayout()
        self.show_chk = QCheckBox("Show password")
        self.show_chk.stateChanged.connect(self.toggle_show)
        show_layout.addStretch()
        show_layout.addWidget(self.show_chk)
        layout.addLayout(show_layout)

        layout.addSpacing(10)

        # Unlock button
        self.unlock_btn = QPushButton("🔓 Open Diary")
        self.unlock_btn.clicked.connect(self.check_password)
        layout.addWidget(self.unlock_btn)

        # Info label
        self.info_label = QLabel("")
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.info_label.setStyleSheet("color: #FF6666; font-size: 12px;")
        layout.addWidget(self.info_label)

        layout.addStretch()

        self.setLayout(layout)

        # Check if first time
        if not os.path.exists(MASTER_FILE):
            self.subtitle_label.setText("Create Your Master Password")
            self.unlock_btn.setText("✅ Create Password")
            self.strength_bar.show()
            self.strength_label.show()
            self.info_label.setText("⚠️ Choose a strong password you won't forget!")
            self.info_label.setStyleSheet("color: #FFA500; font-size: 12px;")

    def on_password_change(self):
        """Show password strength in real-time during creation"""
        if not os.path.exists(MASTER_FILE):
            password = self.password_input.text()
            if password:
                strength, color = check_password_strength(password)
                
                if strength == "Weak":
                    self.strength_bar.setValue(33)
                elif strength == "Medium":
                    self.strength_bar.setValue(66)
                else:
                    self.strength_bar.setValue(100)
                
                self.strength_bar.setStyleSheet(f"QProgressBar::chunk {{ background-color: {color}; }}")
                self.strength_label.setText(f"Strength: {strength}")
                self.strength_label.setStyleSheet(f"color: {color}; font-weight: bold;")
            else:
                self.strength_bar.setValue(0)
                self.strength_label.setText("")

    def toggle_show(self, state):
        self.password_input.setEchoMode(
            QLineEdit.EchoMode.Normal if state else QLineEdit.EchoMode.Password
        )

    def check_password(self):
        password = self.password_input.text().strip()
        
        if not password:
            QMessageBox.warning(self, "Empty Password", "Please enter a password.")
            return

        # First-time setup → create master password
        if not os.path.exists(MASTER_FILE):
            if len(password) < 8:
                QMessageBox.warning(
                    self, 
                    "Weak Password", 
                    "Password must be at least 8 characters long!\n\nFor better security, use:\n• Uppercase and lowercase letters\n• Numbers\n• Special characters"
                )
                return
            
            strength, _ = check_password_strength(password)
            if strength == "Weak":
                reply = QMessageBox.question(
                    self,
                    "Weak Password Warning",
                    "Your password is weak. Are you sure you want to use it?\n\nA stronger password is recommended for security.",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if reply == QMessageBox.StandardButton.No:
                    return
            
            create_master_password(password)
            QMessageBox.information(
                self, 
                "✅ Success!", 
                "Master password created successfully!\n\n📔 Your diary is now protected.\n\nPlease restart the application to login."
            )
            sys.exit(0)
            return

        # Normal login
        self.attempts += 1
        
        if verify_master_password(password):
            init_db()
            try:
                key = load_or_create_diary_key(password)
            except FileNotFoundError as e:
                QMessageBox.critical(
                    self, 
                    "🔒 Diary Locked", 
                    f"Critical security files are missing!\n\n{str(e)}\n\nYour diary entries cannot be decrypted."
                )
                return
            except ValueError:
                QMessageBox.critical(
                    self, 
                    "❌ Access Denied", 
                    "Unable to decrypt diary key.\n\nWrong master password or corrupted diary."
                )
                return

            QMessageBox.information(self, "✅ Welcome Back", "Your diary is ready!")
            self.close()
            self.diary = DiaryWindow(key)
            self.diary.show()
        else:
            remaining = self.max_attempts - self.attempts
            
            if remaining <= 0:
                QMessageBox.critical(
                    self,
                    "🚫 Security Lockout",
                    "Too many failed attempts!\n\nApplication will now close for security."
                )
                sys.exit(1)
            
            self.info_label.setText(f"❌ Incorrect password! {remaining} attempts remaining")
            self.password_input.clear()
            self.password_input.setFocus()


if __name__ == "__main__":
    if not os.path.exists("diary_data"):
        os.makedirs("diary_data", exist_ok=True)

    app = QApplication(sys.argv)
    window = LoginWindow()
    window.show()
    sys.exit(app.exec())