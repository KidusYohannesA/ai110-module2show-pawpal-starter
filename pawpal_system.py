from datetime import datetime, timedelta


class Task:
    pet_task_map = {}  # {Pet: [Task]} — central registry

    def __init__(self, title, description="", duration_minutes=0, priority="medium",
                 frequency="once", start_time=None, status="pending", pet=None):
        """Initialize a task with scheduling details and optional pet assignment."""
        self.title = title
        self.description = description
        self.duration_minutes = duration_minutes
        self.priority = priority  # "low", "medium", "high"
        self.frequency = frequency  # "once", "daily", "weekly", "monthly"
        self.start_time = start_time  # "YYYY-MM-DD HH:MM"
        self.status = status  # "pending", "in_progress", "completed"
        self.pet = pet

        if pet is not None:
            pet.add_task(self)

    def update_time(self, start_time):
        """Set a new start time for the task."""
        self.start_time = start_time

    def get_end_time(self):
        """Calculate and return the end time based on start time and duration."""
        if self.start_time is None:
            return None
        start = datetime.strptime(self.start_time, "%Y-%m-%d %H:%M")
        return (start + timedelta(minutes=self.duration_minutes)).strftime("%Y-%m-%d %H:%M")

    def get_duration(self):
        """Return the task duration in minutes."""
        return self.duration_minutes

    def mark_complete(self):
        """Mark the task as completed."""
        self.status = "completed"

    @classmethod
    def clear(cls):
        """Reset the central pet-task registry."""
        cls.pet_task_map = {}

    def __repr__(self):
        """Return a string representation of the task."""
        return f"Task('{self.title}', priority={self.priority}, frequency={self.frequency}, status={self.status})"


class Pet:
    def __init__(self, name, species, breed="", age=0):
        """Initialize a pet with its details and an empty task list."""
        self.name = name
        self.species = species
        self.breed = breed
        self.age = age
        self.tasks = []
        Task.pet_task_map[self.name] = self.tasks

    def add_task(self, task):
        """Add a task to this pet and set the task's pet reference."""
        self.tasks.append(task)
        task.pet = self

    def remove_task(self, task):
        """Remove a task from this pet's task list."""
        self.tasks.remove(task)

    def get_tasks(self):
        """Return the list of tasks assigned to this pet."""
        return self.tasks

    def __repr__(self):
        """Return a string representation of the pet."""
        return f"Pet('{self.name}', species={self.species})"


class Schedule:
    def __init__(self, week_start_date, pets):
        """Initialize a schedule with a start date and a reference to the owner's pets."""
        self.week_start_date = week_start_date  # "YYYY-MM-DD"
        self._pets = pets  # reference to Owner's pets list

    def _all_tasks(self):
        """Aggregate and return all tasks from all pets."""
        all_tasks = []
        for pet in self._pets:
            all_tasks.extend(pet.get_tasks())
        return all_tasks

    def add_task(self, task):
        """Add a task to its assigned pet if not already present."""
        if task.pet is not None and task not in task.pet.tasks:
            task.pet.add_task(task)

    def remove_task(self, task):
        """Remove a task from its assigned pet."""
        if task.pet is not None:
            task.pet.remove_task(task)

    def edit_task_time(self, task, start_time):
        """Update a task's start time if it exists in the schedule."""
        if task in self._all_tasks():
            task.update_time(start_time)

    def get_tasks_for_pet(self, pet):
        """Return a copy of all tasks for a specific pet."""
        return list(pet.get_tasks())

    def get_weekly_view(self):
        """Return all tasks across all pets for the week."""
        return self._all_tasks()

    def get_daily_view(self, date):
        """Return all tasks scheduled for a specific date."""
        return [t for t in self._all_tasks() if t.start_time and t.start_time.startswith(date)]

    def schedule_tasks(self, date, start_hour=8):
        """Sort tasks by priority and assign sequential start times."""
        priority_order = {"high": 0, "medium": 1, "low": 2}
        sorted_tasks = sorted(self._all_tasks(), key=lambda t: priority_order.get(t.priority, 1))

        current_time = datetime.strptime(f"{date} {start_hour:02d}:00", "%Y-%m-%d %H:%M")
        for task in sorted_tasks:
            task.update_time(current_time.strftime("%Y-%m-%d %H:%M"))
            current_time += timedelta(minutes=task.duration_minutes)

        return sorted_tasks

    def get_explanation(self):
        """Return a human-readable list explaining each scheduled task."""
        explanations = []
        for i, task in enumerate(self.get_weekly_view(), 1):
            if task.start_time is None:
                continue
            pet_name = task.pet.name if task.pet else "Unassigned"
            explanations.append(
                f"{i}. {task.title} ({pet_name}) — {task.start_time} to {task.get_end_time()} | "
                f"Priority: {task.priority}, Frequency: {task.frequency}"
            )
        return explanations

    def __repr__(self):
        """Return a string representation of the schedule."""
        return f"Schedule(week_start='{self.week_start_date}', tasks={len(self._all_tasks())})"


class Owner:
    def __init__(self, name, email="", phone=""):
        """Initialize an owner with contact info, an empty pet list, and a schedule."""
        self.name = name
        self.email = email
        self.phone = phone
        self.pets = []
        self.schedule = Schedule(datetime.today().strftime("%Y-%m-%d"), self.pets)

    def add_pet(self, pet):
        """Add a pet to the owner's pet list."""
        self.pets.append(pet)

    def remove_pet(self, pet):
        """Remove a pet from the owner's pet list."""
        self.pets.remove(pet)

    def add_task(self, task):
        """Add a task to its assigned pet if not already present."""
        if task.pet is not None and task not in task.pet.tasks:
            task.pet.add_task(task)

    def get_all_tasks(self):
        """Return all tasks across all of the owner's pets."""
        all_tasks = []
        for pet in self.pets:
            all_tasks.extend(pet.get_tasks())
        return all_tasks

    def get_schedule(self):
        """Return the owner's schedule."""
        return self.schedule

    def __repr__(self):
        """Return a string representation of the owner."""
        return f"Owner('{self.name}', pets={len(self.pets)})"
