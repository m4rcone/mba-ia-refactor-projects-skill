from sqlalchemy.orm import joinedload

from database import db
from utils.dates import utcnow


class Task(db.Model):
    __tablename__ = "tasks"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(50), default="pending")
    priority = db.Column(db.Integer, default=3)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"), nullable=True)
    created_at = db.Column(db.DateTime, default=utcnow)
    updated_at = db.Column(db.DateTime, default=utcnow, onupdate=utcnow)
    due_date = db.Column(db.DateTime, nullable=True)
    tags = db.Column(db.String(500), nullable=True)

    user = db.relationship("User", backref="tasks")
    category = db.relationship("Category", backref="tasks")

    @classmethod
    def get_all(cls):
        return cls.query.all()

    @classmethod
    def get_all_with_relations(cls):
        return cls.query.options(joinedload(cls.user), joinedload(cls.category)).all()

    @classmethod
    def get_by_id(cls, task_id):
        return cls.query.get(task_id)

    @classmethod
    def get_by_user(cls, user_id):
        return cls.query.filter_by(user_id=user_id).all()

    @classmethod
    def count(cls):
        return cls.query.count()

    @classmethod
    def count_by_status(cls, status):
        return cls.query.filter_by(status=status).count()

    @classmethod
    def count_by_priority(cls, priority):
        return cls.query.filter_by(priority=priority).count()

    @classmethod
    def count_by_category(cls, category_id):
        return cls.query.filter_by(category_id=category_id).count()

    @classmethod
    def search(cls, text=None, status=None, priority=None, user_id=None):
        query = cls.query
        if text:
            query = query.filter(
                db.or_(
                    cls.title.like(f"%{text}%"),
                    cls.description.like(f"%{text}%"),
                )
            )
        if status:
            query = query.filter(cls.status == status)
        if priority is not None:
            query = query.filter(cls.priority == priority)
        if user_id is not None:
            query = query.filter(cls.user_id == user_id)
        return query.all()

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def is_overdue(self):
        if not self.due_date or self.status in ("done", "cancelled"):
            return False
        return self.due_date < utcnow()

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "status": self.status,
            "priority": self.priority,
            "user_id": self.user_id,
            "category_id": self.category_id,
            "created_at": str(self.created_at),
            "updated_at": str(self.updated_at),
            "due_date": str(self.due_date) if self.due_date else None,
            "tags": self.tags.split(",") if self.tags else [],
        }

    def to_dict_detailed(self):
        data = self.to_dict()
        data["overdue"] = self.is_overdue()
        return data

    def to_dict_enriched(self):
        data = self.to_dict_detailed()
        data["user_name"] = self.user.name if self.user else None
        data["category_name"] = self.category.name if self.category else None
        return data

    def to_summary(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "status": self.status,
            "priority": self.priority,
            "created_at": str(self.created_at),
            "due_date": str(self.due_date) if self.due_date else None,
            "overdue": self.is_overdue(),
        }
