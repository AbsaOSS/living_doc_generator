from dataclasses import dataclass


@dataclass
class GHProject:
    id: str
    number: int
    title: str

    def to_dict(self):
        return {
            "id": self.id,
            "number": self.number,
            "title": self.title
        }
