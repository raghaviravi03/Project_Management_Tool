import streamlit as st
from src.authentication import display_login_page
from src.admin_dashboard import display_admin_dashboard
from src.user_dashboard import display_user_dashboard
from src.helpers import display_password_change_section
from src.tasks import display_task_details, display_subtasks_details  # Add this import at the top of your file

def initialize_session_state():
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'user' not in st.session_state:
        st.session_state.user = None
    if 'company_name' not in st.session_state:
        st.session_state.company_name = ""  # Initialize with an empty string or appropriate default
    if 'is_first_login' not in st.session_state:
        st.session_state.is_first_login = False
    if 'page' not in st.session_state:
        st.session_state.page = "Login"

def run_app():
    st.set_page_config(page_title="Project Management Tool", layout="wide")
    st.sidebar.image("cese.jpg")
    st.sidebar.image("knowledge.png")
    st.title("Project Management for Office of Hannah Chair")

    initialize_session_state()  # Ensure session state is properly initialized

    # Initialize the new session state variable
    if 'show_create_user_form' not in st.session_state:
        st.session_state.show_create_user_form = False

    # Check query params to handle page navigation
    query_params = st.experimental_get_query_params()
    page = query_params.get("page", [""])[0]

    if not st.session_state.logged_in:
        display_login_page()
    else:
        if st.session_state.company_name == "":
            st.session_state.company_name = st.session_state.user["company_name"]  # Set the company name from the user data

        if st.session_state.user["role"] == "admin":
            if page == "task_details" or st.session_state.page == "Task Details":
                st.session_state.page = "Task Details"
                display_task_details(st.session_state.user["email"])
            elif page == "subtask_details" or st.session_state.page == "Subtask Details":
                st.session_state.page = "Subtask Details"
                display_subtasks_details(st.session_state.user["email"])
            else:
                display_admin_dashboard(st.session_state.user["name"])
        elif st.session_state.user["role"] == "user":
            if page == "task_details" or st.session_state.page == "Task Details":
                st.session_state.page = "Task Details"
                display_task_details(st.session_state.user["email"])
            elif page == "subtask_details" or st.session_state.page == "Subtask Details":
                st.session_state.page = "Subtask Details"
                display_subtasks_details(st.session_state.user["email"])
            else:
                display_user_dashboard(st.session_state.user["name"])

if __name__ == "__main__":
    run_app()
