class Task:
    def __init__(self, title, description="", duration_minutes=0, priority="medium",
                 start_time=None, end_time=None, status="pending"):
        self.title = title
        self.description = description
        self.duration_minutes = duration_minutes
        self.priority = priority
        self.start_time = start_time
        self.end_time = end_time
        self.status = status

    def update_time(self, start_time, end_time):
        pass

    def get_duration(self):
        pass


class Pet:
    def __init__(self, name, species, breed="", age=0):
        self.name = name
        self.species = species
        self.breed = breed
        self.age = age
        self.tasks = []

    def add_task(self, task):
        pass

    def remove_task(self, task):
        pass

    def get_tasks(self):
        pass


class Schedule:
    def __init__(self, week_start_date):
        self.week_start_date = week_start_date
        self.tasks = []

    def add_task(self, task):
        pass

    def remove_task(self, task):
        pass

    def edit_task_time(self, task, start_time, end_time):
        pass

    def get_weekly_view(self):
        pass

    def get_daily_view(self, date):
        pass


class Owner:
    def __init__(self, name, email="", phone=""):
        self.name = name
        self.email = email
        self.phone = phone
        self.pets = []
        self.schedule = None
        self.tasks = []

    def add_pet(self, pet):
        pass

    def remove_pet(self, pet):
        pass

    def add_task(self, task):
        pass

    def get_schedule(self):
        pass
