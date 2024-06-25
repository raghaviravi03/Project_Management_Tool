import streamlit as st
from streamlit.runtime.scriptrunner.script_run_context import get_script_run_ctx

class SessionState:
    def __init__(self, **kwargs):
        for key, val in kwargs.items():
            setattr(self, key, val)

    def __getitem__(self, key):
        if isinstance(key, str):
            return getattr(self, key, None)
        else:
            raise ValueError(f"Key {key} is not a string.")

    def __setitem__(self, key, val):
        if isinstance(key, str):
            setattr(self, key, val)
        else:
            raise ValueError(f"Key {key} is not a string.")
            
    def __contains__(self, key):
        if isinstance(key, str):
            return hasattr(self, key)
        else:
            raise ValueError(f"Key {key} is not a string.")
    
    def get(self, key, default_value=None):
        if isinstance(key, str):
            return getattr(self, key, default_value)
        else:
            raise ValueError(f"Key {key} is not a string.")
        
    def clear(self):
        for key in list(self.__dict__.keys()):
            del self.__dict__[key]

def get_state(**kwargs):
    ctx = get_script_run_ctx()
    if ctx is None:
        raise RuntimeError("Couldn't get your Streamlit script run context.")

    session = st.session_state

    if '_custom_session_state' not in session:
        default_values = {'logged_in': False, 'user': None, 'is_first_login': False, 'company_name': "", 'page': "Dashboard"}
        default_values.update(kwargs)  # Update default values with kwargs, kwargs will overwrite defaults if there are conflicts
        session._custom_session_state = SessionState(**default_values)

    return session._custom_session_state
    
