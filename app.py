
import streamlit as st
import pandas as pd
from datetime import date

from tcp_client import send_request
from udp_client import send_status
from ai_agent import generate_study_plan
import database
import network_monitor


# -----------------------------------
# PAGE CONFIGURATION
# -----------------------------------

st.set_page_config(
    page_title="AI Smart Study Planner",
    page_icon="📚",
    layout="wide"
)


# -----------------------------------
# APPLICATION HEADER
# -----------------------------------

st.title("📚 AI Smart Study Planner")

st.write(
    "Organize your assignments, manage deadlines, "
    "and plan your study time."
)


# -----------------------------------
# SIDEBAR NAVIGATION
# -----------------------------------

menu = st.sidebar.selectbox(
    "Choose a section",
    [
        "Dashboard",
        "Add Tasks",
        "Study Plan",
        "Network Monitoring",
        "About Project"
    ]
)


# -----------------------------------
# DASHBOARD
# -----------------------------------

if menu == "Dashboard":

    st.header("🎓 Student Dashboard")

    try:

        response = send_request({"action": "get_tasks"})

        if response["success"]:

            network_monitor.log_activity(
                "TCP",
                "Retrieved assignments from database"
            )

            tasks = response["tasks"]

            total_tasks = len(tasks)

            completed_tasks = sum(
                1 for task in tasks
                if task[6] == "Completed"
            )

            pending_tasks = total_tasks - completed_tasks

            col1, col2, col3 = st.columns(3)

            col1.metric("Total Tasks", total_tasks)
            col2.metric("Completed", completed_tasks)
            col3.metric("Pending", pending_tasks)

            st.divider()

            st.subheader("📋 Your Assignments")

            if tasks:

                for task in tasks:

                    task_id = task[0]
                    task_name = task[1]
                    subject = task[2]
                    deadline = task[3]
                    priority = task[4]
                    description = task[5]
                    status = task[6]

                    with st.container(border=True):

                        st.subheader(task_name)

                        st.write("**Subject:**", subject)
                        st.write("**Deadline:**", deadline)
                        st.write("**Priority:**", priority)
                        st.write("**Description:**", description)

                        if status == "Completed":

                            st.success("Completed")

                        else:

                            st.warning("Pending")

                            due_date = date.fromisoformat(deadline)

                            days_left = (
                                due_date - date.today()
                            ).days

                            if days_left < 0:

                                st.error("This task is overdue!")

                            elif days_left == 0:

                                st.warning("Deadline is today!")

                            elif days_left <= 3:

                                st.warning(
                                    f"Deadline approaching: "
                                    f"{days_left} days left."
                                )

                            if st.button(
                                "Mark as Completed",
                                key=f"complete_{task_id}"
                            ):

                                update_response = send_request({
                                    "action": "update_status",
                                    "task_id": task_id,
                                    "status": "Completed"
                                })

                                if update_response["success"]:

                                    network_monitor.log_activity(
                                        "TCP",
                                        f"Assignment completed: {task_name}"
                                    )

                                    st.success(
                                        "Task completed successfully!"
                                    )

                                    # Automatically update AI study plan

                                    try:

                                        generate_study_plan()

                                        st.success(
                                            "AI study plan automatically updated!"
                                        )

                                    except Exception as error:

                                        st.warning(
                                            f"Study plan update failed: {error}"
                                        )

                                    st.rerun()

                                else:

                                    st.error(
                                        update_response["message"]
                                    )

            else:

                st.info("No assignments added yet.")

        else:

            st.error(response["message"])

    except Exception as error:

        st.error(f"TCP connection error: {error}")

        st.info(
            "Please check whether your TCP server is running."
        )


# -----------------------------------
# ADD TASKS
# -----------------------------------

elif menu == "Add Tasks":

    st.header("📝 Add a New Assignment")

    with st.form("task_form"):

        task_name = st.text_input("Assignment Name")

        subject = st.text_input("Subject")

        deadline = st.date_input(
            "Deadline",
            min_value=date.today()
        )

        priority = st.selectbox(
            "Priority",
            ["High", "Medium", "Low"]
        )

        description = st.text_area("Description")

        submitted = st.form_submit_button("Add Task")

        if submitted:

            if task_name.strip() and subject.strip():

                request = {
                    "action": "add_task",
                    "task": task_name,
                    "subject": subject,
                    "deadline": str(deadline),
                    "priority": priority,
                    "description": description
                }

                try:

                    response = send_request(request)

                    if response["success"]:

                        network_monitor.log_activity(
                            "TCP",
                            f"Assignment added: {task_name}"
                        )

                        st.success(response["message"])

                        # UDP monitoring

                        udp_response = send_status(
                            f"New assignment added: {task_name}"
                        )

                        network_monitor.log_activity(
                            "UDP",
                            f"New assignment added: {task_name}"
                        )

                        st.info(
                            f"UDP Monitoring: {udp_response}"
                        )

                        # Automatically update AI study plan

                        try:

                            generate_study_plan()

                            st.success(
                                "AI study plan automatically updated!"
                            )

                        except Exception as error:

                            st.warning(
                                f"Task saved, but study plan update failed: {error}"
                            )

                    else:

                        st.error(response["message"])

                except Exception as error:

                    st.error(f"Connection error: {error}")

            else:

                st.error(
                    "Please enter the assignment name and subject."
                )


# -----------------------------------
# AI STUDY PLAN
# -----------------------------------

elif menu == "Study Plan":

    st.header("📅 Your AI Study Plan")

    st.write(
        "Your AI agent analyzes assignments, "
        "makes recommendations and saves your study plan."
    )

    if st.button("🤖 Generate New Study Plan"):

        try:

            plan = generate_study_plan()

            network_monitor.log_activity(
                "TCP",
                "AI agent generated a new study plan"
            )

            if plan:

                st.success(
                    "Your new AI study plan is ready!"
                )

                st.subheader("🤖 AI Agent Analysis")

                for index, task in enumerate(plan, start=1):

                    with st.container(border=True):

                        st.subheader(
                            f"{index}. {task['task']}"
                        )

                        st.write(
                            "**Priority:**",
                            task["priority"]
                        )

                        st.write(
                            "**Days remaining:**",
                            task["days_left"]
                        )

                        st.write(
                            "**AI Priority Score:**",
                            task["score"]
                        )

                        st.info(
                            f"AI Recommendation: {task['reason']}"
                        )

            else:

                st.info(
                    "No pending assignments found. "
                    "Your study plan is clear!"
                )

        except Exception as error:

            st.error(
                f"Error generating study plan: {error}"
            )

    # Display previously saved study plan

    st.divider()

    st.subheader("💾 Saved Study Plan")

    try:

        saved_plan = database.get_saved_study_plan()

        if saved_plan:

            for task in saved_plan:

                position = task[5]
                task_name = task[1]
                priority = task[2]
                days_left = task[3]
                score = task[4]

                with st.container(border=True):

                    st.write(f"**{position}. {task_name}**")

                    st.write("Priority:", priority)

                    st.write(
                        "Days remaining:",
                        days_left
                    )

                    st.write(
                        "AI Priority Score:",
                        score
                    )

        else:

            st.info(
                "No saved study plan yet. "
                "Generate a new plan to get started."
            )

    except Exception as error:

        st.error(
            f"Could not load saved study plan: {error}"
        )


# -----------------------------------
# NETWORK MONITORING
# -----------------------------------

elif menu == "Network Monitoring":

    st.header("🌐 Network Activity Monitoring")

    st.write(
        "Monitor TCP and UDP communication "
        "activities in your application."
    )

    # Network system information

    st.subheader("🖥️ Network System Information")

    col1, col2 = st.columns(2)

    with col1:

        st.info("""
        **TCP Server**

        IP Address: 127.0.0.1

        Port: 5000

        Purpose: Assignment management and database communication.
        """)

    with col2:

        st.info("""
        **UDP Server**

        IP Address: 127.0.0.1

        Port: 6000

        Purpose: Lightweight network monitoring messages.
        """)

    st.divider()

    # Retrieve permanent logs from SQLite

    logs = network_monitor.get_network_logs()

    # Calculate network statistics

    tcp_count = sum(
        1 for log in logs
        if log["protocol"] == "TCP"
    )

    udp_count = sum(
        1 for log in logs
        if log["protocol"] == "UDP"
    )

    # Display statistics

    col1, col2, col3 = st.columns(3)

    col1.metric("Total Activities", len(logs))
    col2.metric("TCP Activities", tcp_count)
    col3.metric("UDP Activities", udp_count)

    st.divider()

    # Network protocol usage chart

    st.subheader("📊 Network Protocol Usage")

    chart_data = pd.DataFrame({
        "Protocol": ["TCP", "UDP"],
        "Activities": [tcp_count, udp_count]
    })

    st.bar_chart(
        chart_data,
        x="Protocol",
        y="Activities",
        color="Protocol"
    )

    st.divider()

    # Network activity history

    st.subheader("📋 Network Activity History")

    # Clear history button

    if st.button("🗑️ Clear Network History"):

        network_monitor.clear_network_logs()

        st.success("Network history cleared!")

        st.rerun()

    st.divider()

    if logs:

        for log in logs:

            with st.container(border=True):

                st.write("**Time:**", log["time"])

                st.write(
                    "**Protocol:**",
                    log["protocol"]
                )

                st.write(
                    "**Activity:**",
                    log["message"]
                )

                st.success(log["status"])

    else:

        st.info(
            "No network activity recorded yet. "
            "Use the Dashboard or Add Tasks page first."
        )


# -----------------------------------
# ABOUT PROJECT
# -----------------------------------

elif menu == "About Project":

    st.header("📚 About AI Smart Study Planner")

    st.write(
        "AI Smart Study Planner is an intelligent "
        "assignment management application designed "
        "to help students organize their academic work."
    )

    st.divider()

    # Project objectives

    st.subheader("🎯 Project Objectives")

    st.write("""
    - Manage academic assignments.
    - Track assignment deadlines.
    - Prioritize tasks based on urgency.
    - Generate AI-based study recommendations.
    - Monitor TCP and UDP network communication.
    - Store information permanently using SQLite.
    """)

    st.divider()

    # Technologies used

    st.subheader("🛠️ Technologies Used")

    technologies = {
        "Python": "Main programming language",
        "Streamlit": "User interface",
        "SQLite": "Database management",
        "TCP": "Reliable client-server communication",
        "UDP": "Lightweight network monitoring messages",
        "Agentic AI": "Task analysis and study-plan generation"
    }

    for technology, purpose in technologies.items():

        with st.container(border=True):

            st.write(f"**{technology}**")

            st.caption(purpose)

    st.divider()

    # Agentic AI workflow

    st.subheader("🤖 Agentic AI Workflow")

    st.write("""
    1. Observe: Retrieve student assignments.
    2. Analyze: Check deadlines and priorities.
    3. Decide: Calculate task priority scores.
    4. Act: Generate and save a study plan.
    5. Report: Display recommendations to the student.
    """)

    st.divider()

    # Network architecture

    st.subheader("🌐 Network Architecture")

    st.write("""
    TCP Client → TCP Server → SQLite Database

    UDP Client → UDP Server → Monitoring Response

    AI Agent → Assignment Analysis → Study Plan
    """)

    st.success(
        "AI Smart Study Planner - Project Overview"
    )
