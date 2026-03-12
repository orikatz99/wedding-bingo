from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, Text, DateTime, UniqueConstraint

Base = declarative_base()

#user model
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    guest_name = Column(String, nullable=False)

    boards = relationship("Board", back_populates="user")

#board model
class Board(Base):
    __tablename__ = "boards"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    user = relationship("User", back_populates="boards")
    tasks = relationship("BoardTask", back_populates="board")

#board task model
class BoardTask(Base):
    __tablename__ = "board_tasks"
    __table_args__ = (
    UniqueConstraint("board_id", "row", "col", name="unique_task_position_per_board"),
)

    id = Column(Integer, primary_key=True, index=True)
    board_id = Column(Integer, ForeignKey("boards.id"), nullable=False)
    task_text = Column(String, nullable=False)
    is_completed = Column(Boolean, default=False)
    row = Column(Integer, nullable=False)
    col = Column(Integer, nullable=False)
    image_url = Column(String, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    board = relationship("Board", back_populates="tasks")