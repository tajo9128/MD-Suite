"""
Dialogs Module for BioDockify MD Universal
Custom dialog windows for the application
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QLineEdit, QComboBox, QSpinBox,
    QDoubleSpinBox, QCheckBox, QGroupBox, QTextEdit,
    QFileDialog, QMessageBox, QProgressDialog
)
from PyQt6.QtCore import Qt


class NewProjectDialog(QDialog):
    """Dialog for creating a new project"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("New Project")
        self.setModal(True)
        
        layout = QVBoxLayout(self)
        
        # Project name
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Project Name:"))
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("my_simulation")
        name_layout.addWidget(self.name_edit)
        layout.addLayout(name_layout)
        
        # Project directory
        dir_layout = QHBoxLayout()
        dir_layout.addWidget(QLabel("Directory:"))
        self.dir_edit = QLineEdit()
        self.dir_edit.setPlaceholderText("Select directory...")
        dir_layout.addWidget(self.dir_edit)
        
        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self.browse_directory)
        dir_layout.addWidget(browse_btn)
        layout.addLayout(dir_layout)
        
        # Simulation parameters
        params_group = QGroupBox("Simulation Parameters")
        params_layout = QVBoxLayout()
        
        # Total time
        time_layout = QHBoxLayout()
        time_layout.addWidget(QLabel("Total Time (ns):"))
        self.total_ns_spin = QSpinBox()
        self.total_ns_spin.setRange(1, 10000)
        self.total_ns_spin.setValue(100)
        time_layout.addWidget(self.total_ns_spin)
        time_layout.addStretch()
        params_layout.addLayout(time_layout)
        
        # Segment time
        seg_layout = QHBoxLayout()
        seg_layout.addWidget(QLabel("Segment Length (ns):"))
        self.segment_ns_spin = QSpinBox()
        self.segment_ns_spin.setRange(1, 1000)
        self.segment_ns_spin.setValue(10)
        seg_layout.addWidget(self.segment_ns_spin)
        seg_layout.addStretch()
        params_layout.addLayout(seg_layout)
        
        params_group.setLayout(params_layout)
        layout.addWidget(params_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        create_btn = QPushButton("Create")
        create_btn.clicked.connect(self.accept)
        button_layout.addWidget(create_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        
    def browse_directory(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Directory")
        if directory:
            self.dir_edit.setText(directory)
            
    def get_values(self):
        return {
            "name": self.name_edit.text(),
            "directory": self.dir_edit.text(),
            "total_ns": self.total_ns_spin.value(),
            "segment_ns": self.segment_ns_spin.value()
        }


class SettingsDialog(QDialog):
    """Dialog for application settings"""
    
    def __init__(self, parent=None, current_settings=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setModal(True)
        self.setMinimumWidth(400)
        
        layout = QVBoxLayout(self)
        
        # GROMACS settings
        gmx_group = QGroupBox("GROMACS")
        gmx_layout = QVBoxLayout()
        
        wsl_layout = QHBoxLayout()
        wsl_layout.addWidget(QLabel("WSL Distro:"))
        self.wsl_combo = QComboBox()
        self.wsl_combo.addItems(["Ubuntu", "Debian", "Arch"])
        wsl_layout.addWidget(self.wsl_combo)
        gmx_layout.addLayout(wsl_layout)
        
        gmx_group.setLayout(gmx_layout)
        layout.addWidget(gmx_group)
        
        # Notification settings
        notif_group = QGroupBox("Notifications")
        notif_layout = QVBoxLayout()
        
        self.enable_telegram = QCheckBox("Enable Telegram")
        notif_layout.addWidget(self.enable_telegram)
        
        token_layout = QHBoxLayout()
        token_layout.addWidget(QLabel("Bot Token:"))
        self.telegram_token = QLineEdit()
        self.telegram_token.setEchoMode(QLineEdit.EchoMode.Password)
        token_layout.addWidget(self.telegram_token)
        notif_layout.addLayout(token_layout)
        
        chat_layout = QHBoxLayout()
        chat_layout.addWidget(QLabel("Chat ID:"))
        self.telegram_chat = QLineEdit()
        chat_layout.addWidget(self.telegram_chat)
        notif_layout.addLayout(chat_layout)
        
        notif_group.setLayout(notif_layout)
        layout.addWidget(notif_group)
        
        # Safety settings
        safety_group = QGroupBox("Safety")
        safety_layout = QVBoxLayout()
        
        temp_layout = QHBoxLayout()
        temp_layout.addWidget(QLabel("Max Temp (°C):"))
        self.temp_limit = QSpinBox()
        self.temp_limit.setRange(50, 100)
        self.temp_limit.setValue(85)
        temp_layout.addWidget(self.temp_limit)
        temp_layout.addStretch()
        safety_layout.addLayout(temp_layout)
        
        disk_layout = QHBoxLayout()
        disk_layout.addWidget(QLabel("Min Disk (GB):"))
        self.disk_limit = QSpinBox()
        self.disk_limit.setRange(1, 100)
        self.disk_limit.setValue(5)
        disk_layout.addWidget(self.disk_limit)
        disk_layout.addStretch()
        safety_layout.addLayout(disk_layout)
        
        safety_group.setLayout(safety_layout)
        layout.addWidget(safety_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.accept)
        button_layout.addWidget(save_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        
        # Load current settings
        if current_settings:
            self.load_settings(current_settings)
            
    def load_settings(self, settings):
        """Load current settings"""
        self.wsl_combo.setCurrentText(settings.get("wsl_distro", "Ubuntu"))
        self.enable_telegram.setChecked(settings.get("enable_telegram", False))
        self.telegram_token.setText(settings.get("telegram_token", ""))
        self.telegram_chat.setText(settings.get("telegram_chat_id", ""))
        self.temp_limit.setValue(settings.get("temperature_limit", 85))
        self.disk_limit.setValue(settings.get("min_disk_space", 5))
        
    def get_settings(self):
        """Get current settings"""
        return {
            "wsl_distro": self.wsl_combo.currentText(),
            "enable_telegram": self.enable_telegram.isChecked(),
            "telegram_token": self.telegram_token.text(),
            "telegram_chat_id": self.telegram_chat.text(),
            "temperature_limit": self.temp_limit.value(),
            "min_disk_space": self.disk_limit.value()
        }


class ProgressDialog(QDialog):
    """Dialog showing simulation progress"""
    
    def __init__(self, parent=None, title="Simulation Progress"):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(False)
        self.setMinimumWidth(400)
        
        layout = QVBoxLayout(self)
        
        # Status label
        self.status_label = QLabel("Initializing...")
        layout.addWidget(self.status_label)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        layout.addWidget(self.progress_bar)
        
        # Details
        details_group = QGroupBox("Details")
        details_layout = QVBoxLayout()
        
        self.segment_label = QLabel("Segment: -")
        details_layout.addWidget(self.segment_label)
        
        self.time_label = QLabel("Time: -")
        details_layout.addWidget(self.time_label)
        
        self.nspeed_label = QLabel("Speed: -")
        details_layout.addWidget(self.nspeed_label)
        
        details_group.setLayout(details_layout)
        layout.addWidget(details_group)
        
        # Cancel button
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        layout.addWidget(self.cancel_btn)
        
    def update_progress(self, percent, segment=None, time_ns=None, speed=None):
        """Update progress display"""
        self.progress_bar.setValue(int(percent))
        
        if segment is not None:
            self.segment_label.setText(f"Segment: {segment}")
            
        if time_ns is not None:
            self.time_label.setText(f"Time: {time_ns:.2f} ns")
            
        if speed is not None:
            self.nspeed_label.setText(f"Speed: {speed} ns/day")
            
    def set_status(self, status):
        """Update status message"""
        self.status_label.setText(status)


class AboutDialog(QDialog):
    """About dialog"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("About BioDockify MD Universal")
        self.setModal(True)
        
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("<h2>BioDockify MD Universal</h2>")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Version
        version = QLabel("Version 1.0.0")
        version.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(version)
        
        # Description
        desc = QLabel(
            "Professional Multi-GPU Molecular Dynamics Simulation Framework\n"
            "for BioDockify Ecosystem"
        )
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc.setWordWrap(True)
        layout.addWidget(desc)
        
        # Features
        features = QLabel(
            "Features:\n"
            "• Multi-GPU Support (NVIDIA, AMD, Intel)\n"
            "• Segmented Simulation with Checkpoint Resume\n"
            "• Publication-Ready Output Packages\n"
            "• Professional PyQt6 UI"
        )
        layout.addWidget(features)
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)


def show_error(parent, title, message):
    """Show error message dialog"""
    QMessageBox.critical(parent, title, message)
    
    
def show_info(parent, title, message):
    """Show info message dialog"""
    QMessageBox.information(parent, title, message)
    
    
def show_warning(parent, title, message):
    """Show warning message dialog"""
    QMessageBox.warning(parent, title, message)
    
    
def ask_yes_no(parent, title, message):
    """Ask yes/no question"""
    reply = QMessageBox.question(
        parent, 
        title, 
        message,
        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
    )
    return reply == QMessageBox.StandardButton.Yes
