from typing import Optional

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from routers.user.models import User


class UserDAL:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_user(self, email: str, phone_number: str, password: str) -> User:
        user = User(email=email, password=password, phone_number=phone_number)
        self.session.add(user)
        await self.session.flush()
        return user

    async def get_user_by_email(self, email: str) -> Optional[User]:
        query = select(User).where(User.email == email)
        res = await self.session.execute(query)
        user = res.fetchone()
        if user:
            return user[0]

    async def get_user_by_phone_number(self, phone_number: str) -> Optional[User]:
        query = select(User).where(User.phone_number == phone_number)
        res = await self.session.execute(query)
        user = res.fetchone()
        if user:
            return user[0]

    async def verify_email(self, email: str) -> Optional[User]:
        query = (
            update(User).where(User.email == email).values(is_verify=True)
        ).returning(User)
        res = await self.session.execute(query)
        row = res.fetchone()
        return row[0] if row else None

    async def update_user_password(self, email: str, password: str) -> Optional[User]:
        query = (
            update(User).where(User.email == email).values(password=password)
        ).returning(User)
        res = await self.session.execute(query)
        row = res.fetchone()
        return row[0] if row else None
