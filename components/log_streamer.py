"""Log streaming component with real-time updates.

Provides live log streaming from sandbox processes using subprocess pipes.
Supports auto-refresh, pause/resume, and log export.
"""

import streamlit as st
import subprocess
import threading
import queue
import time
from typing import Optional, List, Callable
from dataclasses import dataclass
from datetime import datetime
import re

@dataclass
class LogEntry:
    timestamp: datetime
    level: str
    message: str
    source: str

# Log level patterns for parsing
LOG_LEVEL_PATTERNS = {
    'ERROR': re.compile(r'\b(ERROR|CRITICAL|FATAL)\b', re.IGNORECASE),
    'WARNING': re.compile(r'\b(WARNING|WARN)\b', re.IGNORECASE),
    'INFO': re.compile(r'\b(INFO|INFORMATION)\b', re.IGNORECASE),
    'DEBUG': re.compile(r'\b(DEBUG|TRACE)\b', re.IGNORECASE),
}

LOG_COLORS = {
    'ERROR': '🔴',
    'WARNING': '🟡',
    'INFO': '🔵',
    'DEBUG': '⚪',
    'DEFAULT': '⚫'
}

class LogStreamer:
    """Real-time log streaming from subprocess."""
    
    def __init__(self, command: List[str], buffer_size: int = 1000):
        self.command = command
        self.buffer_size = buffer_size
        self.log_buffer: queue.Queue = queue.Queue(maxsize=buffer_size)
        self.process: Optional[subprocess.Popen] = None
        self._stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self.is_running = False
    
    def start(self) -> bool:
        """Start log streaming."""
        try:
            self.process = subprocess.Popen(
                self.command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,  # Line buffered
                universal_newlines=True
            )
            
            self._stop_event.clear()
            self._thread = threading.Thread(target=self._read_output, daemon=True)
            self._thread.start()
            self.is_running = True
            return True
            
        except Exception as e:
            self.log_buffer.put(f"Error starting log stream: {e}")
            return False
    
    def stop(self):
        """Stop log streaming."""
        self._stop_event.set()
        self.is_running = False
        
        if self.process:
            try:
                self.process.terminate()
                self.process.wait(timeout=2)
            except:
                try:
                    self.process.kill()
                except:
                    pass
            self.process = None
        
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2)
    
    def _read_output(self):
        """Read output from subprocess in background thread."""
        if not self.process or not self.process.stdout:
            return
        
        try:
            for line in iter(self.process.stdout.readline, ''):
                if self._stop_event.is_set():
                    break
                
                if line:
                    # Try to add to buffer, drop oldest if full
                    try:
                        self.log_buffer.put(line.rstrip(), block=False)
                    except queue.Full:
                        # Remove oldest entry and add new one
                        try:
                            self.log_buffer.get_nowait()
                            self.log_buffer.put(line.rstrip(), block=False)
                        except:
                            pass
        except Exception as e:
            self.log_buffer.put(f"Log stream error: {e}")
        finally:
            if self.process and self.process.stdout:
                self.process.stdout.close()
    
    def get_logs(self, count: Optional[int] = None) -> List[str]:
        """Get current log buffer contents."""
        logs = list(self.log_buffer.queue)
        if count:
            return logs[-count:]
        return logs
    
    def clear(self):
        """Clear log buffer."""
        while not self.log_buffer.empty():
            try:
                self.log_buffer.get_nowait()
            except:
                break

def parse_log_level(line: str) -> str:
    """Detect log level from log line."""
    for level, pattern in LOG_LEVEL_PATTERNS.items():
        if pattern.search(line):
            return level
    return 'DEFAULT'

def format_log_line(line: str, show_timestamp: bool = True) -> str:
    """Format a log line with level indicator."""
    level = parse_log_level(line)
    icon = LOG_COLORS.get(level, LOG_COLORS['DEFAULT'])
    
    if show_timestamp:
        timestamp = datetime.now().strftime("%H:%M:%S")
        return f"{timestamp} {icon} {line}"
    else:
        return f"{icon} {line}"

def render_log_streamer(
    openshell_service,
    sandbox_id: str,
    auto_refresh: bool = True,
    refresh_interval: float = 1.0,
    max_lines: int = 500
):
    """Render a real-time log streaming component."""
    
    # Initialize session state
    streamer_key = f"log_streamer_{sandbox_id}"
    if streamer_key not in st.session_state:
        st.session_state[streamer_key] = {
            'streamer': None,
            'is_streaming': False,
            'paused': False,
            'logs': []
        }
    
    state = st.session_state[streamer_key]
    
    st.subheader(f"📜 Live Logs: {sandbox_id}")
    
    # Control bar
    col1, col2, col3, col4, col5 = st.columns([1, 1, 1, 1, 2])
    
    with col1:
        if not state['is_streaming']:
            if st.button("▶️ Start Streaming", use_container_width=True, key=f"start_{streamer_key}"):
                # Start streaming
                cmd = ['openshell', 'logs', sandbox_id, '--follow']
                streamer = LogStreamer(cmd)
                if streamer.start():
                    state['streamer'] = streamer
                    state['is_streaming'] = True
                    state['paused'] = False
                    st.rerun()
                else:
                    st.error("Failed to start log stream")
        else:
            if st.button("⏹️ Stop", use_container_width=True, key=f"stop_{streamer_key}"):
                if state['streamer']:
                    state['streamer'].stop()
                state['is_streaming'] = False
                state['paused'] = False
                st.rerun()
    
    with col2:
        if state['is_streaming']:
            if state['paused']:
                if st.button("▶️ Resume", use_container_width=True, key=f"resume_{streamer_key}"):
                    state['paused'] = False
                    st.rerun()
            else:
                if st.button("⏸️ Pause", use_container_width=True, key=f"pause_{streamer_key}"):
                    state['paused'] = True
                    st.rerun()
    
    with col3:
        if st.button("🗑️ Clear", use_container_width=True, key=f"clear_{streamer_key}"):
            if state['streamer']:
                state['streamer'].clear()
            state['logs'] = []
            st.rerun()
    
    with col4:
        show_timestamps = st.checkbox("Timestamps", value=True, key=f"ts_{streamer_key}")
    
    with col5:
        log_level_filter = st.multiselect(
            "Filter Levels",
            options=['ERROR', 'WARNING', 'INFO', 'DEBUG'],
            default=['ERROR', 'WARNING', 'INFO'],
            key=f"filter_{streamer_key}"
        )
    
    # Status indicator
    if state['is_streaming']:
        if state['paused']:
            st.info("⏸️ Stream paused")
        else:
            st.success("▶️ Streaming active")
    else:
        st.warning("⏹️ Stream stopped")
    
    # Log display area
    st.divider()
    
    # Get current logs
    if state['is_streaming'] and state['streamer'] and not state['paused']:
        state['logs'] = state['streamer'].get_logs(max_lines)
        
        # Auto-refresh
        if auto_refresh:
            time.sleep(refresh_interval)
            st.rerun()
    
    # Filter and format logs
    filtered_logs = []
    for line in state['logs']:
        level = parse_log_level(line)
        if level in log_level_filter or (level == 'DEFAULT' and 'INFO' in log_level_filter):
            formatted = format_log_line(line, show_timestamps)
            filtered_logs.append(formatted)
    
    # Display logs in text area
    if filtered_logs:
        log_text = "\n".join(filtered_logs)
        st.text_area(
            "Log Output",
            value=log_text,
            height=400,
            key=f"log_display_{streamer_key}",
            help="Real-time log output from the sandbox"
        )
    else:
        st.info("No logs available. Start streaming to see output.")
    
    # Export controls
    st.divider()
    col1, col2 = st.columns([1, 1])
    
    with col1:
        if state['logs']:
            log_export = "\n".join(state['logs'])
            st.download_button(
                "⬇️ Download Logs",
                data=log_export,
                file_name=f"{sandbox_id}_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain",
                use_container_width=True,
                key=f"download_{streamer_key}"
            )
    
    with col2:
        if st.button("📋 Copy to Clipboard", use_container_width=True, key=f"copy_{streamer_key}"):
            if state['logs']:
                log_text = "\n".join(state['logs'])
                st.code(log_text)
                st.success("Logs displayed above - select and copy")
    
    # Statistics
    if state['logs']:
        st.divider()
        error_count = sum(1 for line in state['logs'] if 'ERROR' in line.upper())
        warning_count = sum(1 for line in state['logs'] if 'WARNING' in line.upper())
        
        cols = st.columns(3)
        with cols[0]:
            st.metric("Total Lines", len(state['logs']))
        with cols[1]:
            st.metric("Errors", error_count, delta_color="inverse")
        with cols[2]:
            st.metric("Warnings", warning_count, delta_color="inverse")

def render_log_viewer_simple(
    openshell_service,
    sandbox_id: str,
    lines: int = 100
):
    """Render a simple log viewer (non-streaming)."""
    
    # Load logs
    with st.spinner("Loading logs..."):
        logs = openshell_service.get_sandbox_logs(sandbox_id, lines)
    
    if not logs:
        st.info("No logs available for this sandbox.")
        return
    
    # Display controls
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        show_timestamps = st.checkbox("Show Timestamps", value=True, key=f"simple_ts_{sandbox_id}")
    
    with col2:
        if st.button("🔄 Refresh", key=f"simple_refresh_{sandbox_id}"):
            st.rerun()
    
    with col3:
        log_lines = st.slider("Lines", min_value=10, max_value=1000, value=lines, step=10, key=f"simple_lines_{sandbox_id}")
    
    # Format and display
    log_lines_list = logs.split('\n') if isinstance(logs, str) else []
    
    if show_timestamps:
        formatted_logs = [format_log_line(line) for line in log_lines_list]
    else:
        formatted_logs = [f"{LOG_COLORS[parse_log_level(line)]} {line}" for line in log_lines_list]
    
    log_text = "\n".join(formatted_logs)
    
    st.text_area(
        "Log Output",
        value=log_text,
        height=400,
        key=f"simple_display_{sandbox_id}"
    )
    
    # Download button
    st.download_button(
        "⬇️ Download Logs",
        data=logs,
        file_name=f"{sandbox_id}_logs.txt",
        mime="text/plain",
        key=f"simple_download_{sandbox_id}"
    )
