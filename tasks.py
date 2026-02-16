from __future__ import annotations

from dataclasses import dataclass
from datetime import date
import os


@dataclass(slots=True)
class Task:
    task_id: int
    name: str
    frequency: int
    last_done: date

    @property
    def days_since_last_done(self) -> int:
        return (date.today() - self.last_done).days

    def save(self) -> None:
        file_path = os.getenv("TASKS_PATH")
        with open(file_path, encoding="utf-8") as f:
            lines = f.readlines()
        lines[self.task_id] =\
            f"{self.name}|{self.frequency}|{self.last_done.isoformat()}\n"
        with open(file_path, "w", encoding="utf-8") as f:
            f.writelines(lines)
            f.flush()

    @classmethod
    def load(cls) -> list[Task]:
        file_path = os.getenv("TASKS_PATH")
        with open(file_path, encoding="utf-8") as f:
            lines = f.readlines()
        return [cls(i, *line.strip().split("|")) for i, line in enumerate(lines)]

    def to_dict(self):
        return {
            "task_id": int(self.task_id),
            "name": self.name,
            "frequency": int(self.frequency),
            "last_done": self.last_done
        }

    @staticmethod
    def from_dict(data):
        return Task(
            task_id=int(data["task_id"]),
            name=data["name"],
            frequency=int(data["frequency"]),
            last_done=date.fromisoformat(data["last_done"])
        )

    @property
    def room(self) -> str:
        return self.name.split("]")[0][1:]
