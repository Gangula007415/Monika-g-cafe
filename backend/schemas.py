# from pydantic import BaseModel, EmailStr
# from typing import Optional, List
# from pydantic import EmailStr
# from datetime import datetime, date


# # ==========================================
# # AUTH & USER SCHEMAS
# # ==========================================
# class UserRegister(BaseModel):
#     first_name: str
#     last_name: str
#     email: EmailStr
#     phone_profile: Optional[str] = None
#     password: str
#     role_id: int = 4

# class UserResponse(BaseModel):
#     user_id: int
#     first_name: str
#     last_name: str
#     email: EmailStr
#     loyalty_points: int
#     class Config:
#         from_attributes = True

# class Token(BaseModel):
#     access_token: str
#     token_type: str

# class OTPSendRequest(BaseModel):
#     email: EmailStr

# class OTPVerifyRequest(BaseModel):
#     email: EmailStr
#     otp_code: str

# class GoogleLoginRequest(BaseModel):
#     token: str

# # ==========================================
# # EMPLOYEE & ATTENDANCE SCHEMAS
# # ==========================================
# class EmployeeCreate(BaseModel):
#     user_id: int
#     salary: float
#     hire_date: date

# class AttendanceClock(BaseModel):
#     employee_id: int
#     clock_in: datetime

# # ==========================================
# # MENU SCHEMAS
# # ==========================================
# class MenuItemSchema(BaseModel):
#     name: str
#     description: Optional[str] = None
#     price: float
#     category_id: int
#     is_available: bool = True

# class MenuItemResponse(MenuItemSchema):
#     item_id: int
#     class Config:
#         from_attributes = True

# # ==========================================
# # INVENTORY SCHEMAS
# # ==========================================
# class IngredientCreate(BaseModel):
#     name: str
#     stock_level: float
#     unit: str
#     low_stock_threshold: float
#     supplier_id: Optional[int] = None

# # ==========================================
# # ORDER SCHEMAS
# # ==========================================
# class OrderItemDetails(BaseModel):
#     item_id: int
#     quantity: int
#     unit_price: float

# class OrderCreate(BaseModel):
#     customer_id: Optional[int] = None
#     table_id: Optional[int] = None
#     order_type: str
#     items: List[OrderItemDetails]

# # ==========================================
# # BILLING SCHEMAS
# # ==========================================
# class BillCreate(BaseModel):
#     order_id: int
#     subtotal: float
#     tax_amount: float
#     discount_applied: float = 0.0
#     total_amount: float
#     payment_method: str

# # ==========================================
# # RESERVATION SCHEMAS
# # ==========================================
# class ReservationCreate(BaseModel):
#     customer_id: int
#     table_id: int
#     reservation_time: datetime
#     number_of_guests: int

# # ==========================================
# # FEEDBACK SCHEMAS
# # ==========================================
# class FeedbackCreate(BaseModel):
#     customer_id: int
#     order_id: Optional[int] = None
#     rating: int
#     comments: Optional[str] = None

# # ==========================================
# # ANALYTICS & REPORTS SCHEMAS
# # ==========================================
# class SalesReportResponse(BaseModel):
#     start_date: date
#     end_date: date
#     total_orders: int
#     total_revenue: float
#     top_selling_items: List[str]

#     class PhoneSchema(BaseModel):
#         phone: str


from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime, date


# ==========================================
# AUTH & USER SCHEMAS
# ==========================================

class UserRegister(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone_profile: Optional[str] = None
    password: str
    role_id: int = 4


class UserResponse(BaseModel):
    user_id: int
    first_name: str
    last_name: str
    email: EmailStr
    loyalty_points: int

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


class OTPSendRequest(BaseModel):
    email: EmailStr


class OTPVerifyRequest(BaseModel):
    email: EmailStr
    otp_code: str


class GoogleLoginRequest(BaseModel):
    token: str



# ==========================================
# EMPLOYEE & ATTENDANCE SCHEMAS
# ==========================================

class EmployeeCreate(BaseModel):
    user_id: int
    salary: float
    hire_date: date


class AttendanceClock(BaseModel):
    employee_id: int
    clock_in: datetime



# ==========================================
# MENU SCHEMAS
# ==========================================

class MenuItemSchema(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    category_id: int
    is_available: bool = True


class MenuItemResponse(MenuItemSchema):
    item_id: int

    class Config:
        from_attributes = True



# ==========================================
# INVENTORY & SUPPLIER SCHEMAS
# ==========================================

class SupplierCreate(BaseModel):
    supplier_name: str
    contact_name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None


class SupplierResponse(SupplierCreate):
    supplier_id: int

    class Config:
        from_attributes = True



class IngredientCreate(BaseModel):
    name: str
    stock_level: float
    unit: str
    low_stock_threshold: float
    supplier_id: Optional[int] = None


class IngredientResponse(IngredientCreate):
    ingredient_id: int

    class Config:
        from_attributes = True



# ==========================================
# ORDER SCHEMAS
# ==========================================

class OrderItemDetails(BaseModel):
    item_id: int
    quantity: int
    unit_price: float


class OrderCreate(BaseModel):
    customer_id: Optional[int] = None
    table_id: Optional[int] = None
    order_type: str
    items: List[OrderItemDetails]



# ==========================================
# BILLING SCHEMAS
# ==========================================

class BillCreate(BaseModel):
    order_id: int
    subtotal: float
    tax_amount: float
    discount_applied: float = 0.0
    total_amount: float
    payment_method: str



# ==========================================
# RESERVATION SCHEMAS
# ==========================================

class ReservationCreate(BaseModel):
    customer_id: int
    table_id: int
    reservation_time: datetime
    number_of_guests: int



# ==========================================
# FEEDBACK SCHEMAS
# ==========================================

class FeedbackCreate(BaseModel):
    customer_id: int
    order_id: Optional[int] = None
    rating: int
    comments: Optional[str] = None



# ==========================================
# ANALYTICS SCHEMAS
# ==========================================

class SalesReportResponse(BaseModel):
    start_date: date
    end_date: date
    total_orders: int
    total_revenue: float
    top_selling_items: List[str]



# ==========================================
# PHONE SCHEMA
# ==========================================

class PhoneSchema(BaseModel):
    phone: str


class FacebookLoginRequest(BaseModel):
    token: str

class GithubLoginRequest(BaseModel):
    code: str

class MicrosoftLoginRequest(BaseModel):
    token: Optional[str] = None
    code: Optional[str] = None
    redirect_uri: Optional[str] = None


# ==========================================
# ACCOUNT LOCK SCHEMAS
# ==========================================

class AccountLockRequest(BaseModel):
    duration_minutes: Optional[int] = 15


class AccountLockStatusResponse(BaseModel):
    user_id: int
    email: str
    is_locked: bool
    failed_login_attempts: int
    locked_until: Optional[datetime] = None
    remaining_minutes: int = 0
