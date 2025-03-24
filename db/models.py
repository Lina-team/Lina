from sqlalchemy import String, BigInteger, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .database import Base


class User(Base):
    __tablename__ = 'user'
    name: Mapped[str] = mapped_column(String, nullable=True)


class Group(Base):
    __tablename__ = 'group'
    rules: Mapped[str] = mapped_column(String(1000), nullable=True)
    notes: Mapped[list["Note"]] = relationship("Note", back_populates="group", cascade="all, delete-orphan")

    
class Note(Base):
    __tablename__ = 'note'
    name: Mapped[str] = mapped_column(String(20), nullable=False)
    note: Mapped[str] = mapped_column(String(1000), nullable=False)
    group_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('group.id'))
    group: Mapped["Group"] = relationship("Group", back_populates="notes")

