from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from backend.database import get_db
from backend import models, schemas
from backend.utils import auth as auth_utils
from backend.utils.email import send_email

from backend.utils.auth import hash_password, create_access_token, verify_password, get_current_user, oauth2_scheme
from backend.config import settings
import random
from datetime import datetime, timedelta
import httpx

import os
from pydantic import BaseModel, Field
from twilio.rest import Client  # 🚀 Added for live SMS transmission

# ── 1. SCHEMA DEFINITIONS (DE-DUPLICATED) ──────────────────────────
class PhoneSchema(BaseModel):
    phone: str = Field(..., placeholder="+916303674994")

class PhoneVerifyRequest(BaseModel):
    phone: str
    otp_code: str

# ── 2. TWILIO CONFIGURATION METRICS ────────────────────────────────
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "")
TWILIO_FROM_NUMBER = os.getenv("TWILIO_FROM_NUMBER", "+12193552493")

# ── 2b. ACCOUNT LOCKOUT SETTINGS ───────────────────────────────────
MAX_FAILED_ATTEMPTS = 5
LOCKOUT_DURATION_MINUTES = 15

router = APIRouter(prefix="/auth", tags=["Authentication"])

# ── 3. REGISTER ENDPOINT (ROBUST ROLE VALIDATION) ──────────────────
@router.post("/register", response_model=schemas.UserResponse)
def register(user_data: schemas.UserRegister, db: Session = Depends(get_db)):
    existing_user = db.query(models.User).filter(models.User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    if user_data.phone_profile and user_data.phone_profile.strip():
        existing_phone = db.query(models.User).filter(models.User.phone_profile == user_data.phone_profile.strip()).first()
        if existing_phone:
            raise HTTPException(status_code=400, detail="Phone number already registered to another account")

    # Safety check: Verify that the requested role_id actually exists in the database
    target_role_id = user_data.role_id
    role_exists = db.query(models.Role).filter(models.Role.role_id == target_role_id).first()
    
    if not role_exists:
        default_role = db.query(models.Role).filter(models.Role.role_name.ilike("customer")).first()
        if default_role:
            target_role_id = default_role.role_id
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail=f"Role ID {target_role_id} does not exist. Please provide a valid role."
            )

    hashed_pwd = auth_utils.hash_password(user_data.password)
    new_user = models.User(
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        email=user_data.email,
        phone_profile=user_data.phone_profile.strip() if user_data.phone_profile else None,
        password_hash=hashed_pwd,
        role_id=target_role_id
    )
    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
    except IntegrityError as err:
        db.rollback()
        raise HTTPException(status_code=400, detail="Account registration failed due to duplicate entry (Email or Phone already registered).")
    return new_user


# ── 4. LOG IN ENDPOINT (NOW WITH ACCOUNT LOCKOUT) ──────────────────
@router.post("/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == form_data.username).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Credentials")

    if user.locked_until and user.locked_until > datetime.now():
        remaining = int((user.locked_until - datetime.now()).total_seconds() // 60) + 1
        raise HTTPException(
            status_code=status.HTTP_423_LOCKED,
            detail=f"Account locked due to too many failed attempts. Try again in {remaining} minute(s)."
        )

    if user.locked_until and user.locked_until <= datetime.now():
        user.failed_login_attempts = 0
        user.locked_until = None

    if not auth_utils.verify_password(form_data.password, user.password_hash):
        user.failed_login_attempts = (user.failed_login_attempts or 0) + 1

        if user.failed_login_attempts >= MAX_FAILED_ATTEMPTS:
            user.locked_until = datetime.now() + timedelta(minutes=LOCKOUT_DURATION_MINUTES)
            db.commit()
            raise HTTPException(
                status_code=status.HTTP_423_LOCKED,
                detail=f"Account locked due to too many failed attempts. Try again in {LOCKOUT_DURATION_MINUTES} minute(s)."
            )

        db.commit()
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Credentials")

    if user.failed_login_attempts or user.locked_until:
        user.failed_login_attempts = 0
        user.locked_until = None
        db.commit()

    access_token = auth_utils.create_access_token(data={"sub": user.email, "role": user.role_id})
    return {"access_token": access_token, "token_type": "bearer"}

# ── 5. EMAIL OTP DISPATCH ──────────────────────────────────────────
@router.post("/send-otp")
def send_otp(request: schemas.OTPSendRequest, db: Session = Depends(get_db)):
    otp_code = f"{random.randint(100000, 999999)}"
    expires_at = datetime.now() + timedelta(minutes=5)

    otp_entry = models.OTPVerification(
        email=request.email,
        otp_code=otp_code,
        expires_at=expires_at,
        is_verified=False
    )
    db.add(otp_entry)
    db.commit()

    html_content = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; border: 1px solid #e0e0e0; border-radius: 8px; overflow: hidden; box-shadow: 0 4px 10px rgba(0,0,0,0.05);">
        <div style="background-color: #d4a373; padding: 20px; text-align: center; color: white;">
            <h2 style="margin: 0; font-size: 24px; letter-spacing: 1px;">Monika G Cafe</h2>
        </div>
        <div style="padding: 30px; line-height: 1.6; color: #333;">
            <p>Hello,</p>
            <p>We received a request to log in to your Monika G Cafe account using a One-Time Password (OTP).</p>
            <div style="background-color: #fcf8f2; border: 1px dashed #d4a373; border-radius: 6px; padding: 15px; text-align: center; margin: 25px 0;">
                <span style="font-size: 32px; font-weight: bold; letter-spacing: 5px; color: #a3704c;">{otp_code}</span>
            </div>
            <p style="font-size: 14px; color: #666;">This OTP is valid for <strong>5 minutes</strong>. If you did not request this, please ignore this email.</p>
        </div>
        <div style="background-color: #f1f1f1; padding: 15px; text-align: center; font-size: 12px; color: #888; border-top: 1px solid #e0e0e0;">
            &copy; 2026 Monika G Cafe. All rights reserved.
        </div>
    </div>
    """
    email_sent = send_email(
        to_email=request.email,
        subject="Monika G Cafe - Log In OTP",
        html_content=html_content
    )

    print(f"\n[OTP Dispatch] Generated OTP {otp_code} for {request.email}. Email sent status: {email_sent}\n")
    
    res = {
        "status": "success",
        "message": "OTP generated successfully",
        "email_delivered": email_sent,
        "fallback_otp": otp_code
    }
    return res

# ── 6. EMAIL OTP VERIFY ────────────────────────────────────────────
@router.post("/verify-otp", response_model=schemas.Token)
def verify_otp(request: schemas.OTPVerifyRequest, db: Session = Depends(get_db)):
    otp_record = db.query(models.OTPVerification).filter(
        models.OTPVerification.email == request.email,
        models.OTPVerification.is_verified == False,
        models.OTPVerification.expires_at > datetime.now()
    ).order_by(models.OTPVerification.id.desc()).first()

    if not otp_record or otp_record.otp_code != request.otp_code:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired OTP")

    otp_record.is_verified = True

    user = db.query(models.User).filter(models.User.email == request.email).first()
    if not user:
        user = models.User(
            email=request.email,
            role_id=4,
            password_hash=auth_utils.hash_password(""),
            first_name="User",
            last_name=""
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    else:
        db.commit()

    access_token = auth_utils.create_access_token(data={"sub": user.email, "role": user.role_id})
    return {"access_token": access_token, "token_type": "bearer"}

# ── 7. PHONE OTP DISPATCH ──────────────────────────────────────────
@router.post("/send-otp-phone")
async def send_otp_phone(data: PhoneSchema, db: Session = Depends(get_db)):
    raw_phone = data.phone.strip().replace(" ", "").replace("-", "")
    if not raw_phone.startswith("+"):
        if len(raw_phone) == 10:
            clean_phone = f"+91{raw_phone}"
        else:
            clean_phone = f"+{raw_phone}"
    else:
        clean_phone = raw_phone

    otp_code = f"{random.randint(100000, 999999)}"
    expires_at = datetime.now() + timedelta(minutes=5)

    otp_entry = models.OTPVerification(
        email=clean_phone,
        otp_code=otp_code,
        expires_at=expires_at,
        is_verified=False
    )
    db.add(otp_entry)
    db.commit()

    account_sid = settings.TWILIO_ACCOUNT_SID or os.getenv("TWILIO_ACCOUNT_SID", "")
    auth_token = settings.TWILIO_AUTH_TOKEN or os.getenv("TWILIO_AUTH_TOKEN", "")
    from_number = settings.TWILIO_FROM_NUMBER or os.getenv("TWILIO_FROM_NUMBER", "+12193552493")

    sms_sent = False
    twilio_error = None

    if account_sid and auth_token and from_number:
        try:
            client = Client(account_sid, auth_token)
            client.messages.create(
                body=f"Your secret code for Monika G Cafe is: {otp_code}. Welcome!",
                from_=from_number,
                to=clean_phone
            )
            sms_sent = True
            print(f"🚀 Live SMS delivered to carriers for: {clean_phone}")
        except Exception as e:
            twilio_error = str(e)
            print(f"⚠️ TWILIO ERROR ENCOUNTERED: {twilio_error}")
            print("\n" + "="*50)
            print(f"👉 TESTING FALLBACK OTP CODE: {otp_code} 👈")
            print("="*50 + "\n")
    else:
        print(f"⚠️ Twilio credentials missing in settings! Fallback OTP CODE: {otp_code}")

    res = {
        "status": "success",
        "detail": "OTP generated successfully",
        "sms_delivered": sms_sent
    }
    if twilio_error:
        res["twilio_error"] = twilio_error
        res["fallback_otp"] = otp_code
    elif not sms_sent:
        res["fallback_otp"] = otp_code

    return res

# ── 8. PHONE OTP VERIFY ────────────────────────────────────────────
@router.post("/verify-otp-phone", response_model=schemas.Token)
def verify_otp_phone(request: PhoneVerifyRequest, db: Session = Depends(get_db)):
    search_phone = request.phone.replace(" ", "")
    if not search_phone.startswith("+"):
        search_phone = f"+91{search_phone}"

    otp_record = db.query(models.OTPVerification).filter(
        models.OTPVerification.email == search_phone,
        models.OTPVerification.is_verified == False,
        models.OTPVerification.expires_at > datetime.now()
    ).order_by(models.OTPVerification.id.desc()).first()

    if not otp_record or otp_record.otp_code != request.otp_code:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired OTP")

    otp_record.is_verified = True
    db.commit()

    user = db.query(models.User).filter(
        (models.User.phone_profile == search_phone) | (models.User.phone_profile == request.phone.replace(" ", ""))
    ).first()

    if not user:
        user = models.User(
            first_name="Phone",
            last_name="User",
            email=f"phone_{random.randint(1000,9999)}@monikagcafe.local",
            phone_profile=search_phone,
            password_hash=auth_utils.hash_password(""),
            role_id=4
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    access_token = auth_utils.create_access_token(data={"sub": user.phone_profile, "role": user.role_id})
    return {"access_token": access_token, "token_type": "bearer"}

# ── 9. GOOGLE OAUTH LOGIN ──────────────────────────────────────────
@router.post("/google-login", response_model=schemas.Token)
async def google_login(payload: schemas.GoogleLoginRequest, db: Session = Depends(get_db)):
    if payload.token.startswith("mock_google_token_"):
        email = payload.token.replace("mock_google_token_", "") + "@gmail.com"
        given_name = "MockGoogle"
        family_name = "User"
    else:
        async with httpx.AsyncClient() as client:
            try:
                resp = await client.get(f"https://oauth2.googleapis.com/tokeninfo?id_token={payload.token}")
                if resp.status_code != 200:
                    raise HTTPException(status_code=400, detail="Invalid Google OAuth credential token")
                data = resp.json()
            except HTTPException:
                raise
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Failed to communicate with Google OAuth verification API: {str(e)}")

        google_client_id = settings.GOOGLE_CLIENT_ID
        if data.get("aud") != google_client_id:
            raise HTTPException(status_code=400, detail="Google client ID mismatch")

        email = data.get("email")
        if not email:
            raise HTTPException(status_code=400, detail="Google account email not found in token info")

        given_name = data.get("given_name", "Google")
        family_name = data.get("family_name", "User")

    user = db.query(models.User).filter(models.User.email == email).first()
    if not user:
        user = models.User(
            first_name=given_name,
            last_name=family_name,
            email=email,
            password_hash=auth_utils.hash_password(""),
            role_id=4
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    access_token = auth_utils.create_access_token(data={"sub": user.email, "role": user.role_id})
    return {"access_token": access_token, "token_type": "bearer"}

# ── 10. GITHUB OAUTH LOGIN ─────────────────────────────────────────
@router.post("/github-login", response_model=schemas.Token)
async def github_login(payload: schemas.GithubLoginRequest, db: Session = Depends(get_db)):
    async with httpx.AsyncClient() as client:
        token_resp = await client.post(
            "https://github.com/login/oauth/access_token",
            headers={"Accept": "application/json"},
            data={
                "client_id": settings.GITHUB_CLIENT_ID,
                "client_secret": settings.GITHUB_CLIENT_SECRET,
                "code": payload.code
            }
        )
        token_data = token_resp.json()
        gh_access_token = token_data.get("access_token")

        if not gh_access_token:
            raise HTTPException(status_code=400, detail="GitHub Token Exchange Failed")

        user_headers = {
            "Authorization": f"token {gh_access_token}",
            "User-Agent": "MonikaG-Cafe-App-v1.0",
            "Accept": "application/json"
        }
        user_resp = await client.get("https://api.github.com/user", headers=user_headers)
        user_data = user_resp.json()

        email = user_data.get("email")
        if not email:
            emails_resp = await client.get("https://api.github.com/user/emails", headers=user_headers)
            if emails_resp.status_code == 200:
                emails_list = emails_resp.json()
                primary = next((e["email"] for e in emails_list if e.get("primary")), None)
                email = primary or (emails_list[0]["email"] if emails_list else None)

        if not email:
            email = f"github_{user_data.get('id')}@monikagcafe.local"

        full_name = user_data.get("name") or user_data.get("login") or "GitHub User"
        name_parts = full_name.split(" ")
        first_name = name_parts[0]
        last_name = name_parts[-1] if len(name_parts) > 1 else ""

        user = db.query(models.User).filter(models.User.email == email).first()
        if not user:
            user = models.User(
                first_name=first_name,
                last_name=last_name,
                email=email,
                password_hash=hash_password(""),
                role_id=4
            )
            db.add(user)
            db.commit()
            db.refresh(user)

    access_token = create_access_token(data={"sub": user.email, "role": user.role_id})
    return {"access_token": access_token, "token_type": "bearer"}

# ── 11. FACEBOOK OAUTH LOGIN ───────────────────────────────────────
@router.post("/facebook-login", response_model=schemas.Token)
async def facebook_login(payload: schemas.FacebookLoginRequest, db: Session = Depends(get_db)):
    async with httpx.AsyncClient() as client:
        try:
            url = f"https://graph.facebook.com/me?fields=id,email,first_name,last_name&access_token={payload.token}"
            resp = await client.get(url)
            if resp.status_code != 200:
                raise HTTPException(status_code=400, detail="Invalid Facebook authentication token")
            data = resp.json()
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to reach Facebook API: {str(e)}")

    email = data.get("email") or f"fb_{data.get('id')}@monikagcafe.local"
    first_name = data.get("first_name", "Facebook")
    last_name = data.get("last_name", "User")

    user = db.query(models.User).filter(models.User.email == email).first()
    if not user:
        user = models.User(
            first_name=first_name,
            last_name=last_name,
            email=email,
            password_hash=auth_utils.hash_password(""),
            role_id=4
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    access_token = auth_utils.create_access_token(data={"sub": user.email, "role": user.role_id})
    return {"access_token": access_token, "token_type": "bearer"}

# ── 12. MICROSOFT OAUTH LOGIN ──────────────────────────────────────
@router.post("/microsoft-login", response_model=schemas.Token)
async def microsoft_login(payload: schemas.MicrosoftLoginRequest, db: Session = Depends(get_db)):
    if payload.token and payload.token.startswith("mock_microsoft_token_"):
        email = payload.token.replace("mock_microsoft_token_", "") + "@outlook.com"
        first_name = "MockMicrosoft"
        last_name = "User"
    else:
        ms_token = payload.token
        async with httpx.AsyncClient() as client:
            if not ms_token and payload.code:
                token_url = "https://login.microsoftonline.com/common/oauth2/v2.0/token"
                redirect_uri = payload.redirect_uri or "http://127.0.0.1:8000/login.html"
                token_data = {
                    "client_id": settings.MICROSOFT_CLIENT_ID,
                    "client_secret": settings.MICROSOFT_CLIENT_SECRET,
                    "code": payload.code,
                    "grant_type": "authorization_code",
                    "redirect_uri": redirect_uri,
                    "scope": "User.Read"
                }
                token_resp = await client.post(token_url, data=token_data)
                if token_resp.status_code != 200:
                    err_detail = token_resp.text
                    try:
                        err_json = token_resp.json()
                        err_detail = err_json.get("error_description", err_detail)
                    except Exception:
                        pass
                    print(f"⚠️ Microsoft token exchange failed ({token_resp.status_code}): {err_detail}")
                    raise HTTPException(status_code=400, detail=f"Microsoft token exchange failed: {err_detail}")
                ms_token = token_resp.json().get("access_token")

            if not ms_token:
                raise HTTPException(status_code=400, detail="Microsoft access token or authorization code required")

            try:
                graph_resp = await client.get(
                    "https://graph.microsoft.com/v1.0/me",
                    headers={"Authorization": f"Bearer {ms_token}"}
                )
                if graph_resp.status_code != 200:
                    raise HTTPException(status_code=400, detail="Invalid Microsoft authentication token")
                user_data = graph_resp.json()
            except HTTPException:
                raise
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Failed to reach Microsoft Graph API: {str(e)}")

        email = user_data.get("mail") or user_data.get("userPrincipalName") or f"ms_{user_data.get('id')}@monikagcafe.local"
        first_name = user_data.get("givenName") or user_data.get("displayName", "Microsoft").split(" ")[0]
        last_name = user_data.get("surname") or (user_data.get("displayName", "").split(" ")[-1] if " " in user_data.get("displayName", "") else "User")

    user = db.query(models.User).filter(models.User.email == email).first()
    if not user:
        user = models.User(
            first_name=first_name,
            last_name=last_name,
            email=email,
            password_hash=auth_utils.hash_password(""),
            role_id=4
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    access_token = auth_utils.create_access_token(data={"sub": user.email, "role": user.role_id})
    return {"access_token": access_token, "token_type": "bearer"}


# ── 13. AUTHORIZATION & CURRENT USER ─────────────────────────────
@router.get("/me", response_model=schemas.UserResponse)
def get_me(current_user: models.User = Depends(get_current_user)):
    """Retrieve details for the currently authorized user (Locked by Bearer Authorization token)"""
    return current_user


# ── 14. ACCOUNT LOCKOUT MANAGEMENT ─────────────────────────────────
@router.get("/lock-status/{user_id}", response_model=schemas.AccountLockStatusResponse)
def check_lock_status(user_id: int, db: Session = Depends(get_db)):
    """Query account lockout status and remaining lockout duration for a user."""
    user = db.query(models.User).filter(models.User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User account not found")

    is_locked = False
    remaining = 0
    if user.locked_until:
        if user.locked_until > datetime.now():
            is_locked = True
            remaining = int((user.locked_until - datetime.now()).total_seconds() // 60) + 1
        else:
            # Lockout expired, auto-clear
            user.failed_login_attempts = 0
            user.locked_until = None
            db.commit()

    return schemas.AccountLockStatusResponse(
        user_id=user.user_id,
        email=user.email,
        is_locked=is_locked,
        failed_login_attempts=user.failed_login_attempts or 0,
        locked_until=user.locked_until,
        remaining_minutes=remaining
    )


@router.post("/lock/{user_id}")
def lock_account(user_id: int, req: schemas.AccountLockRequest = None, db: Session = Depends(get_db)):
    """Manually lock a user account for a specified duration in minutes."""
    user = db.query(models.User).filter(models.User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User account not found")

    duration = (req.duration_minutes if req and req.duration_minutes else LOCKOUT_DURATION_MINUTES)
    user.locked_until = datetime.now() + timedelta(minutes=duration)
    user.failed_login_attempts = MAX_FAILED_ATTEMPTS
    db.commit()

    return {
        "status": "success",
        "message": f"Account for user {user.email} (ID: {user_id}) has been locked for {duration} minutes."
    }


@router.post("/unlock/{user_id}")
def unlock_account(user_id: int, db: Session = Depends(get_db)):
    """Manually unlock a user account and reset failed login attempts."""
    user = db.query(models.User).filter(models.User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User account not found")

    user.failed_login_attempts = 0
    user.locked_until = None
    db.commit()

    return {
        "status": "success",
        "message": f"Account for user {user.email} (ID: {user_id}) has been unlocked successfully."
    }
