from db import mydb, cursor

#Renaming active status of the calls to hold given today

query1=''' UPDATE call_book.trade_calls
SET status = 'HOLD' where status="ACTIVE"
'''
cursor.execute(query1)
mydb.commit()
print('Active calls updated to HOLD')


#checking  expired calls
query2=''' 
UPDATE trade_calls
SET status = 'EXPIRED',status_date=CURRENT_DATE()
WHERE doa <= CURDATE() - INTERVAL 30 DAY
AND status IN ('ENTRYZONE', 'HOLD')
'''
cursor.execute(query2)
mydb.commit()
print("EXPIRED CALLS UPDATED")



query = """

SELECT id,doa,symbol,call_type,entry_price,target1,target2,stoploss,status,status_date
FROM trade_calls
WHERE status IN("HOLD","ENTRYZONE","TARGET1 HIT")
"""

cursor.execute(query)

active_calls = cursor.fetchall()
print(active_calls)


# # ========FETCH OHLC DATA SYMBOL WISE=============

for i in active_calls:
    symbol=i[2]
    doa=i[1]
    trade_id = i[0]
    call_type = i[3]
    entry_price = float(i[4])
    target1 = float(i[5])
    target2 = float(i[6])
    stoploss = i[7]
    trade_status = i[8]
    status_date = i[9]
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

    cursor.execute(bhav_query, (symbol,doa))

    candles = cursor.fetchall()




    for candle in candles:
#
        new_status = None
        candle_date = candle[0]
        high_price = float(candle[1])

        low_price = float(candle[2])

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


