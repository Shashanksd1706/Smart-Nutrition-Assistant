from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

# 👤 User table
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    meals = relationship("MealHistory", back_populates="user")


# 🍽️ MealHistory table
class MealHistory(Base):
    __tablename__ = "meal_history"
    id = Column(Integer, primary_key=True, index=True)
    input_text = Column(Text, nullable=False)
    meal_plan = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="meals")
