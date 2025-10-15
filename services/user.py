from sqlalchemy.future import select

from db import AsyncSession
from models.user import UserModel
from schemas.user import UserSchema, UserCreateSchema
from common.exception import ApiException
from common.response import CommonResponse

def get_list() -> list:
    return []

async def create_user(data: UserCreateSchema, session: AsyncSession) -> CommonResponse:
    # 校验该用户名是否已存在
    result = await session.execute(
        select(UserModel).filter(UserModel.is_delete==False, UserModel.name==data.name)
    )
    if result.scalars().first():
        raise ApiException('该用户已存在')
    
    # 创建用户
    user = UserModel(**data.model_dump())
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return CommonResponse.success(data=UserSchema.model_validate(user).model_dump())

