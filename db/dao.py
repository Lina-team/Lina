from .utils import connection
from .models import User, Group, Note
from sqlalchemy import select
from typing import List, Dict, Any, Optional
from sqlalchemy.exc import SQLAlchemyError


@connection
async def set_user(session, tg_id: int, name: str) -> User:
    try:
        user = await session.scalar(select(User).filter_by(id=tg_id))

        if not user:
            new_user = User(id=tg_id, name=name)
            session.add(new_user)
            await session.commit()
            return new_user
        else:
            return user
    except SQLAlchemyError as e:
        await session.rollback()


@connection
async def set_group(session, group_id: int) -> Group:
    try:
        group = await session.scalar(select(Group).filter_by(id=group_id))

        if not group:
            new_group = Group(id=group_id)
            session.add(new_group)
            await session.commit()
            return new_group
        else:
            return group
    except SQLAlchemyError as e:
        await session.rollback()


@connection
async def get_notes(session, group_id: int) -> list[Note]:
    try:
        res = await session.execute(select(Note).where(Note.group_id == group_id))
        notes = res.scalars().all()
        return notes
    except SQLAlchemyError as e:
        await session.rollback()


@connection
async def set_note(session, name: str, note: str, group_id: int) -> Note:
    try:
        group = await session.scalar(select(Group).filter_by(id=group_id))

        if not group:
            group = Group(id=group_id)
            session.add(group)
            await session.commit()

        note = Note(name=name, note=note, group_id=group_id)
        session.add(note)
        await session.commit()
        return note
    except SQLAlchemyError as e:
        print(e)
        await session.rollback()


@connection
async def delete_note(session, name: str, group_id: int) -> bool:
    try:
        note = await session.scalar(select(Note).filter_by(name=name, group_id=group_id))

        if not note:
            return False

        await session.delete(note)
        await session.commit()
        return True
    except SQLAlchemyError as e:
        await session.rollback()


@connection
async def get_note(session, name: str, group_id: int) -> Note:
    try:
        note = await session.scalar(select(Note).filter_by(name=name, group_id=group_id))
        return note
    except SQLAlchemyError as e:
        await session.rollback()


@connection
async def set_rules(session, group_id: int, rules: str) -> None:
    try:
        group = await session.scalar(select(Group).filter_by(id=group_id))

        if not group:
            group = Group(id=group_id)
            session.add(group)
            await session.commit()

        group.rules = rules
        await session.commit()
    except SQLAlchemyError as e:
        await session.rollback()


@connection
async def get_rules(session, group_id: int):
    try:
        res = await session.execute(select(Group).where(Group.id == group_id))
        rules = res.scalars().first().rules
        return rules
    except SQLAlchemyError as e:
        await session.rollback()
