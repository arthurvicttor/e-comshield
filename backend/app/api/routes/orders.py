from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.api.deps import get_db
from app.models.order import Order
from app.models.user import User
from app.schemas.order import OrderResponse
from app.security.dependencies import get_current_user


router = APIRouter(
    prefix="/orders",
    tags=["Orders"],
)


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: int,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user_statement = select(User).where(
        User.username == current_user
    )

    user = db.exec(user_statement).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    order_statement = select(Order).where(
        Order.id == order_id
    )

    order = db.exec(order_statement).first()

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found",
        )

    if order.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this order",
        )

    return order