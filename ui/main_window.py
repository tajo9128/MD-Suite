"""
Main Window Module for BioDockify MD Universal
Professional PyQt6 UI for MD simulations
"""

import sys
import os
import logging
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QProgressBar, QTextEdit, QGroupBox,
    QFileDialog, QMessageBox, QStatusBar, QMenuBar, QMenu,
    QTabWidget, QTableWidget, QTableWidgetItem, QComboBox,
    QSpinBox, QDoubleSpinBox, QCheckBox, QFrame
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QThread
from PyQt6.QtGui import QAction, QIcon, QFont

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    """
    Main application window for BioDockify MD Universal.
    
    Provides professional UI for managing MD simulations with
    GPU detection, segment management, and progress tracking.
    """
    
    # Signals
    simulation_started = pyqtSignal()
    simulation_stopped = pyqtSignal()
    progress_updated = pyqtSignal(float)
    
    def __init__(self):
        super().__init__()
        
        self.project_path = None
        self.is_simulation_running = False
        
        # Core modules (will be initialized)
        self.gpu_info = {}
        self.backend = "gmx_cpu"
        self.segment_manager = None
        self.nanobot = None
        
        self.init_ui()
        self.detect_hardware()
        
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("BioDockify MD Universal")
        self.setMinimumSize(1000, 700)
        
        # Apply stylesheet
        self.apply_stylesheet()
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        
        # Add menu bar
        self.create_menu_bar()
        
        # Add tab widget
        tabs = QTabWidget()
        main_layout.addWidget(tabs)
        
        # Tab 1: Simulation Control
        tabs.addTab(self.create_simulation_tab(), "Simulation")
        
        # Tab 2: Hardware Info
        tabs.addTab(self.create_hardware_tab(), "Hardware")
        
        # Tab 3: Project Settings
        tabs.addTab(self.create_settings_tab(), "Settings")
        
        # Tab 4: Log Viewer
        tabs.addTab(self.create_log_tab(), "Logs")
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
        
    def create_menu_bar(self):
        """Create menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("File")
        
        new_action = QAction("New Project", self)
        new_action.triggered.connect(self.new_project)
        file_menu.addAction(new_action)
        
        open_action = QAction("Open Project", self)
        open_action.triggered.connect(self.open_project)
        file_menu.addAction(open_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Simulation menu
        sim_menu = menubar.addMenu("Simulation")
        
        start_action = QAction("Start", self)
        start_action.triggered.connect(self.start_simulation)
        sim_menu.addAction(start_action)
        
        stop_action = QAction("Stop", self)
        stop_action.triggered.connect(self.stop_simulation)
        sim_menu.addAction(stop_action)
        
        resume_action = QAction("Resume", self)
        resume_action.triggered.connect(self.resume_simulation)
        sim_menu.addAction(resume_action)
        
        # Tools menu
        tools_menu = menubar.addMenu("Tools")
        
        package_action = QAction("Create Publication Package", self)
        package_action.triggered.connect(self.create_package)
        tools_menu.addAction(package_action)
        
        analyze_action = QAction("Run Analysis", self)
        analyze_action.triggered.connect(self.run_analysis)
        tools_menu.addAction(analyze_action)
        
    def create_simulation_tab(self) -> QWidget:
        """Create simulation control tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Project selection
        project_group = QGroupBox("Project")
        project_layout = QHBoxLayout()
        
        self.project_label = QLabel("No project selected")
        project_layout.addWidget(self.project_label)
        
        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self.browse_project)
        project_layout.addWidget(browse_btn)
        
        project_group.setLayout(project_layout)
        layout.addWidget(project_group)
        
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
        
        # Backend selection
        backend_layout = QHBoxLayout()
        backend_layout.addWidget(QLabel("Backend:"))
        self.backend_combo = QComboBox()
        self.backend_combo.addItems(["gmx_cuda", "gmx_sycl", "gmx_cpu"])
        backend_layout.addWidget(self.backend_combo)
        backend_layout.addStretch()
        params_layout.addLayout(backend_layout)
        
        params_group.setLayout(params_layout)
        layout.addWidget(params_group)
        
        # Progress
        progress_group = QGroupBox("Progress")
        progress_layout = QVBoxLayout()
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        progress_layout.addWidget(self.progress_bar)
        
        self.progress_label = QLabel("0% complete")
        progress_layout.addWidget(self.progress_label)
        
        self.current_segment_label = QLabel("Current segment: -")
        progress_layout.addWidget(self.current_segment_label)
        
        progress_group.setLayout(progress_layout)
        layout.addWidget(progress_group)
        
        # Control buttons
        button_layout = QHBoxLayout()
        
        self.start_btn = QPushButton("Start Simulation")
        self.start_btn.clicked.connect(self.start_simulation)
        button_layout.addWidget(self.start_btn)
        
        self.stop_btn = QPushButton("Stop")
        self.stop_btn.clicked.connect(self.stop_simulation)
        self.stop_btn.setEnabled(False)
        button_layout.addWidget(self.stop_btn)
        
        self.resume_btn = QPushButton("Resume")
        self.resume_btn.clicked.connect(self.resume_simulation)
        button_layout.addWidget(self.resume_btn)
        
        layout.addLayout(button_layout)
        
        layout.addStretch()
        
        return widget
        
    def create_hardware_tab(self) -> QWidget:
        """Create hardware info tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Hardware info group
        hw_group = QGroupBox("Detected Hardware")
        hw_layout = QVBoxLayout()
        
        self.hw_vendor = QLabel("GPU Vendor: Detecting...")
        hw_layout.addWidget(self.hw_vendor)
        
        self.hw_device = QLabel("Device: -")
        hw_layout.addWidget(self.hw_device)
        
        self.hw_vram = QLabel("VRAM: -")
        hw_layout.addWidget(self.hw_vram)
        
        self.hw_backend = QLabel("Selected Backend: -")
        hw_layout.addWidget(self.hw_backend)
        
        hw_group.setLayout(hw_layout)
        layout.addWidget(hw_group)
        
        # Refresh button
        refresh_btn = QPushButton("Refresh Hardware Detection")
        refresh_btn.clicked.connect(self.detect_hardware)
        layout.addWidget(refresh_btn)
        
        layout.addStretch()
        
        return widget
        
    def create_settings_tab(self) -> QWidget:
        """Create settings tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Notifications
        notif_group = QGroupBox("Notifications")
        notif_layout = QVBoxLayout()
        
        self.enable_telegram = QCheckBox("Enable Telegram Notifications")
        notif_layout.addWidget(self.enable_telegram)
        
        self.enable_email = QCheckBox("Enable Email Notifications")
        notif_layout.addWidget(self.enable_email)
        
        notif_group.setLayout(notif_layout)
        layout.addWidget(notif_group)
        
        # Safety
        safety_group = QGroupBox("Safety Settings")
        safety_layout = QVBoxLayout()
        
        temp_layout = QHBoxLayout()
        temp_layout.addWidget(QLabel("Max Temperature (°C):"))
        self.temp_limit = QSpinBox()
        self.temp_limit.setRange(50, 100)
        self.temp_limit.setValue(85)
        temp_layout.addWidget(self.temp_limit)
        safety_layout.addLayout(temp_layout)
        
        disk_layout = QHBoxLayout()
        disk_layout.addWidget(QLabel("Min Disk Space (GB):"))
        self.disk_limit = QSpinBox()
        self.disk_limit.setRange(1, 100)
        self.disk_limit.setValue(5)
        disk_layout.addWidget(self.disk_limit)
        safety_layout.addLayout(disk_layout)
        
        safety_group.setLayout(safety_layout)
        layout.addWidget(safety_group)
        
        layout.addStretch()
        
        return widget
        
    def create_log_tab(self) -> QWidget:
        """Create log viewer tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setFont(QFont("Courier", 9))
        layout.addWidget(self.log_text)
        
        # Clear button
        clear_btn = QPushButton("Clear Logs")
        clear_btn.clicked.connect(lambda: self.log_text.clear())
        layout.addWidget(clear_btn)
        
        return widget
        
    def apply_stylesheet(self):
        """Apply custom stylesheet"""
        stylesheet = """
        QMainWindow {
            background-color: #f5f5f5;
        }
        
        QGroupBox {
            font-weight: bold;
            border: 2px solid #cccccc;
            border-radius: 5px;
            margin-top: 10px;
            padding-top: 10px;
        }
        
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px 0 5px;
        }
        
        QPushButton {
            background-color: #0078d4;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            font-weight: bold;
        }
        
        QPushButton:hover {
            background-color: #106ebe;
        }
        
        QPushButton:pressed {
            background-color: #005a9e;
        }
        
        QPushButton:disabled {
            background-color: #cccccc;
            color: #666666;
        }
        
        QProgressBar {
            border: 2px solid #cccccc;
            border-radius: 5px;
            text-align: center;
        }
        
        QProgressBar::chunk {
            background-color: #0078d4;
        }
        
        QTabWidget::pane {
            border: 1px solid #cccccc;
            background-color: white;
        }
        
        QTabBar::tab {
            background-color: #e1e1e1;
            padding: 8px 16px;
            margin-right: 2px;
        }
        
        QTabBar::tab:selected {
            background-color: white;
            border-bottom: 2px solid #0078d4;
        }
        
        QTextEdit {
            background-color: #1e1e1e;
            color: #d4d4d4;
            font-family: Consolas, Courier New;
        }
        
        QStatusBar {
            background-color: #0078d4;
            color: white;
        }
        """
        
        self.setStyleSheet(stylesheet)
        
    def detect_hardware(self):
        """Detect available hardware"""
        try:
            from core.gpu_detector import detect_gpu
            from core.backend_selector import select_backend
            
            self.gpu_info = detect_gpu()
            self.backend = select_backend(self.gpu_info)
            
            # Update UI
            self.hw_vendor.setText(f"GPU Vendor: {self.gpu_info.get('vendor', 'Unknown')}")
            self.hw_device.setText(f"Device: {self.gpu_info.get('device_name', 'N/A')}")
            self.hw_vram.setText(f"VRAM: {self.gpu_info.get('vram', 0)} MB")
            self.hw_backend.setText(f"Selected Backend: {self.backend}")
            
            # Set combo to detected backend
            index = self.backend_combo.findText(self.backend)
            if index >= 0:
                self.backend_combo.setCurrentIndex(index)
                
            self.log(f"Hardware detected: {self.gpu_info['vendor']} - {self.backend}")
            
        except Exception as e:
            self.log(f"Hardware detection error: {e}")
            self.hw_vendor.setText("GPU Vendor: Detection failed")
            
    def browse_project(self):
        """Browse for project directory"""
        directory = QFileDialog.getExistingDirectory(
            self,
            "Select Project Directory",
            os.getcwd()
        )
        
        if directory:
            self.project_path = directory
            self.project_label.setText(f"Project: {directory}")
            self.log(f"Project selected: {directory}")
            
    def new_project(self):
        """Create new project"""
        directory = QFileDialog.getExistingDirectory(
            self,
            "Create New Project Directory",
            os.getcwd()
        )
        
        if directory:
            # Create basic project structure
            os.makedirs(os.path.join(directory, "segments"), exist_ok=True)
            self.project_path = directory
            self.project_label.setText(f"Project: {directory}")
            self.log(f"New project created: {directory}")
            
    def open_project(self):
        """Open existing project"""
        self.browse_project()
        
    def start_simulation(self):
        """Start simulation"""
        if not self.project_path:
            QMessageBox.warning(self, "No Project", "Please select a project first")
            return
            
        self.is_simulation_running = True
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        
        self.log("Simulation started...")
        self.status_bar.showMessage("Simulation running...")
        
        # Update progress
        self.progress_bar.setValue(5)
        
    def stop_simulation(self):
        """Stop simulation"""
        self.is_simulation_running = False
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        
        self.log("Simulation stopped")
        self.status_bar.showMessage("Simulation stopped")
        
    def resume_simulation(self):
        """Resume simulation from checkpoint"""
        if not self.project_path:
            QMessageBox.warning(self, "No Project", "Please select a project first")
            return
            
        self.is_simulation_running = True
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        
        self.log("Resuming simulation...")
        self.status_bar.showMessage("Resuming simulation...")
        
    def create_package(self):
        """Create publication package"""
        if not self.project_path:
            QMessageBox.warning(self, "No Project", "Please select a project first")
            return
            
        self.log("Creating publication package...")
        
        try:
            from core.publication_packager import PublicationPackager
            
            packager = PublicationPackager(self.project_path)
            package_path = packager.create_publication_package()
            
            self.log(f"Package created: {package_path}")
            QMessageBox.information(self, "Success", f"Package created: {package_path}")
            
        except Exception as e:
            self.log(f"Package creation failed: {e}")
            QMessageBox.critical(self, "Error", f"Failed to create package: {e}")
            
    def run_analysis(self):
        """Run analysis on simulation results"""
        if not self.project_path:
            QMessageBox.warning(self, "No Project", "Please select a project first")
            return
            
        self.log("Running analysis...")
        
    def log(self, message: str):
        """Add message to log"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.append(f"[{timestamp}] {message}")
        logger.info(message)


def launch_ui():
    """Launch the application UI"""
    app = QApplication(sys.argv)
    app.setApplicationName("BioDockify MD Universal")
    app.setOrganizationName("BioDockify")
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    launch_ui()
