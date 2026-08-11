from sqlalchemy import Column, Integer, String, ForeignKey, Numeric, Boolean, DateTime, Date, Text, func
from sqlalchemy.orm import relationship
from backend.database import Base


class Role(Base):
    __tablename__ = "roles"
    role_id = Column(Integer, primary_key=True, index=True)
    role_name = Column(String(50), unique=True, nullable=False)


class User(Base):
    __tablename__ = "users"
    user_id = Column(Integer, primary_key=True, index=True)
    role_id = Column(Integer, ForeignKey("roles.role_id"), nullable=False)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    phone_profile = Column(String(15), unique=True, nullable=True)
    password_hash = Column(String(255), nullable=False)
    loyalty_points = Column(Integer, default=0)
    failed_login_attempts = Column(Integer, default=0, nullable=True)
    locked_until = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=func.now())

    role = relationship("Role")
    orders = relationship("Order", back_populates="customer")
    reservations = relationship("Reservation", back_populates="customer")
    feedback = relationship("Feedback", back_populates="customer")


class OTPVerification(Base):
    __tablename__ = "otp_verifications"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(100), index=True, nullable=False)
    otp_code = Column(String(6), nullable=False)
    expires_at = Column(DateTime, nullable=False)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())


class Employee(Base):
    __tablename__ = "employees"
    employee_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), unique=True, nullable=False)
    salary = Column(Numeric(10, 2), nullable=False)
    hire_date = Column(Date, nullable=False)
    status = Column(String(20), default="Active")

    user = relationship("User")
    attendance = relationship("Attendance", back_populates="employee")


class Attendance(Base):
    __tablename__ = "attendance"
    attendance_id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.employee_id"), nullable=False)
    date = Column(Date, nullable=False)
    clock_in = Column(DateTime, nullable=False)
    clock_out = Column(DateTime, nullable=True)

    employee = relationship("Employee", back_populates="attendance")


class Category(Base):
    __tablename__ = "categories"
    category_id = Column(Integer, primary_key=True, index=True)
    category_name = Column(String(50), unique=True, nullable=False)

    items = relationship("MenuItem", back_populates="category")


class MenuItem(Base):
    __tablename__ = "menu_items"
    item_id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey("categories.category_id"), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(String(255))
    price = Column(Numeric(10, 2), nullable=False)
    is_available = Column(Boolean, default=True)

    category = relationship("Category", back_populates="items")
    ingredients = relationship("MenuItemIngredient", back_populates="menu_item")


class Supplier(Base):
    __tablename__ = "suppliers"
    supplier_id = Column(Integer, primary_key=True, index=True)
    supplier_name = Column(String(100), nullable=False)
    contact_name = Column(String(100))
    phone = Column(String(15))
    email = Column(String(100))

    ingredients = relationship("Ingredient", back_populates="supplier")


class Ingredient(Base):
    __tablename__ = "ingredients"
    ingredient_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    stock_level = Column(Numeric(10, 2), default=0.00)
    unit = Column(String(20), nullable=False)
    low_stock_threshold = Column(Numeric(10, 2), nullable=False)
    supplier_id = Column(Integer, ForeignKey("suppliers.supplier_id"), nullable=True)

    supplier = relationship("Supplier", back_populates="ingredients")
    menu_items = relationship("MenuItemIngredient", back_populates="ingredient")


class MenuItemIngredient(Base):
    __tablename__ = "menu_item_ingredients"
    item_id = Column(Integer, ForeignKey("menu_items.item_id"), primary_key=True)
    ingredient_id = Column(Integer, ForeignKey("ingredients.ingredient_id"), primary_key=True)
    quantity_required = Column(Numeric(10, 2), nullable=False)

    menu_item = relationship("MenuItem", back_populates="ingredients")
    ingredient = relationship("Ingredient", back_populates="menu_items")


class CafeTable(Base):
    __tablename__ = "cafe_tables"
    table_id = Column(Integer, primary_key=True, index=True)
    table_number = Column(String(10), unique=True, nullable=False)
    seating_capacity = Column(Integer, nullable=False)
    status = Column(String(20), default="Available")


class Order(Base):
    __tablename__ = "orders"
    order_id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("users.user_id"), nullable=True)
    table_id = Column(Integer, ForeignKey("cafe_tables.table_id"), nullable=True)
    order_type = Column(String(20), nullable=False)
    order_status = Column(String(20), default="Pending")
    created_at = Column(DateTime, default=func.now())

    customer = relationship("User", back_populates="orders")
    items = relationship("OrderItem", back_populates="order")
    bill = relationship("Bill", uselist=False, back_populates="order")


class OrderItem(Base):
    __tablename__ = "order_items"
    order_item_id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.order_id"), nullable=False)
    item_id = Column(Integer, ForeignKey("menu_items.item_id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Numeric(10, 2), nullable=False)

    order = relationship("Order", back_populates="items")
    menu_item = relationship("MenuItem")


class Bill(Base):
    __tablename__ = "bills"
    bill_id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.order_id"), unique=True, nullable=False)
    subtotal = Column(Numeric(10, 2), nullable=False)
    tax_amount = Column(Numeric(10, 2), nullable=False)
    discount_applied = Column(Numeric(10, 2), default=0.00)
    total_amount = Column(Numeric(10, 2), nullable=False)
    payment_method = Column(String(30), nullable=False)
    payment_status = Column(String(20), default="Unpaid")
    issued_at = Column(DateTime, default=func.now())

    order = relationship("Order", back_populates="bill")


class Reservation(Base):
    __tablename__ = "reservations"
    reservation_id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    table_id = Column(Integer, ForeignKey("cafe_tables.table_id"), nullable=False)
    reservation_time = Column(DateTime, nullable=False)
    number_of_guests = Column(Integer, nullable=False)
    status = Column(String(20), default="Pending")
    created_at = Column(DateTime, default=func.now())

    customer = relationship("User", back_populates="reservations")


class Feedback(Base):
    __tablename__ = "feedback"
    feedback_id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    order_id = Column(Integer, ForeignKey("orders.order_id"), nullable=True)
    rating = Column(Integer, nullable=False)
    comments = Column(Text)
    created_at = Column(DateTime, default=func.now())

    customer = relationship("User", back_populates="feedback")