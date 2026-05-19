from fastapi import FastAPI, HTTPException,Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from db import mydb,cursor
import bcrypt
import random
app = FastAPI()

# -----------------------------------
# CORS
# -----------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------------
# SUBMIT TRADE CALL API
# -----------------------------------


# @app.get("/")
# def home():
#     return FileResponse("form.html")


@app.post("/submit_call")
def submit_call(data: dict):

    try:

        # -----------------------------
        # FETCH DATA
        # -----------------------------

        doa = data.get("call_date")

        student_name = data.get("student_name")

        symbol = data.get("symbol")

        call_type = data.get("call_type")

        entry_price = float(data.get("entry_price"))

        target1 = float(data.get("target1"))

        target2 = float(data.get("target2"))

        stoploss = float(data.get("stoploss"))

        # -----------------------------
        # RISK REWARD CALCULATION
        # -----------------------------

        risk = abs(entry_price - stoploss)

        reward = abs(target2 - entry_price)

        # -----------------------------
        # INSERT QUERY
        # -----------------------------

        insert_query = """

            INSERT INTO trade_calls (

                doa,
                student_name,
                symbol,
                call_type,
                entry_price,
                target1,
                target2,
                stoploss,
                risk,
                reward

            )

            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)

        """

        values = (

            doa,
            student_name,
            symbol,
            call_type,
            entry_price,
            target1,
            target2,
            stoploss,
            risk,
            reward

        )

        cursor.execute(insert_query, values)

        mydb.commit()

        return {

            "message": "Trade Call Added Successfully"

        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )




@app.post("/login")
def login(data: dict = Body(...)):

    try:

        mobilenumber = data.get("mobileNumber")

        pin = data.get("pin")

        # -----------------------------
        # CHECK USER IN DATABASE
        # -----------------------------

        query = """

            SELECT id, full_name, pin_hash
            FROM users_call
            WHERE mobile_number=%s

        """

        values = (mobilenumber,)

        cursor.execute(query, values)

        user = cursor.fetchone()

        # -----------------------------
        # INVALID LOGIN
        # -----------------------------

        if not user:

            raise HTTPException(
                status_code=401,
                detail="Invalid Mobilenumber or Pin"
            )

        stored_hash = user[2]

        # -----------------------------
        # VERIFY PIN
        # -----------------------------

        if not bcrypt.checkpw(

            pin.encode("utf-8"),
            stored_hash.encode("utf-8")

        ):

            raise HTTPException(
                status_code=401,
                detail="Invalid Mobilenumber or Pin"
            )

        # -----------------------------
        # SUCCESS LOGIN
        # -----------------------------

        return {

            "success": True,

            "message": "Login Successful",

            "user": {

                "id": user[0],

                "full_name": user[1]

            }

        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@app.post("/signup")
def signup(data: dict = Body(...)):

    try:

        # -----------------------------------
        # FETCH DATA
        # -----------------------------------

        full_name = data.get("fullName")

        mobile_number = data.get("mobileNumber")

        dob = data.get("DOB")

        pin_code = data.get("pinCode")

        city = data.get("city")

        email = data.get("email")

        pin = data.get("pin")

        # -----------------------------------

        # -----------------------------------

        check_query = """

            SELECT id
            FROM users_call
            WHERE email=%s
            OR mobile_number=%s

        """

        cursor.execute(
            check_query,
            (email, mobile_number)
        )

        existing_user = cursor.fetchone()

        if existing_user:

            raise HTTPException(
                status_code=400,
                detail="User already exists"
            )

        # -----------------------------------
        # HASH PIN
        # -----------------------------------

        hashed_pin = bcrypt.hashpw(
            pin.encode("utf-8"),
            bcrypt.gensalt()
        )

        # -----------------------------------
        # INSERT QUERY
        # -----------------------------------

        insert_query = """

            INSERT INTO users_call (

                full_name,
                mobile_number,
                dob,
                pin_code,
                city,
                email,
                pin_hash

            )

            VALUES (%s,%s,%s,%s,%s,%s,%s)

        """

        values = (

            full_name,
            mobile_number,
            dob,
            pin_code,
            city,
            email,
            hashed_pin.decode("utf-8")

        )

        cursor.execute(insert_query, values)

        mydb.commit()

        return {

            "success": True,
            "message": "Signup Successful"

        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


    

@app.post("/send-otp")
async def send_otp(data: dict = Body(...)):

    try:

        email = data.get("email")

        otp = str(random.randint(100000, 999999))

        connection = mydb

        cursor = connection.cursor()

        # -----------------------------------
        # DELETE OLD OTP OF SAME EMAIL
        # -----------------------------------

        delete_query = """

            DELETE FROM email_otp
            WHERE email=%s

        """

        cursor.execute(delete_query, (email,))

        # -----------------------------------
        # INSERT NEW OTP
        # -----------------------------------

        insert_query = """

            INSERT INTO email_otp (

                email,
                otp

            )

            VALUES (%s,%s)

        """

        cursor.execute(insert_query, (email, otp))

        mydb.commit()

        return {

            "success": True,
            "message": "OTP Sent"


        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@app.post("/verify-otp")
def verify_otp(data: dict = Body(...)):

    try:

        email = data.get("email")

        otp = data.get("otp")

        query = """

            SELECT id
            FROM email_otp
            WHERE email=%s
            AND otp=%s

        """
        connection = mydb

        cursor = connection.cursor()

        cursor.execute(query, (email, otp))

        result = cursor.fetchone()

        if not result:

            raise HTTPException(
                status_code=401,
                detail="Invalid OTP"
            )


        mydb.commit()

        return {

            "success": True,
            "message": "OTP Verified"

        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
