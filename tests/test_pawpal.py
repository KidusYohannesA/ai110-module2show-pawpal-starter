import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from pawpal_system import Task, Pet, Schedule, Owner


def test_task_completion():
    task = Task("Morning walk", duration_minutes=30, priority="high")
    assert task.status == "pending"
    task.mark_complete()
    assert task.status == "completed"


def test_task_addition_increases_pet_task_count():
    pet = Pet("Mochi", "dog")
    assert len(pet.tasks) == 0
    Task("Feeding", duration_minutes=15, pet=pet)
    assert len(pet.tasks) == 1
    Task("Grooming", duration_minutes=20, pet=pet)
    assert len(pet.tasks) == 2


def test_schedule_sorts_by_priority_then_duration():
    Task.clear()
    owner = Owner("Test")
    pet = Pet("Buddy", "dog")
    owner.add_pet(pet)

    Task("Long high", duration_minutes=60, priority="high", pet=pet)
    Task("Short high", duration_minutes=10, priority="high", pet=pet)
    Task("Medium task", duration_minutes=20, priority="medium", pet=pet)

    scheduled = owner.get_schedule().schedule_tasks("2026-01-01")

    assert scheduled[0].title == "Short high"
    assert scheduled[1].title == "Long high"
    assert scheduled[2].title == "Medium task"


def test_schedule_skips_completed_tasks():
    Task.clear()
    owner = Owner("Test")
    pet = Pet("Buddy", "dog")
    owner.add_pet(pet)

    done_task = Task("Done task", duration_minutes=15, priority="high", pet=pet)
    done_task.mark_complete()
    Task("Pending task", duration_minutes=20, priority="low", pet=pet)

    scheduled = owner.get_schedule().schedule_tasks("2026-01-01")

    assert len(scheduled) == 1
    assert scheduled[0].title == "Pending task"


def test_start_time_stored_as_datetime():
    from datetime import datetime

    task = Task("Walk", duration_minutes=30, start_time="2026-01-01 09:00")
    assert isinstance(task.start_time, datetime)

    end = task.get_end_time()
    assert isinstance(end, datetime)
    assert end == datetime(2026, 1, 1, 9, 30)


def test_get_tasks_by_time_returns_chronological_order():
    Task.clear()
    owner = Owner("Test")
    pet = Pet("Buddy", "dog")
    owner.add_pet(pet)

    Task("Late task", duration_minutes=10, priority="low",
         start_time="2026-01-01 14:00", pet=pet)
    Task("Early task", duration_minutes=10, priority="low",
         start_time="2026-01-01 08:00", pet=pet)
    Task("Mid task", duration_minutes=10, priority="low",
         start_time="2026-01-01 11:00", pet=pet)

    schedule = owner.get_schedule()
    sorted_tasks = schedule.get_tasks_by_time()

    assert sorted_tasks[0].title == "Early task"
    assert sorted_tasks[1].title == "Mid task"
    assert sorted_tasks[2].title == "Late task"


def test_get_tasks_by_time_unscheduled_tasks_go_last():
    Task.clear()
    owner = Owner("Test")
    pet = Pet("Buddy", "dog")
    owner.add_pet(pet)

    Task("No time", duration_minutes=10, pet=pet)
    Task("Has time", duration_minutes=10, start_time="2026-01-01 09:00", pet=pet)

    schedule = owner.get_schedule()
    sorted_tasks = schedule.get_tasks_by_time()

    assert sorted_tasks[0].title == "Has time"
    assert sorted_tasks[1].title == "No time"
    assert sorted_tasks[1].start_time is None


def test_daily_task_creates_next_occurrence_on_complete():
    from datetime import datetime, timedelta
    Task.clear()
    pet = Pet("Buddy", "dog")
    task = Task("Feeding", duration_minutes=15, priority="high",
                frequency="daily", start_time="2026-01-01 08:00", pet=pet)

    next_task = task.mark_complete()

    assert task.status == "completed"
    assert next_task is not None
    assert next_task.status == "pending"
    assert next_task.title == "Feeding"
    assert next_task.frequency == "daily"
    assert next_task.pet is pet
    assert next_task.start_time == datetime(2026, 1, 2, 8, 0)
    assert next_task in pet.tasks


def test_weekly_task_creates_next_occurrence_on_complete():
    from datetime import datetime, timedelta
    Task.clear()
    pet = Pet("Buddy", "dog")
    task = Task("Grooming", duration_minutes=20, priority="medium",
                frequency="weekly", start_time="2026-01-01 10:00", pet=pet)

    next_task = task.mark_complete()

    assert next_task.start_time == datetime(2026, 1, 8, 10, 0)
    assert next_task.frequency == "weekly"


def test_once_task_does_not_recur_on_complete():
    Task.clear()
    pet = Pet("Buddy", "dog")
    task = Task("Vet visit", duration_minutes=60, priority="high",
                frequency="once", start_time="2026-01-01 09:00", pet=pet)

    result = task.mark_complete()

    assert task.status == "completed"
    assert result is None
    assert len(pet.tasks) == 1


def test_detect_conflicts_finds_overlapping_tasks_different_pets():
    Task.clear()
    owner = Owner("Test")
    pet_a = Pet("Mochi", "dog")
    pet_b = Pet("Luna", "cat")
    owner.add_pet(pet_a)
    owner.add_pet(pet_b)

    Task("Walk", duration_minutes=30, start_time="2026-01-01 08:00", pet=pet_a)
    Task("Feeding", duration_minutes=20, start_time="2026-01-01 08:15", pet=pet_b)

    warnings = owner.get_schedule().detect_conflicts()

    assert len(warnings) == 1
    assert "Walk" in warnings[0]
    assert "Feeding" in warnings[0]


def test_detect_conflicts_same_pet_overlap():
    Task.clear()
    owner = Owner("Test")
    pet = Pet("Mochi", "dog")
    owner.add_pet(pet)

    Task("Walk", duration_minutes=30, start_time="2026-01-01 08:00", pet=pet)
    Task("Grooming", duration_minutes=20, start_time="2026-01-01 08:20", pet=pet)

    warnings = owner.get_schedule().detect_conflicts()

    assert len(warnings) == 1
    assert "Mochi" in warnings[0]


def test_detect_conflicts_no_overlap():
    Task.clear()
    owner = Owner("Test")
    pet = Pet("Mochi", "dog")
    owner.add_pet(pet)

    Task("Walk", duration_minutes=30, start_time="2026-01-01 08:00", pet=pet)
    Task("Feeding", duration_minutes=15, start_time="2026-01-01 08:30", pet=pet)

    warnings = owner.get_schedule().detect_conflicts()

    assert len(warnings) == 0


def test_pet_remove_task():
    Task.clear()
    pet = Pet("Mochi", "dog")
    task = Task("Walk", duration_minutes=30, pet=pet)

    assert len(pet.tasks) == 1
    pet.remove_task(task)
    assert len(pet.tasks) == 0


def test_get_daily_view_filters_by_date():
    Task.clear()
    owner = Owner("Test")
    pet = Pet("Buddy", "dog")
    owner.add_pet(pet)

    Task("Monday walk", duration_minutes=30,
         start_time="2026-01-05 09:00", pet=pet)
    Task("Tuesday walk", duration_minutes=30,
         start_time="2026-01-06 09:00", pet=pet)
    Task("No time", duration_minutes=15, pet=pet)

    schedule = owner.get_schedule()
    monday_tasks = schedule.get_daily_view("2026-01-05")

    assert len(monday_tasks) == 1
    assert monday_tasks[0].title == "Monday walk"


def test_monthly_task_creates_next_occurrence_on_complete():
    from datetime import datetime, timedelta
    Task.clear()
    pet = Pet("Buddy", "dog")
    task = Task("Flea treatment", duration_minutes=10, priority="high",
                frequency="monthly", start_time="2026-01-01 08:00", pet=pet)

    next_task = task.mark_complete()

    assert task.status == "completed"
    assert next_task is not None
    assert next_task.start_time == datetime(2026, 1, 31, 8, 0)
    assert next_task.frequency == "monthly"
    assert next_task.pet is pet


def test_edit_task_time_updates_start_time():
    Task.clear()
    owner = Owner("Test")
    pet = Pet("Buddy", "dog")
    owner.add_pet(pet)

    task = Task("Walk", duration_minutes=30,
                start_time="2026-01-01 08:00", pet=pet)
    schedule = owner.get_schedule()

    schedule.edit_task_time(task, "2026-01-01 14:00")

    from datetime import datetime
    assert task.start_time == datetime(2026, 1, 1, 14, 0)


def test_get_explanation_returns_formatted_strings():
    Task.clear()
    owner = Owner("Test")
    pet = Pet("Buddy", "dog")
    owner.add_pet(pet)

    Task("Walk", duration_minutes=30, priority="high",
         frequency="daily", start_time="2026-01-01 08:00", pet=pet)
    Task("Feeding", duration_minutes=15, priority="medium",
         frequency="once", start_time="2026-01-01 08:30", pet=pet)

    explanations = owner.get_schedule().get_explanation()

    assert len(explanations) == 2
    assert "Walk" in explanations[0]
    assert "Buddy" in explanations[0]
    assert "Priority: high" in explanations[0]
    assert "Frequency: daily" in explanations[0]
    assert "Feeding" in explanations[1]


# ── Edge-case tests ──────────────────────────────────────────────────


def test_chained_recurring_completions():
    """Completing a recurring task twice should produce a valid chain."""
    from datetime import datetime
    Task.clear()
    pet = Pet("Buddy", "dog")
    task1 = Task("Walk", duration_minutes=30, frequency="daily",
                 start_time="2026-01-01 08:00", pet=pet)

    task2 = task1.mark_complete()
    task3 = task2.mark_complete()

    assert task1.status == "completed"
    assert task2.status == "completed"
    assert task3.status == "pending"
    assert task3.start_time == datetime(2026, 1, 3, 8, 0)
    assert task3.pet is pet


def test_recurring_task_with_no_start_time():
    """A recurring task without a start_time should still create a next task, but with start_time=None."""
    Task.clear()
    pet = Pet("Buddy", "dog")
    task = Task("Walk", duration_minutes=30, frequency="daily", pet=pet)

    next_task = task.mark_complete()

    assert next_task is not None
    assert next_task.start_time is None
    assert next_task.pet is pet


def test_recurring_task_with_no_pet_does_not_recur():
    """A recurring task with no pet returns None on complete (no recurrence)."""
    Task.clear()
    task = Task("Walk", duration_minutes=30, frequency="daily",
                start_time="2026-01-01 08:00")

    result = task.mark_complete()

    assert task.status == "completed"
    assert result is None


def test_zero_duration_tasks_no_conflict():
    """Two zero-duration tasks at the same time are not flagged as conflicts."""
    Task.clear()
    owner = Owner("Test")
    pet = Pet("Buddy", "dog")
    owner.add_pet(pet)

    Task("Note A", duration_minutes=0, start_time="2026-01-01 08:00", pet=pet)
    Task("Note B", duration_minutes=0, start_time="2026-01-01 08:00", pet=pet)

    warnings = owner.get_schedule().detect_conflicts()
    assert len(warnings) == 0


def test_conflict_boundary_one_minute_before():
    """Task starting 1 min before previous ends IS a conflict; starting exactly at end is NOT."""
    Task.clear()
    owner = Owner("Test")
    pet = Pet("Buddy", "dog")
    owner.add_pet(pet)

    Task("Walk", duration_minutes=30, start_time="2026-01-01 08:00", pet=pet)
    Task("Feed", duration_minutes=15, start_time="2026-01-01 08:29", pet=pet)

    warnings = owner.get_schedule().detect_conflicts()
    assert len(warnings) == 1


def test_schedule_tasks_with_zero_duration():
    """Zero-duration tasks get scheduled at the same time (no advance)."""
    from datetime import datetime
    Task.clear()
    owner = Owner("Test")
    pet = Pet("Buddy", "dog")
    owner.add_pet(pet)

    Task("Note A", duration_minutes=0, priority="high", pet=pet)
    Task("Note B", duration_minutes=0, priority="high", pet=pet)

    scheduled = owner.get_schedule().schedule_tasks("2026-01-01")
    assert scheduled[0].start_time == scheduled[1].start_time == datetime(2026, 1, 1, 8, 0)


def test_get_daily_view_midnight_boundary():
    """A task at exactly midnight belongs to that day."""
    Task.clear()
    owner = Owner("Test")
    pet = Pet("Buddy", "dog")
    owner.add_pet(pet)

    Task("Midnight meds", duration_minutes=10,
         start_time="2026-01-05 00:00", pet=pet)
    Task("Late night walk", duration_minutes=15,
         start_time="2026-01-04 23:50", pet=pet)

    schedule = owner.get_schedule()
    jan5 = schedule.get_daily_view("2026-01-05")
    jan4 = schedule.get_daily_view("2026-01-04")

    assert len(jan5) == 1
    assert jan5[0].title == "Midnight meds"
    assert len(jan4) == 1
    assert jan4[0].title == "Late night walk"


def test_duplicate_pet_names_overwrite_pet_task_map():
    """A second pet with the same name overwrites the first in pet_task_map."""
    Task.clear()
    pet1 = Pet("Buddy", "dog")
    Task("Walk", duration_minutes=30, pet=pet1)

    pet2 = Pet("Buddy", "cat")
    Task("Groom", duration_minutes=20, pet=pet2)

    assert Task.pet_task_map["Buddy"] is pet2.tasks
    assert len(pet1.tasks) == 1  # pet1 still has its task
    assert len(Task.pet_task_map["Buddy"]) == 1  # but map points to pet2


def test_schedule_add_task_with_no_pet_does_nothing():
    """Adding a task with pet=None through Schedule is a no-op."""
    Task.clear()
    owner = Owner("Test")
    pet = Pet("Buddy", "dog")
    owner.add_pet(pet)
    schedule = owner.get_schedule()

    orphan = Task("Orphan", duration_minutes=10)
    schedule.add_task(orphan)

    assert len(schedule._all_tasks()) == 0


def test_schedule_remove_task_with_no_pet_does_nothing():
    """Removing a task with pet=None through Schedule is a no-op (no error)."""
    Task.clear()
    owner = Owner("Test")
    schedule = owner.get_schedule()

    orphan = Task("Orphan", duration_minutes=10)
    schedule.remove_task(orphan)  # should not raise
