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
