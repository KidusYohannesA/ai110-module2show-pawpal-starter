import streamlit as st
from datetime import datetime
from pawpal_system import Task, Pet, Owner

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to **PawPal+**, your pet care planning assistant.
Add your pets, assign tasks, and generate a priority-based daily schedule.
"""
)

# --- Session State Initialization ---
if "owner" not in st.session_state:
    st.session_state.owner = Owner("Owner")

owner = st.session_state.owner

# --- Owner Setup ---
st.subheader("Owner")
owner_name = st.text_input("Owner name", value=owner.name)
owner.name = owner_name

# --- Add Pet ---
st.divider()
st.subheader("Add a Pet")

col1, col2 = st.columns(2)
with col1:
    pet_name = st.text_input("Pet name", value="Mochi")
with col2:
    species = st.selectbox("Species", ["dog", "cat", "other"])

if st.button("Add pet"):
    if pet_name.strip():
        pet = Pet(pet_name.strip(), species)
        owner.add_pet(pet)
        st.success(f"Added {pet_name} the {species}!")
    else:
        st.warning("Please enter a pet name.")

if owner.pets:
    st.write("**Your Pets**")
    pet_table = "| Name | Species |\n|---|---|\n"
    for pet in owner.pets:
        pet_table += f"| {pet.name} | {pet.species} |\n"
    st.markdown(pet_table)
else:
    st.info("No pets yet. Add one above.")

# --- Add Task ---
st.divider()
st.subheader("Add a Task")

if owner.pets:
    pet_names = [pet.name for pet in owner.pets]
    selected_pet_name = st.selectbox("Assign to pet", pet_names)
    selected_pet = next(p for p in owner.pets if p.name == selected_pet_name)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        task_title = st.text_input("Task title", value="Morning walk")
    with col2:
        duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
    with col3:
        priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)
    with col4:
        frequency = st.selectbox("Frequency", ["once", "daily", "weekly", "monthly"], index=0)

    if st.button("Add task"):
        task = Task(task_title, duration_minutes=int(duration), priority=priority,
                    frequency=frequency, pet=selected_pet)
        st.success(f"Added '{task_title}' to {selected_pet_name}!")

    all_tasks = owner.get_all_tasks()
    if all_tasks:
        schedule = owner.get_schedule()
        sorted_tasks = schedule.get_tasks_by_time()
        st.write("**Current Tasks** (sorted by scheduled time)")
        task_table = "| Task | Pet | Duration (min) | Priority | Frequency | Scheduled Time |\n"
        task_table += "|---|---|---|---|---|---|\n"
        for t in sorted_tasks:
            time_info = t.start_time.strftime("%Y-%m-%d %H:%M") if t.start_time else "Unscheduled"
            task_table += (f"| {t.title} | {t.pet.name} | {t.duration_minutes} | "
                           f"{t.priority.capitalize()} | {t.frequency.capitalize()} | {time_info} |\n")
        st.markdown(task_table)

        conflicts = schedule.detect_conflicts()
        if conflicts:
            for warning in conflicts:
                st.warning(warning)
        else:
            st.success("No task conflicts detected.")
    else:
        st.info("No tasks yet. Add one above.")
else:
    st.info("Add a pet first before creating tasks.")

# --- Generate Schedule ---
st.divider()
st.subheader("Generate Schedule")

if owner.pets and owner.get_all_tasks():
    today = datetime.today().strftime("%Y-%m-%d")
    if st.button("Generate schedule"):
        schedule = owner.get_schedule()
        sorted_tasks = schedule.schedule_tasks(today)

        st.write(f"**Schedule for {owner.name} — {today}**")
        sched_table = "| # | Task | Pet | Start | End | Duration (min) | Priority | Frequency |\n"
        sched_table += "|---|---|---|---|---|---|---|---|\n"
        for i, task in enumerate(sorted_tasks, 1):
            pet_name = task.pet.name if task.pet else "Unassigned"
            start_str = task.start_time.strftime("%H:%M") if task.start_time else "N/A"
            end_str = task.get_end_time().strftime("%H:%M") if task.start_time else "N/A"
            sched_table += (f"| {i} | {task.title} | {pet_name} | {start_str} | {end_str} | "
                            f"{task.duration_minutes} | {task.priority.capitalize()} | "
                            f"{task.frequency.capitalize()} |\n")
        st.markdown(sched_table)

        conflicts = schedule.detect_conflicts()
        if conflicts:
            st.subheader("Conflict Warnings")
            for warning in conflicts:
                st.warning(warning)
        else:
            st.success("No scheduling conflicts detected!")
else:
    st.info("Add at least one pet and one task to generate a schedule.")
