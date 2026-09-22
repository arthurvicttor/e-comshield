from sqlmodel import Field, SQLModel 


from app.db.base import Base


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: int | None = Field(
        default=None,
        primary_key=True,
        index=True,
    )

    username: str = Field(
        max_length=50,
        unique=True,
        index=True,
    )

    hashed_password: str = Field(
        max_length=255,
    )
    