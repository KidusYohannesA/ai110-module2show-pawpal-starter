from datetime import datetime, timedelta


class Task:
    pet_task_map = {}  # {Pet: [Task]} — central registry

    _TIME_FMT = "%Y-%m-%d %H:%M"

    def __init__(self, title, description="", duration_minutes=0, priority="medium",
                 frequency="once", start_time=None, status="pending", pet=None):
        """Initialize a task with scheduling details and optional pet assignment."""
        self.title = title
        self.description = description
        self.duration_minutes = duration_minutes
        self.priority = priority  # "low", "medium", "high"
        self.frequency = frequency  # "once", "daily", "weekly", "monthly"
        self.start_time = self._parse_time(start_time)  # stored as datetime or None
        self.status = status  # "pending", "in_progress", "completed"
        self.pet = pet

        if pet is not None:
            pet.add_task(self)

    @classmethod
    def _parse_time(cls, value):
        """Convert a string or datetime to a datetime object, or return None."""
        if value is None or isinstance(value, datetime):
            return value
        return datetime.strptime(value, cls._TIME_FMT)

    def update_time(self, start_time):
        """Set a new start time for the task (accepts string or datetime)."""
        self.start_time = self._parse_time(start_time)

    def get_end_time(self):
        """Calculate and return the end time based on start time and duration."""
        if self.start_time is None:
            return None
        return self.start_time + timedelta(minutes=self.duration_minutes)

    def get_duration(self):
        """Return the task duration in minutes."""
        return self.duration_minutes

    _FREQUENCY_DELTAS = {
        "daily": timedelta(days=1),
        "weekly": timedelta(weeks=1),
        "monthly": timedelta(days=30),
    }

    def mark_complete(self):
        """Mark the task as completed. If it recurs, create the next occurrence on the same pet.

        For recurring tasks (daily, weekly, monthly), a new pending Task is created
        with its start_time advanced by the corresponding delta from _FREQUENCY_DELTAS.
        The new task is automatically added to the same pet.

        Returns:
            Task: The next occurrence if the task recurs, or None for one-time tasks.
        """
        self.status = "completed"
        delta = self._FREQUENCY_DELTAS.get(self.frequency)
        if delta is None or self.pet is None:
            return None
        next_time = self.start_time + delta if self.start_time else None
        next_task = Task(
            title=self.title,
            description=self.description,
            duration_minutes=self.duration_minutes,
            priority=self.priority,
            frequency=self.frequency,
            start_time=next_time,
            pet=self.pet,
        )
        return next_task

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

    def get_tasks_by_time(self, tasks=None):
        """Return tasks sorted chronologically by start_time. Unscheduled tasks go last.

        Uses datetime.max as a sentinel for None start_times so that unscheduled
        tasks sort to the end of the list.

        Args:
            tasks: Optional list of tasks to sort. Defaults to all tasks from all pets.

        Returns:
            list[Task]: Tasks ordered by start_time ascending.
        """
        if tasks is None:
            tasks = self._all_tasks()
        return sorted(tasks, key=lambda t: t.start_time or datetime.max)

    def detect_conflicts(self):
        """Return warning messages for any tasks whose time windows overlap.

        Uses a sweep-line approach over chronologically sorted tasks: for each
        consecutive pair, checks if the next task starts before the current one
        ends. This runs in O(n log n) time due to the sort, with a single O(n)
        pass for comparisons.

        Returns:
            list[str]: Warning messages for each detected overlap, or an empty list.
        """
        fmt = Task._TIME_FMT
        scheduled = [t for t in self.get_tasks_by_time() if t.start_time is not None]
        warnings = []
        for i in range(len(scheduled) - 1):
            task_a = scheduled[i]
            task_b = scheduled[i + 1]
            if task_b.start_time < task_a.get_end_time():
                pet_a = task_a.pet.name if task_a.pet else "Unassigned"
                pet_b = task_b.pet.name if task_b.pet else "Unassigned"
                warnings.append(
                    f"Conflict: '{task_a.title}' ({pet_a}) ends at "
                    f"{task_a.get_end_time().strftime(fmt)} but "
                    f"'{task_b.title}' ({pet_b}) starts at "
                    f"{task_b.start_time.strftime(fmt)}"
                )
        return warnings

    def get_weekly_view(self):
        """Return all tasks across all pets for the week."""
        return self._all_tasks()

    def get_daily_view(self, date):
        """Return all tasks scheduled for a specific date (accepts 'YYYY-MM-DD' string or date)."""
        if isinstance(date, str):
            date = datetime.strptime(date, "%Y-%m-%d").date()
        return [t for t in self._all_tasks() if t.start_time and t.start_time.date() == date]

    def schedule_tasks(self, date, start_hour=8):
        """Sort pending tasks by priority (then shortest duration) and assign sequential start times.

        Filters out completed tasks, then sorts by (priority, duration_minutes)
        so high-priority tasks run first and shorter tasks come before longer ones
        at the same priority level. Tasks are assigned back-to-back starting at
        start_hour with no gaps.

        Args:
            date: Date string in "YYYY-MM-DD" format.
            start_hour: Hour of day to begin scheduling (default 8 = 8:00 AM).

        Returns:
            list[Task]: Scheduled tasks in priority order with updated start_times.
        """
        priority_order = {"high": 0, "medium": 1, "low": 2}
        pending_tasks = [t for t in self._all_tasks() if t.status != "completed"]
        sorted_tasks = sorted(pending_tasks, key=lambda t: (priority_order.get(t.priority, 1), t.duration_minutes))

        current_time = datetime.strptime(f"{date} {start_hour:02d}:00", "%Y-%m-%d %H:%M")
        for task in sorted_tasks:
            task.update_time(current_time)
            current_time += timedelta(minutes=task.duration_minutes)

        return sorted_tasks

    def get_explanation(self):
        """Return a human-readable list explaining each scheduled task."""
        explanations = []
        fmt = Task._TIME_FMT
        for i, task in enumerate(self.get_tasks_by_time(), 1):
            if task.start_time is None:
                continue
            pet_name = task.pet.name if task.pet else "Unassigned"
            start_str = task.start_time.strftime(fmt)
            end_str = task.get_end_time().strftime(fmt)
            explanations.append(
                f"{i}. {task.title} ({pet_name}) — {start_str} to {end_str} | "
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
