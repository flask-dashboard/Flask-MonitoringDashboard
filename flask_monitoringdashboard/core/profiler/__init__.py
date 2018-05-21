import threading

from flask_monitoringdashboard.core.profiler.profileThread import ProfileThread


def start_profile_thread(endpoint):
    """Start a profiler thread."""
    current_thread = threading.current_thread().ident
    profile_thread = ProfileThread(thread_to_monitor=current_thread, endpoint=endpoint)
    profile_thread.start()
    return profile_thread
