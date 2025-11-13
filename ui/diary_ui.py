# ui/diary_ui.py
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QMessageBox, QApplication, QLineEdit, QScrollArea, QFrame, QComboBox
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont
from database import fetch_entries, delete_entry, toggle_favorite, get_stats
from ui.entry_ui import AddEntryWindow, ViewEntryWindow
from utils import format_date_only, get_preview, get_mood_emoji
import os
import sys

AUTO_LOCK_TIME = 10 * 60 * 1000  # 10 minutes auto-lock


class DiaryWindow(QWidget):
    def __init__(self, key):
        super().__init__()
        self.key = key
        self.setWindowTitle("📔 SecureDiary - My Journal")
        self.setGeometry(350, 100, 1200, 700)
        self.setStyleSheet("""
            QWidget { 
                background-color: #0a0a0a; 
                color: #EEEEEE; 
                font-family: 'Segoe UI';
            }
            QPushButton { 
                background-color: #2a2a2a; 
                border-radius: 6px; 
                padding: 8px 15px;
                color: #EEEEEE;
                font-weight: bold;
                min-width: 80px;
            }
            QPushButton:hover { 
                background-color: #3a3a3a; 
            }
            QPushButton#add {
                background-color: #8b7355;
            }
            QPushButton#add:hover {
                background-color: #a0866f;
            }
            QPushButton#lock {
                background-color: #8b4513;
            }
            QPushButton#lock:hover {
                background-color: #a0522d;
            }
            QLineEdit, QComboBox {
                background-color: #1a1a1a;
                border: 2px solid #2a2a2a;
                border-radius: 6px;
                padding: 8px;
                color: #EEEEEE;
            }
            QLineEdit:focus, QComboBox:focus {
                border: 2px solid #8b7355;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #EEEEEE;
            }
            QScrollArea {
                border: none;
            }
        """)

        self.setup_ui()
        self.load_entries()
        self.setup_autolock()

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Header
        header_container = QVBoxLayout()
        
        # Top row: Title and buttons
        top_row = QHBoxLayout()
        
        title_section = QVBoxLayout()
        title = QLabel("📔 My Encrypted Diary")
        title_font = QFont("Segoe UI", 20, QFont.Weight.Bold)
        title.setFont(title_font)
        title.setStyleSheet("color: #FFFFFF;")
        title_section.addWidget(title)
        
        self.stats_label = QLabel("Loading...")
        self.stats_label.setStyleSheet("color: #888888; font-size: 12px;")
        title_section.addWidget(self.stats_label)
        
        top_row.addLayout(title_section)
        top_row.addStretch()

        # Action buttons
        self.add_btn = QPushButton("✍️ New Entry")
        self.add_btn.setObjectName("add")
        self.add_btn.clicked.connect(self.open_new_entry)

        self.refresh_btn = QPushButton("🔄 Refresh")
        self.refresh_btn.clicked.connect(self.load_entries)

        self.lock_btn = QPushButton("🔒 Lock Diary")
        self.lock_btn.setObjectName("lock")
        self.lock_btn.clicked.connect(self.lock_diary)

        for b in [self.add_btn, self.refresh_btn, self.lock_btn]:
            top_row.addWidget(b)
        
        header_container.addLayout(top_row)
        
        # Filters row
        filters_layout = QHBoxLayout()
        
        # Search
        filters_layout.addWidget(QLabel("🔍"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search entries by title...")
        self.search_input.textChanged.connect(self.on_search)
        filters_layout.addWidget(self.search_input, stretch=3)
        
        # Mood filter
        filters_layout.addWidget(QLabel("😊"))
        self.mood_filter = QComboBox()
        self.mood_filter.addItems([
            "All Moods", "Happy", "Sad", "Excited", "Angry", 
            "Calm", "Anxious", "Grateful", "Reflective", "Loved", "Tired"
        ])
        self.mood_filter.currentTextChanged.connect(self.on_filter_change)
        filters_layout.addWidget(self.mood_filter, stretch=1)
        
        # Favorites filter
        self.favorites_btn = QPushButton("⭐ Show Favorites")
        self.favorites_btn.setCheckable(True)
        self.favorites_btn.clicked.connect(self.on_filter_change)
        filters_layout.addWidget(self.favorites_btn)
        
        header_container.addLayout(filters_layout)
        
        layout.addLayout(header_container)

        # Scrollable entries area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        self.entries_widget = QWidget()
        self.entries_layout = QVBoxLayout(self.entries_widget)
        self.entries_layout.setSpacing(15)
        self.entries_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        scroll.setWidget(self.entries_widget)
        layout.addWidget(scroll)

        # Footer
        footer = QLabel("💭 Your thoughts are safe here, encrypted with AES-256")
        footer.setStyleSheet("color: #666666; font-size: 11px; font-style: italic;")
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(footer)

        self.setLayout(layout)

    def update_stats(self):
        """Update statistics display"""
        try:
            stats = get_stats()
            total = stats["total_entries"]
            favorites = stats["favorites"]
            diary_ok = "✅ Encrypted" if stats["diary_encrypted"] else "❌ Not Encrypted"
            self.stats_label.setText(f"📊 {total} entries | ⭐ {favorites} favorites | {diary_ok}")
        except Exception as e:
            self.stats_label.setText(f"⚠️ Error loading stats: {str(e)}")

    def on_search(self):
        """Handle search"""
        self.load_entries()

    def on_filter_change(self):
        """Handle filter changes"""
        self.load_entries()

    def load_entries(self):
        """Load and display entries"""
        # Clear existing entries
        for i in reversed(range(self.entries_layout.count())): 
            widget = self.entries_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()
        
        # Get filter values
        search_query = self.search_input.text().strip() or None
        mood_filter = self.mood_filter.currentText() if self.mood_filter.currentText() != "All Moods" else None
        show_favorites = self.favorites_btn.isChecked()
        
        try:
            entries = fetch_entries(self.key, search_query, mood_filter, show_favorites)
            self.update_stats()
        except Exception as e:
            QMessageBox.critical(self, "❌ Error", f"Failed to load entries:\n{str(e)}")
            return

        if not entries:
            empty_label = QLabel("📝 No entries found.\n\nStart writing your first diary entry!")
            empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty_label.setStyleSheet("color: #666666; font-size: 16px; padding: 100px;")
            self.entries_layout.addWidget(empty_label)
            return

        # Create entry cards
        for entry in entries:
            self.create_entry_card(entry)

    def create_entry_card(self, entry):
        """Create a card widget for each entry"""
        card = QFrame()
        card.setFrameShape(QFrame.Shape.StyledPanel)
        card.setStyleSheet("""
            QFrame {
                background-color: #1a1a1a;
                border: 2px solid #2a2a2a;
                border-radius: 10px;
                padding: 15px;
            }
            QFrame:hover {
                border: 2px solid #8b7355;
            }
        """)
        
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(10)
        
        # Header row: Title, mood, favorite
        header_row = QHBoxLayout()
        
        # Title
        title_label = QLabel(entry["title"])
        title_label.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #FFFFFF;")
        header_row.addWidget(title_label)
        
        header_row.addStretch()
        
        # Mood emoji
        if entry["mood"]:
            mood_label = QLabel(f"{get_mood_emoji(entry['mood'])} {entry['mood']}")
            mood_label.setStyleSheet("color: #AAAAAA; font-size: 12px;")
            header_row.addWidget(mood_label)
        
        # Favorite star
        favorite_icon = "⭐" if entry["is_favorite"] else "☆"
        favorite_label = QLabel(favorite_icon)
        favorite_label.setStyleSheet("font-size: 18px;")
        header_row.addWidget(favorite_label)
        
        card_layout.addLayout(header_row)
        
        # Date
        date_label = QLabel(format_date_only(entry["created_at"]))
        date_label.setStyleSheet("color: #888888; font-size: 11px;")
        card_layout.addWidget(date_label)
        
        # Preview content
        if entry["decryptable"]:
            preview = get_preview(entry["content"], 200)
        else:
            preview = entry["content"]
        
        content_label = QLabel(preview)
        content_label.setWordWrap(True)
        content_label.setStyleSheet(
            "color: #CCCCCC; font-size: 12px; line-height: 1.5;" if entry["decryptable"]
            else "color: #FF6666; font-size: 12px;"
        )
        card_layout.addWidget(content_label)
        
        # Tags
        if entry["tags"]:
            tags_label = QLabel(f"🏷️ {entry['tags']}")
            tags_label.setStyleSheet("color: #8b7355; font-size: 11px;")
            card_layout.addWidget(tags_label)
        
        # Action buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        view_btn = QPushButton("👁 Read")
        view_btn.setMaximumWidth(80)
        view_btn.clicked.connect(lambda checked, eid=entry["id"]: self.view_entry(eid))
        
        edit_btn = QPushButton("✏ Edit")
        edit_btn.setMaximumWidth(80)
        edit_btn.clicked.connect(lambda checked, eid=entry["id"]: self.edit_entry(eid))
        
        fav_btn = QPushButton("⭐" if not entry["is_favorite"] else "☆")
        fav_btn.setMaximumWidth(50)
        fav_btn.setToolTip("Toggle favorite")
        fav_btn.clicked.connect(lambda checked, eid=entry["id"]: self.toggle_favorite_entry(eid))
        
        delete_btn = QPushButton("🗑")
        delete_btn.setMaximumWidth(50)
        delete_btn.setStyleSheet("QPushButton { background-color: #8b0000; }")
        delete_btn.clicked.connect(lambda checked, eid=entry["id"], title=entry["title"]: self.delete_entry_confirm(eid, title))
        
        for btn in [view_btn, edit_btn, fav_btn, delete_btn]:
            btn_layout.addWidget(btn)
        
        card_layout.addLayout(btn_layout)
        
        self.entries_layout.addWidget(card)

    def view_entry(self, entry_id):
        """View full entry"""
        from database import get_entry_by_id
        entry = get_entry_by_id(entry_id, self.key)
        
        if not entry:
            QMessageBox.warning(self, "Error", "Entry not found!")
            return
        
        if not entry["decryptable"]:
            QMessageBox.warning(
                self,
                "⚠️ Cannot View",
                "This entry cannot be decrypted!\n\nThe diary key may be missing or corrupted."
            )
            return
        
        self.view_window = ViewEntryWindow(entry, self.key, parent=self)
        self.view_window.show()

    def edit_entry(self, entry_id):
        """Edit existing entry"""
        from database import get_entry_by_id
        entry = get_entry_by_id(entry_id, self.key)
        
        if not entry:
            QMessageBox.warning(self, "Error", "Entry not found!")
            return
        
        if not entry["decryptable"]:
            QMessageBox.warning(
                self,
                "⚠️ Cannot Edit",
                "This entry cannot be edited because it's undecryptable!\n\nThe diary key may be missing or corrupted."
            )
            return
        
        self.edit_window = AddEntryWindow(self.key, entry, parent=self)
        self.edit_window.show()

    def toggle_favorite_entry(self, entry_id):
        """Toggle favorite status"""
        try:
            toggle_favorite(entry_id)
            self.load_entries()
        except Exception as ex:
            QMessageBox.critical(self, "❌ Error", f"Failed to toggle favorite:\n{str(ex)}")

    def delete_entry_confirm(self, entry_id, title):
        """Delete entry with confirmation"""
        reply = QMessageBox.question(
            self,
            "🗑️ Delete Entry?",
            f"Are you sure you want to delete:\n\n📝 {title}\n\n⚠️ This action cannot be undone!",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                delete_entry(entry_id)
                QMessageBox.information(self, "✅ Deleted", "Entry deleted successfully.")
                self.load_entries()
            except Exception as ex:
                QMessageBox.critical(self, "❌ Error", f"Failed to delete:\n{str(ex)}")

    def open_new_entry(self):
        """Open new entry window"""
        self.new_window = AddEntryWindow(self.key, parent=self)
        self.new_window.show()

    def setup_autolock(self):
        """Setup auto-lock timer for inactivity"""
        self.inactivity_timer = QTimer()
        self.inactivity_timer.timeout.connect(self.lock_diary)
        self.inactivity_timer.start(AUTO_LOCK_TIME)
        self.installEventFilter(self)

    def eventFilter(self, obj, event):
        """Reset inactivity timer on user interaction"""
        self.inactivity_timer.start(AUTO_LOCK_TIME)
        return super().eventFilter(obj, event)

    def lock_diary(self):
        """Lock the diary and return to login"""
        QMessageBox.information(
            self,
            "🔒 Auto-Lock",
            "Diary locked due to inactivity.\n\nPlease login again to access your entries."
        )
        self.close()
        QApplication.quit()
        os.system(f"python {sys.argv[0]}")
