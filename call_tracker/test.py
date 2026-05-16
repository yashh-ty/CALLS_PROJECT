from db import mydb, cursor





query = """

SELECT id,doa,symbol,call_type,entry_price,target1,target2,stoploss,status,status_date
FROM trade_calls
WHERE status IN('ACTIVE',"HOLD","ENTRYZONE","TARGET1 HIT")
"""

cursor.execute(query)

active_calls = cursor.fetchall()
print(active_calls)

# GROUP CALLS SYMBOL WISE
grouped = {}
for i in active_calls:
    symbol = i[2]
    if symbol not in grouped:
        grouped[symbol] = []
    grouped[symbol].append(i)

print(grouped)

# FINDING MINIMUM DOA OF EACH SYMBOL
symbol_min_date = {}
for symbol, data in grouped.items():
    min_date = min(d[1] for d in data)
    symbol_min_date[symbol] = min_date

print(symbol_min_date)

# ========FETCH OHLC DATA SYMBOL WISE=============

for symbol, min_doa in symbol_min_date.items():

    bhav_query = """

    SELECT
        T_DATE,
        HIGH_PRICE,
        LOW_PRICE

    FROM stock_streets.bhavcopy

    WHERE SYMBOL = %s
    AND T_DATE >%s

    ORDER BY T_DATE ASC

    """

    cursor.execute(bhav_query, (symbol, min_doa))

    candles = cursor.fetchall()

    print(candles)

    symbol_trades = grouped[symbol]


    for trade in symbol_trades:
        trade_id = trade[0]

        call_type = trade[3]

        entry_price = float(trade[4])

        target1 = float(trade[5])

        target2 = float(trade[6])

        stoploss = trade[7]

        trade_status = trade[8]

        status_date = trade[9]

        #
        for candle in candles:

            new_status = None
            candle_date = candle[0]

            high_price = float(candle[1])

            low_price = float(candle[2])

            if candle_date < trade[1]:
                continue
            if call_type == "LONG":

                status_rank = {
                    "HOLD": 1,
                    "ENTRYZONE": 2,
                    "TARGET1 HIT": 3,
                    "TARGET2 HIT": 4,
                    "SL HIT": 5
                }


                if high_price >= target2:
                    new_status = "TARGET2 HIT"

                elif high_price >= target1:
                    new_status = "TARGET1 HIT"

                elif high_price >= entry_price:
                    new_status = "ENTRYZONE"

                elif low_price <= stoploss and trade_status!="TARGET1 HIT" and trade_status != "TARGET2 HIT" :
                    new_status = "SL HIT"


                if new_status:
                    if status_rank[new_status] > status_rank[trade_status]:
                        trade_status = new_status
                        status_date = candle_date


                if trade_status in ["TARGET2 HIT", "SL HIT"]:
                    update_query = """
                    UPDATE trade_calls
                    SET
                    status = %s,
                    status_date = %s
                    WHERE id = %s

                    """

                    cursor.execute(update_query,
                                   (trade_status, status_date, trade_id))

                    mydb.commit()

                    print(
                        f"TRADE ID {trade_id} | "
                        f"{symbol} | "
                        f"{trade_status}"
                    )
                    print(status_date)
                    print("VALIDATION COMPLETED")
                    break



        else:
            update_query = """
            UPDATE trade_calls
            SET
            status = %s,
            status_date = %s
            WHERE id = %s
            """

            cursor.execute(update_query,
                               (trade_status, status_date, trade_id))

            mydb.commit()

            print(
                    f"TRADE ID {trade_id} | "
                    f"{symbol} | "
                    f"{trade_status}"
                )
            print(status_date)
            print("VALIDATION COMPLETED")


