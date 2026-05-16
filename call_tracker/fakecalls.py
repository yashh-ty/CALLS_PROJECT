from db import mydb,cursor

#give in format of "2026-034"
doa="2026-04-15"
student_name="SUMAN"
symbol="ASIANPAINT"
call_type="LONG"
entry_price=2600
target1=2700
target2=2800
stoploss=2400
insert_query = """

    INSERT INTO trade_calls (

        doa,
        student_name,
        symbol,
        call_type,
        entry_price,
        target1,
        target2,
        stoploss



    )

    VALUES (%s,%s,%s,%s,%s,%s,%s,%s)

"""

cursor.execute(insert_query, (
doa,student_name,symbol,call_type,entry_price,target1,target2,stoploss
))

mydb.commit()