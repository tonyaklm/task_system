from sqlalchemy import Column, PrimaryKeyConstraint, Index, VARCHAR, INTEGER, ForeignKeyConstraint
from database import Base


class TaskDao(Base):
    __tablename__ = 'task'
    id = Column(INTEGER, primary_key=True, autoincrement=True)
    user_id = Column(INTEGER, nullable=False)
    title = Column(VARCHAR, nullable=False)
    content = Column(VARCHAR, nullable=False)

    __table_args__ = (
        PrimaryKeyConstraint("id", name="task_pkey"),
        Index("user_index", "user_id"),
        ForeignKeyConstraint(['user_id'], ['user.id'])
    )
