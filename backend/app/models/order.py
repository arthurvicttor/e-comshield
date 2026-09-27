from sqlmodel import Field, SQLModel


class Order(SQLModel, table=True):
    __tablename__ = "orders"

    id: int | None = Field(
        default=None,
        primary_key=True,
        index=True,
    )

    user_id: int = Field(
        foreign_key="users.id",
        index=True,
    )

    product_name: str = Field(
        max_length=100,
    )

    status: str = Field(
        max_length=50,
    )