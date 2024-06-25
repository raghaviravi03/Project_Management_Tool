import streamlit as st
from .database import get_users_collection
from .helpers import create_new_user, create_task, find_tasks_by_status, update_task_status, login, change_password, admin_user_exists, get_task_collection, get_user_names_from_emails
from datetime import datetime
from pymongo import DESCENDING
import pytz
from bson import ObjectId
import time

def truncate_text(text, max_length):
    """Truncate text and append '...' if it exceeds the max_length."""
    if len(text) > max_length:
        return text[:max_length] + "..."
    else:
        return text

def display_task(task, email=None, company_name=None, is_admin=False, allow_status_change=True, task_index=0):
    status_color = {
        "pending": "red",
        "in progress": "orange",
        "completed": "green",
        "cancelled": "black"
    }
    priority_color = {
        "High": "red",
        "Moderate": "orange",
        "Low": "green"
    }
    
    # Fetch user names for assigned users and admins
    assigned_to_names = get_user_names_from_emails(task['assigned_to'], company_name)
    task_admin_names = get_user_names_from_emails(task.get('task_admin', []), company_name)
    
    col1, col2, col3, col4, col5, col6, col7, col8, col9, col10 = st.columns([1, 3, 3, 1, 1, 1, 1, 1, 2, 2])
    with col1:
        truncated_name = truncate_text(task['name'], 30)
        st.markdown(f"**Task**: {truncated_name}")
    with col2:
        st.markdown(f"**Assigned to**: {', '.join(assigned_to_names)}")
    with col3:
        task_admin = ', '.join(task_admin_names) if task_admin_names else 'Not Set'
        st.markdown(f"**Admin**: {task_admin}")
    with col4:
        st.markdown(f'**Status**: <p style="color:{status_color[task["status"]]}">{task["status"]}</p>', unsafe_allow_html=True)
    with col5:
        st.markdown(f'**Priority**: <p style="color:{priority_color[task["priority"]]}">{task["priority"]}</p>', unsafe_allow_html=True)
    with col6:
        days_passed = (datetime.utcnow() - task['created_at']).days
        st.markdown(f"**Days passed**: {days_passed}")
    with col7:
        due_date = task.get('due_date')
        if due_date:
            due_date_str = due_date.strftime('%Y-%m-%d')
            st.markdown(f"**Due Date**: {due_date_str}")
        else:
            st.markdown(f"**Due Date**: Not Set")
    with col8:
        st.empty()
    if email:
        unique_key = f"{task['_id']}-{email}-{task_index:05d}-{task['created_at'].isoformat()}-{time.time()}"
        with col9:
            view_update_btn = st.button("View/Update", key=f"view-update-{unique_key}")
        if view_update_btn:
            st.write('## Clicked')
            st.session_state.selected_task_id = str(task['_id'])
            st.session_state.company_name = company_name
            st.session_state.page = "Task Details"                
            st.experimental_rerun()
    with col10:
        view_subtasks_btn = st.button("View Subtasks", key=f"view-subtasks-{unique_key}")
        if view_subtasks_btn:
            st.session_state.selected_task_id = str(task['_id'])
            st.session_state.company_name = company_name
            st.session_state.page = "Subtask Details"
            st.experimental_rerun()

def display_task_details(email=None):
    st.subheader("Task Details")

    back_to_dashboard = st.button('Back to My Tasks')
    if back_to_dashboard:
        st.session_state.page = "Dashboard"
        st.experimental_rerun()

    task = get_task_collection(st.session_state.company_name).find_one({"_id": ObjectId(st.session_state.selected_task_id)})
    truncated_name = truncate_text(task['name'], 30)

    user = get_users_collection().find_one({"email": email})
    first_name = user['name'].split(' ')[0]
    updated_by = f"{first_name} ({email})"

    with st.container():
        st.write('---')
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Task:**")
            st.markdown("**Assigned to:**")
            st.markdown("**Admin:**")
            st.markdown("**Description:**")
            st.markdown("")
            st.markdown("**Status:**")
            st.markdown("**Priority:**")
            st.markdown("")
            st.markdown("**Dependent Tasks:**")
            st.markdown("**Due Date:**")
        with col2:
            st.markdown(f"{task['name']}")
            st.markdown(f"{', '.join(task['assigned_to'])}")
            task_admin = task.get('task_admin', 'Not Set')
            st.markdown(f"{task_admin}")
            description_expander = st.expander("Description", expanded=False)
            description_expander.markdown(f'<div style="height:250px; overflow:auto;border:1px solid black;padding:10px;">{task["description"]}</div>', unsafe_allow_html=True)
            st.markdown(f"{task['status'].capitalize()}")
            st.markdown(f"{task['priority']}")
            dependent_tasks_expander = st.expander("Dependent Tasks", expanded=False)
            if task["dependent_tasks"]:
                dependent_tasks = get_task_collection(st.session_state.company_name).find({"name": {"$in": task["dependent_tasks"]}})
                dependent_tasks_info = [(t["name"], t["assigned_to"]) for t in dependent_tasks]
                dependent_tasks_expander.markdown('<br>'.join(f'{name} (Assigned to: {assigned_to})' for name, assigned_to in dependent_tasks_info), unsafe_allow_html=True)
            else:
                dependent_tasks_expander.markdown('No dependent tasks.')
            due_date = task.get('due_date')
            if due_date:
                st.markdown(f"{due_date.strftime('%Y-%m-%d')}")
            else:
                st.markdown(f"Not Set")
        st.write('---')

        st.subheader("Subtasks")
        if task.get("subtasks"):
            for idx, subtask in enumerate(task["subtasks"]):
                display_subtask(subtask, task['_id'], idx, email)
                
        user_mapping = {f"{user['name']} ({user['email']})": user['email'] for user in get_users_collection().find({"company_name": st.session_state.company_name})}
        subtask_name = st.text_input("Subtask Name", key="subtask_name")
        subtask_description = st.text_area("Subtask Description", key="subtask_description")
        subtask_assigned_to_keys = st.multiselect("Assign Subtask To", list(user_mapping.keys()), key="subtask_assigned_to")
        subtask_assigned_to = [user_mapping[key] for key in subtask_assigned_to_keys]
        subtask_admin_keys = st.multiselect("Subtask Admin", list(user_mapping.keys()), key="subtask_admin")
        subtask_admin = [user_mapping[key] for key in subtask_admin_keys]
        subtask_due_date = st.date_input("Subtask Due Date", key="subtask_due_date", min_value=datetime.now().date())
        subtask_priority = st.selectbox("Subtask Priority", ["High", "Moderate", "Low"], key="subtask_priority")
        subtask_status = st.selectbox("Subtask Status", ["pending", "in progress", "completed", "cancelled"], key="subtask_status")
        create_subtask_btn = st.button("Create Subtask", key="create_subtask_btn")

        if create_subtask_btn:
            subtask = {
                "name": subtask_name,
                "description": subtask_description,
                "assigned_to": subtask_assigned_to,
                "task_admin": subtask_admin,
                "status": subtask_status,
                "priority": subtask_priority,
                "created_at": datetime.utcnow(),
                "due_date": datetime.combine(subtask_due_date, datetime.min.time()),  # Convert to datetime
                "parent_task_id": task["_id"],
                "dependent_tasks": []
            }
            get_task_collection(st.session_state.company_name).update_one(
                {"_id": task["_id"]},
                {"$push": {"subtasks": subtask}}
            )
            st.success("Subtask created successfully!")
            st.experimental_rerun()

        if email and task["status"] not in ["completed", "cancelled"]:
            unique_key = f"{task['_id']}-{email}"
            with st.form(key=f"update_form-{unique_key}", clear_on_submit=True):
                row1_col1, row1_col2 = st.columns([2,2])
                with row1_col1:
                    status_options = ["Pending", "In Progress", "Completed", "Cancelled"]
                    selected_status = st.selectbox(f"Update status for {truncated_name}", status_options, key=f"status-{unique_key}")
                    new_status = selected_status.lower()
                with row1_col2:
                    minutes_worked = st.number_input("Minutes worked", min_value=0, step=1, format="%i", key=f"minutes-{unique_key}")
                comment = st.text_area(f"Add comment for {truncated_name}:",key=f"comment-{unique_key}")
                update_task_btn = st.form_submit_button("Update")
            
            if update_task_btn:
                if not comment.strip() and minutes_worked != 0:
                    st.error(f"Please provide a reason for updating the minutes worked.")
                else:
                    update_task_status(str(task["_id"]), new_status, st.session_state.company_name, comment.strip() if comment else None, minutes_worked, updated_by)
                    if new_status != task["status"]:
                        task["status"] = new_status
                    st.success("Task updated successfully!")
        elif task["status"] in ["completed", "cancelled"]:
            st.info("This task is already completed or cancelled and cannot be updated.")

    for status_update in task.get('status_updates', []):
        with st.container():
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.markdown(f"**Comment**: {status_update['comment']}")
            with col2:
                st.markdown(f"**Minutes Worked**: {status_update['minutes_worked']}")
            with col3:
                st.markdown(f"**Time (IST)**: {status_update['timestamp'].astimezone(pytz.timezone('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S')}")
            with col4:
                st.markdown(f"**Updated By**: {status_update['updated_by']}")
            st.write('---')
            
def display_subtask(subtask, parent_task_id, subtask_index, email):
    status_color = {
        "pending": "red",
        "in progress": "orange",
        "completed": "green",
        "cancelled": "black"
    }
    priority_color = {
        "High": "red",
        "Moderate": "orange",
        "Low": "green"
    }

    assigned_to_names = get_user_names_from_emails(subtask['assigned_to'], st.session_state.company_name)
    task_admin_names = get_user_names_from_emails(subtask.get('task_admin', []), st.session_state.company_name)

    st.markdown(f"### Subtask {subtask_index + 1}: {subtask['name']}")
    col1, col2, col3, col4, col5, col6 = st.columns([3, 3, 2, 2, 1, 1])
    with col1:
        st.markdown(f"**Assigned to**: {', '.join(assigned_to_names)}")
    with col2:
        subtask_admin = ', '.join(task_admin_names) if task_admin_names else 'Not Set'
        st.markdown(f"**Admin**: {subtask_admin}")
    with col3:
        st.markdown(f'**Status**: <p style="color:{status_color[subtask["status"]]}">{subtask["status"]}</p>', unsafe_allow_html=True)
    with col4:
        st.markdown(f'**Priority**: <p style="color:{priority_color[subtask["priority"]]}">{subtask["priority"]}</p>', unsafe_allow_html=True)
    with col5:
        due_date = subtask.get('due_date')
        if due_date:
            due_date_str = due_date.strftime('%Y-%m-%d')
            st.markdown(f"**Due Date**: {due_date_str}")
        else:
            st.markdown(f"**Due Date**: Not Set")
    with col6:
        st.empty()

    unique_key = f"{parent_task_id}-{subtask['name']}-{email}-{subtask_index:05d}-{subtask['created_at'].isoformat()}"
    with st.form(key=f"update_subtask_form-{unique_key}", clear_on_submit=True):
        row1_col1, row1_col2 = st.columns([2,2])
        with row1_col1:
            status_options = ["Pending", "In Progress", "Completed", "Cancelled"]
            selected_status = st.selectbox(f"Update status for {subtask['name']}", status_options, key=f"status-{unique_key}")
            new_status = selected_status.lower()
        with row1_col2:
            minutes_worked = st.number_input("Minutes worked", min_value=0, step=1, format="%i", key=f"minutes-{unique_key}")
        comment = st.text_area(f"Add comment for {subtask['name']}:", key=f"comment-{unique_key}")
        update_subtask_btn = st.form_submit_button("Update Subtask")
    
    if update_subtask_btn:
        if not comment.strip() and minutes_worked != 0:
            st.error(f"Please provide a reason for updating the minutes worked.")
        else:
            subtask['status'] = new_status
            subtask['minutes_worked'] = minutes_worked
            subtask['comment'] = comment.strip() if comment else None
            get_task_collection(st.session_state.company_name).update_one(
                {"_id": parent_task_id, "subtasks.name": subtask['name']},
                {"$set": {
                    "subtasks.$.status": new_status,
                    "subtasks.$.minutes_worked": minutes_worked,
                    "subtasks.$.comment": comment.strip() if comment else None
                }}
            )
            st.success(f"Subtask '{subtask['name']}' updated successfully!")
            st.experimental_rerun()

def display_subtasks_details(email=None):
    st.subheader("Subtask Details")

    back_to_dashboard = st.button('Back to Task Details')
    if back_to_dashboard:
        st.session_state.page = "Task Details"
        st.experimental_rerun()

    task = get_task_collection(st.session_state.company_name).find_one({"_id": ObjectId(st.session_state.selected_task_id)})
    
    if task.get("subtasks"):
        for idx, subtask in enumerate(task["subtasks"]):
            display_subtask(subtask, task['_id'], idx, email)
    else:
        st.info("No subtasks available.")
