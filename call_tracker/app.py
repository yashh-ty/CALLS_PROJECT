from flask import Flask, request, jsonify
from call_tracker.db import mydb, cursor
from flask_cors import CORS
app = Flask(__name__)
CORS(app)
@app.route('/submit_call', methods=['POST'])
def submit_call():

    data = request.json

    call_date = data.get("call_date")
    student_name = data.get("student_name")
    symbol = data.get("symbol")
    call_type = data.get("call_type")

    entry_price = float(data.get("entry_price"))
    target1 = float(data.get("target1"))
    target2 = float(data.get("target2"))
    stoploss = float(data.get("stoploss"))

    # -----------------------------
    # Risk Reward Calculation
    # -----------------------------

    risk = (entry_price - stoploss)

    reward = (target2 - entry_price)

    # -----------------------------
    # Insert Query
    # -----------------------------

    insert_query = """

        INSERT INTO trade_calls (

            call_date,
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

        call_date,
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

    return jsonify({

        "message": "Trade Call Added Successfully"

    })

if __name__ == "__main__":
    app.run(debug=True)