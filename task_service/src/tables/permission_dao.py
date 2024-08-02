from sqlalchemy import Column, PrimaryKeyConstraint, INTEGER, Index, ForeignKeyConstraint
from database import Base


class PermissionDao(Base):
    __tablename__ = 'permission'
    access_user_id = Column(INTEGER, primary_key=True, autoincrement=False)
    task_id = Column(INTEGER, primary_key=True, autoincrement=False)
    access_mode = Column(INTEGER, nullable=False)

    __table_args__ = (
        PrimaryKeyConstraint("access_user_id", "task_id", name="permission_pkey"),
        ForeignKeyConstraint(['access_user_id'], ['user.id'], ondelete='CASCADE'),
        ForeignKeyConstraint(['task_id'], ['task.id'], ondelete='CASCADE')
    )
