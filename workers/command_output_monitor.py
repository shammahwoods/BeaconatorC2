import re
from pathlib import Path
from PyQt6.QtCore import QThread, pyqtSignal
from database import BeaconRepository

class CommandOutputMonitor(QThread):
    """Monitor output from a specific beacon"""
    output_received = pyqtSignal(str)
    
    def __init__(self, beacon_id: str, beacon_repository: BeaconRepository, config):
        super().__init__()
        self.beacon_id = beacon_id
        self.beacon_repository = beacon_repository
        self.running = True
        self.output_file = Path(config.LOGS_FOLDER) / f"output_{beacon_id}.txt"
        self.last_content = None

    def get_latest_content(self, content: str) -> str:
        """Extract content from the last timestamp onwards"""
        # Match timestamp pattern [YYYY-MM-DD HH:MM:SS]
        timestamps = list(re.finditer(r'\[\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\]', content))
        
        if not timestamps:
            return content
            
        # Get the position of the last timestamp
        last_timestamp_pos = timestamps[-1].start()
        return content[last_timestamp_pos:]

    def run(self):
        import utils  # Import here to avoid circular imports
        while self.running:
            try:
                if self.output_file.exists():
                    with open(self.output_file, 'r') as f:
                        content = f.read()
                        if content:
                            latest_content = self.get_latest_content(content)
                            # Only emit if content has changed
                            if latest_content != self.last_content:
                                self.last_content = latest_content
                                self.output_received.emit(latest_content)
                                
            except Exception as e:
                if utils.logger:
                    utils.logger.log_message(f"Error reading output file: {e}")
            self.msleep(100)

    def stop(self):
        self.running = False