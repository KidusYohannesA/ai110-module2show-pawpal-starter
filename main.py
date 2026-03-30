from pawpal_system import Task, Pet, Schedule, Owner

owner = Owner("Jordan", email="jordan@email.com", phone="555-1234")

mochi = Pet("Mochi", "dog", breed="Shiba Inu", age=3)
luna = Pet("Luna", "cat", breed="Siamese", age=5)

owner.add_pet(mochi)
owner.add_pet(luna)

Task("Morning walk", description="Walk around the park", duration_minutes=30,
     priority="high", frequency="daily", pet=mochi)

Task("Feeding", description="Wet food and fresh water", duration_minutes=15,
     priority="high", frequency="daily", pet=luna)

Task("Grooming", description="Brush fur and check ears", duration_minutes=20,
     priority="medium", frequency="weekly", pet=mochi)

Task("Play session", description="Interactive toy time", duration_minutes=25,
     priority="low", frequency="daily", pet=luna)

today = owner.schedule.week_start_date
schedule = owner.get_schedule()
schedule.schedule_tasks(today)

print(f"=== Today's Schedule for {owner.name} ({today}) ===\n")
for line in schedule.get_explanation():
    print(line)

# --- Conflict demo: manually set two tasks to the same time ---
Task("Vet checkup", description="Annual exam", duration_minutes=45,
     priority="high", frequency="once", start_time=f"{today} 09:00", pet=mochi)

Task("Nail trimming", description="Clip nails", duration_minutes=30,
     priority="medium", frequency="monthly", start_time=f"{today} 09:15", pet=luna)

print("\n=== Conflict Detection ===\n")
conflicts = schedule.detect_conflicts()
if conflicts:
    for warning in conflicts:
        print(f"⚠{warning}")
else:
    print("No scheduling conflicts found.")
