from app.core.security import hash_password
from app.crud import BaseCrud
from app.models import User
from app.schemas import UserCreate, UserUpdate


class UserCrud(BaseCrud[User, UserCreate, UserUpdate]):
    def _prepare_create_data(self, obj_in: UserCreate) -> dict:
        data = obj_in.model_dump(exclude={"password"})
        data["hashed_password"] = hash_password(obj_in.password)
        return data


user_crud = UserCrud(User)
