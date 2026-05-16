from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from db import mydb, cursor

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


@app.get("/")
def home():
    return FileResponse("form.html")


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