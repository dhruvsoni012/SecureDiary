# ui/entry_ui.py
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton,
    QMessageBox, QLabel, QTextEdit, QComboBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from database import add_entry, update_entry
from utils import format_timestamp, count_words


class AddEntryWindow(QWidget):
    """Add or Edit diary entry"""
    def __init__(self, key, entry=None, parent=None):
        super().__init__()
        self.key = key
        self.entry = entry  # If editing, this contains entry data
        self.parent_window = parent
        
        is_editing = entry is not None
        self.setWindowTitle("✏️ Edit Entry" if is_editing else "✍️ New Diary Entry")
        self.setGeometry(500, 200, 700, 700)
        self.setStyleSheet("""
            QWidget { 
                background-color: #0a0a0a; 
                color: #EEEEEE; 
                font-family: 'Segoe UI';
            }
            QLineEdit { 
                border: 2px solid #2a2a2a; 
                border-radius: 6px; 
                padding: 10px; 
                background-color: #1a1a1a;
                color: #EEEEEE;
                font-size: 13px;
            }
            QLineEdit:focus {
                border: 2px solid #8b7355;
            }
            QTextEdit {
                border: 2px solid #2a2a2a; 
                border-radius: 6px; 
                padding: 10px; 
                background-color: #1a1a1a;
                color: #EEEEEE;
                font-size: 13px;
                line-height: 1.6;
            }
            QTextEdit:focus {
                border: 2px solid #8b7355;
            }
            QComboBox {
                border: 2px solid #2a2a2a; 
                border-radius: 6px; 
                padding: 8px; 
                background-color: #1a1a1a;
                color: #EEEEEE;
            }
            QComboBox:focus {
                border: 2px solid #8b7355;
            }
            QPushButton { 
                background-color: #2a2a2a; 
                border-radius: 6px; 
                padding: 10px; 
                color: #EEEEEE;
                font-weight: bold;
            }
            QPushButton:hover { 
                background-color: #3a3a3a; 
            }
            QPushButton#primary {
                background-color: #8b7355;
            }
            QPushButton#primary:hover {
                background-color: #a0866f;
            }
            QLabel {
                color: #CCCCCC;
            }
        """)

        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(25, 25, 25, 25)

        # Title
        is_editing = self.entry is not None
        title = QLabel("✏️ Edit Your Entry" if is_editing else "✍️ Write a New Entry")
        title_font = QFont("Segoe UI", 16, QFont.Weight.Bold)
        title.setFont(title_font)
        title.setStyleSheet("color: #FFFFFF;")
        layout.addWidget(title)

        subtitle = QLabel("Express your thoughts freely - they're encrypted and safe")
        subtitle.setStyleSheet("color: #888888; font-size: 11px;")
        layout.addWidget(subtitle)

        layout.addSpacing(10)

        # Entry Title
        title_label = QLabel("Title *")
        layout.addWidget(title_label)
        
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Give your entry a title...")
        if self.entry:
            self.title_input.setText(self.entry["title"])
        layout.addWidget(self.title_input)

        # Mood and Tags row
        mood_tags_layout = QHBoxLayout()
        
        # Mood selector
        mood_layout = QVBoxLayout()
        mood_label = QLabel("How are you feeling?")
        mood_layout.addWidget(mood_label)
        
        self.mood_combo = QComboBox()
        self.mood_combo.addItems([
            "Select mood...", "😊 Happy", "😢 Sad", "🎉 Excited", 
            "😠 Angry", "😌 Calm", "😰 Anxious", "🙏 Grateful", 
            "🤔 Reflective", "❤️ Loved", "😴 Tired"
        ])
        if self.entry and self.entry["mood"]:
            # Find and set the mood
            for i in range(self.mood_combo.count()):
                if self.entry["mood"] in self.mood_combo.itemText(i):
                    self.mood_combo.setCurrentIndex(i)
                    break
        mood_layout.addWidget(self.mood_combo)
        mood_tags_layout.addLayout(mood_layout)
        
        # Tags
        tags_layout = QVBoxLayout()
        tags_label = QLabel("Tags (comma separated)")
        tags_layout.addWidget(tags_label)
        
        self.tags_input = QLineEdit()
        self.tags_input.setPlaceholderText("personal, work, ideas...")
        if self.entry and self.entry["tags"]:
            self.tags_input.setText(self.entry["tags"])
        tags_layout.addWidget(self.tags_input)
        mood_tags_layout.addLayout(tags_layout)
        
        layout.addLayout(mood_tags_layout)

        # Content
        content_label = QLabel("Your Entry *")
        layout.addWidget(content_label)
        
        self.content_input = QTextEdit()
        self.content_input.setPlaceholderText("Write your thoughts here...\n\nTip: Be honest and open - only you can read this.")
        self.content_input.textChanged.connect(self.update_word_count)
        if self.entry:
            self.content_input.setPlainText(self.entry["content"])
        layout.addWidget(self.content_input, stretch=1)

        # Word count
        self.word_count_label = QLabel("0 words")
        self.word_count_label.setStyleSheet("color: #888888; font-size: 11px;")
        self.word_count_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        layout.addWidget(self.word_count_label)

        # Update word count initially if editing
        if self.entry:
            self.update_word_count()

        # Buttons
        btn_layout = QHBoxLayout()
        
        self.cancel_btn = QPushButton("❌ Cancel")
        self.cancel_btn.clicked.connect(self.close)
        
        save_text = "💾 Update Entry" if is_editing else "💾 Save Entry"
        self.save_btn = QPushButton(save_text)
        self.save_btn.setObjectName("primary")
        self.save_btn.clicked.connect(self.save_entry)
        
        btn_layout.addWidget(self.cancel_btn)
        btn_layout.addWidget(self.save_btn)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

    def update_word_count(self):
        """Update word count label"""
        text = self.content_input.toPlainText()
        words = count_words(text)
        self.word_count_label.setText(f"{words} words")

    def save_entry(self):
        """Save or update entry"""
        title = self.title_input.text().strip()
        content = self.content_input.toPlainText().strip()
        mood_text = self.mood_combo.currentText()
        mood = mood_text.split(" ", 1)[1] if mood_text != "Select mood..." else None
        tags = self.tags_input.text().strip() or None
        
        if not title:
            QMessageBox.warning(self, "⚠️ Missing Title", "Please enter a title for your entry.")
            return
        
        if not content:
            QMessageBox.warning(self, "⚠️ Missing Content", "Please write something in your entry.")
            return
        
        try:
            if self.entry:
                # Update existing entry
                update_entry(self.entry["id"], title, content, self.key, mood, tags)
                QMessageBox.information(self, "✅ Updated", "Your entry has been updated successfully!")
            else:
                # Add new entry
                add_entry(title, content, self.key, mood, tags)
                QMessageBox.information(self, "✅ Saved", "Your entry has been saved securely!")
            
            if self.parent_window:
                self.parent_window.load_entries()
            
            self.close()
        except Exception as ex:
            QMessageBox.critical(self, "❌ Error", f"Failed to save entry:\n{str(ex)}")


class ViewEntryWindow(QWidget):
    """View entry in read-only mode"""
    def __init__(self, entry, key, parent=None):
        super().__init__()
        self.entry = entry
        self.key = key
        self.parent_window = parent
        
        self.setWindowTitle(f"📖 {entry['title']}")
        self.setGeometry(500, 200, 700, 700)
        self.setStyleSheet("""
            QWidget { 
                background-color: #0a0a0a; 
                color: #EEEEEE; 
                font-family: 'Segoe UI';
            }
            QTextEdit {
                border: 2px solid #2a2a2a; 
                border-radius: 6px; 
                padding: 15px; 
                background-color: #1a1a1a;
                color: #EEEEEE;
                font-size: 14px;
                line-height: 1.8;
            }
            QPushButton { 
                background-color: #2a2a2a; 
                border-radius: 6px; 
                padding: 10px; 
                color: #EEEEEE;
                font-weight: bold;
            }
            QPushButton:hover { 
                background-color: #3a3a3a; 
            }
            QPushButton#primary {
                background-color: #8b7355;
            }
            QPushButton#primary:hover {
                background-color: #a0866f;
            }
            QLabel {
                color: #CCCCCC;
            }
        """)

        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(25, 25, 25, 25)

        # Title
        title = QLabel(self.entry["title"])
        title_font = QFont("Segoe UI", 18, QFont.Weight.Bold)
        title.setFont(title_font)
        title.setStyleSheet("color: #FFFFFF;")
        title.setWordWrap(True)
        layout.addWidget(title)

        # Metadata row
        meta_layout = QHBoxLayout()
        
        # Date
        date_str = format_timestamp(self.entry["created_at"])
        date_label = QLabel(f"📅 {date_str}")
        date_label.setStyleSheet("color: #888888; font-size: 12px;")
        meta_layout.addWidget(date_label)
        
        meta_layout.addStretch()
        
        # Mood
        if self.entry["mood"]:
            from utils import get_mood_emoji
            mood_label = QLabel(f"{get_mood_emoji(self.entry['mood'])} {self.entry['mood']}")
            mood_label.setStyleSheet("color: #AAAAAA; font-size: 12px;")
            meta_layout.addWidget(mood_label)
        
        # Favorite
        if self.entry["is_favorite"]:
            fav_label = QLabel("⭐")
            fav_label.setStyleSheet("font-size: 16px;")
            meta_layout.addWidget(fav_label)
        
        layout.addLayout(meta_layout)

        # Tags
        if self.entry["tags"]:
            tags_label = QLabel(f"🏷️ {self.entry['tags']}")
            tags_label.setStyleSheet("color: #8b7355; font-size: 11px;")
            layout.addWidget(tags_label)

        layout.addSpacing(10)

        # Content (read-only)
        self.content_display = QTextEdit()
        self.content_display.setPlainText(self.entry["content"])
        self.content_display.setReadOnly(True)
        layout.addWidget(self.content_display, stretch=1)

        # Word count
        words = count_words(self.entry["content"])
        word_count = QLabel(f"📊 {words} words")
        word_count.setStyleSheet("color: #888888; font-size: 11px;")
        word_count.setAlignment(Qt.AlignmentFlag.AlignRight)
        layout.addWidget(word_count)

        # Buttons
        btn_layout = QHBoxLayout()
        
        self.close_btn = QPushButton("✖ Close")
        self.close_btn.clicked.connect(self.close)
        
        self.edit_btn = QPushButton("✏ Edit")
        self.edit_btn.setObjectName("primary")
        self.edit_btn.clicked.connect(self.open_edit)
        
        btn_layout.addStretch()
        btn_layout.addWidget(self.close_btn)
        btn_layout.addWidget(self.edit_btn)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

    def open_edit(self):
        """Open edit window"""
        self.close()
        if self.parent_window:
            self.parent_window.edit_entry(self.entry["id"])
