
from ai_agent import generate_study_plan

plan = generate_study_plan()

print("\nAI STUDY PLAN")
print("-------------------------")

if not plan:
    print("No pending assignments found.")

else:
    for index, task in enumerate(plan, start=1):
        print(f"\n{index}. {task['task']}")
        print(f"Priority: {task['priority']}")
        print(f"Days remaining: {task['days_left']}")
        print(f"AI Priority Score: {task['score']}")
        print(f"AI Recommendation: {task['reason']}")

    print("\nStudy plan saved successfully!")
