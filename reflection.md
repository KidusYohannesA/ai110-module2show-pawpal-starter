# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
- Add pet, Add/edit Tasks, Scheduling
- What classes did you include, and what responsibilities did you assign to each?
A pet class that stores tasks to its pet aswell as basic information about the task, A Task class detailing more information on the task including time, schedule class that keeps track of the entire schedule/tasks like a weekly calander(Actions: editing a tasks start and end time). Owner class has information about the owner, thier schedule, pets, tasks.

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.
Task is now the central registry via a class-level pet_task_map, linking each pet to its tasks replacing the scattered Pet.tasks list
end_time removed from Task; it's now derived via get_end_time() using start_time + duration_minutes
Pet no longer stores its own task list — it delegates to Task.pet_task_map
Schedule is the single source of truth for the owner's calendar, with get_tasks_for_pet() for filtering
Owner.tasks removed — Owner.schedule is the only way to access tasks
---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
