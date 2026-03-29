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
