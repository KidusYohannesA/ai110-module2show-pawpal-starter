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
    st.write("Your pets:")
    for pet in owner.pets:
        st.write(f"- {pet.name} ({pet.species})")
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
        st.write("Current tasks:")
        for t in all_tasks:
            st.write(f"- **{t.title}** ({t.pet.name}) — {t.duration_minutes} min, "
                     f"Priority: {t.priority}, Frequency: {t.frequency}")
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
        explanation = schedule.get_explanation()

        st.write(f"**Schedule for {owner.name} — {today}**")
        for line in explanation:
            st.write(line)
else:
    st.info("Add at least one pet and one task to generate a schedule.")
