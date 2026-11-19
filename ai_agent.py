
from datetime import date
from tcp_client import send_request
import database


# TOOL 1: Retrieve assignments from the database through TCP
def get_student_tasks():
    response = send_request({"action": "get_tasks"})

    if response["success"]:
        return response["tasks"]

    return []


# TOOL 2: Analyze assignments and make decisions
def analyze_tasks(tasks):
    recommendations = []

    for task in tasks:
        task_name = task[1]
        deadline = task[3]
        priority = task[4]
        status = task[6]

        # Ignore completed assignments
        if status == "Completed":
            continue

        due_date = date.fromisoformat(deadline)
        days_left = (due_date - date.today()).days

        # Calculate priority score
        if priority == "High":
            priority_score = 3
        elif priority == "Medium":
            priority_score = 2
        else:
            priority_score = 1

        # Calculate urgency score
        if days_left <= 0:
            urgency_score = 5
        elif days_left <= 2:
            urgency_score = 4
        elif days_left <= 5:
            urgency_score = 3
        else:
            urgency_score = 1

        # Calculate total score
        total_score = priority_score + urgency_score

        # Explain the recommendation
        if days_left < 0:
            reason = "This assignment is overdue."
        elif days_left == 0:
            reason = "The deadline is today."
        elif days_left <= 2:
            reason = "The deadline is very close."
        elif priority == "High":
            reason = "This assignment has high priority."
        else:
            reason = "This assignment has a lower urgency."

        recommendations.append({
            "task": task_name,
            "days_left": days_left,
            "priority": priority,
            "score": total_score,
            "reason": reason
        })

    # Rank assignments from highest to lowest score
    recommendations.sort(
        key=lambda item: item["score"],
        reverse=True
    )

    return recommendations


# TOOL 3: Save the recommended study plan
def save_study_plan(plan):
    database.save_study_plan(plan)


# AGENT: Retrieve, analyze, decide, save and report
def generate_study_plan():
    tasks = get_student_tasks()

    recommendations = analyze_tasks(tasks)

    save_study_plan(recommendations)

    return recommendations
