from sqladmin import ModelView

from app.models.user import User


class UserAdmin(ModelView, model=User):
    can_create = True
    can_edit = True
    can_delete = False
    can_view_details = True

    column_list = ["__all__"]
    column_searchable_list = [User.username, User.email]
    column_sortable_list = [User.id]
    column_details_exclude_list = [User.hashed_password]
