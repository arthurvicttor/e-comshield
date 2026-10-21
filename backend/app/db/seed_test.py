
import os

from sqlmodel import Session, select

from app.db.session import engine
from app.models.user import User
from app.models.order import Order
from app.security.password import hash_password


def seed_test_database():
    # Impede execução fora do ambiente de CI
    if os.getenv("GITHUB_ACTIONS") != "true":
        raise RuntimeError(
            "Este seed só pode ser executado no GitHub Actions."
        )

    with Session(engine) as session:
        # Criar usuário que realizará os testes
        user1 = session.exec(
            select(User).where(User.username == "user1")
        ).first()

        if user1 is None:
            user1 = User(
                username="user1",
                hashed_password=hash_password("user123"),
            )
            session.add(user1)
            session.commit()
            session.refresh(user1)

        # Criar proprietário do pedido
        user2 = session.exec(
            select(User).where(User.username == "user2")
        ).first()

        if user2 is None:
            user2 = User(
                username="user2",
                hashed_password=hash_password("user456"),
            )
            session.add(user2)
            session.commit()
            session.refresh(user2)

        # Criar um pedido de teste para o usuário2
        order = session.get(Order, 1)

        if order is None:
            order = Order(
                id=1,
                user_id=user2.id,
                product_name="Produto de teste",
                status="pending",
            )
            session.add(order)
            session.commit()

    print("Banco de testes preparado com sucesso.")


if __name__ == "__main__":
    seed_test_database()
