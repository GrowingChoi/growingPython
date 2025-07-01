import pymysql
from Car import Car

class DbConnection:
    def __init__(self, host="192.168.0.15", uid="user4", pw="9999", db_name="test_db"):
        self.host = host
        self.uid = uid
        self.pw = pw
        self.db_name = db_name

    def select_all_data(self,mode:str = "") -> list | None:
        result = ""

        if mode == "0만원~3000만원":
            result = "WHERE price BETWEEN 0 AND 3000"
        elif mode == "3000만원~5000만원":
            result = "WHERE price BETWEEN  3000 AND 5000"
        elif mode == "5000만원~7000만원":
            result = "WHERE price BETWEEN 5000 AND 7000"
        elif mode == "7000만원~1억원":
            result = "WHERE price BETWEEN 7000 AND 10000"
        elif mode == "1억원~2억원":
            result = "WHERE price BETWEEN 10000 AND 20000"
        elif mode == "2억원이상":
            result = "WHERE price >= 20000"


        sql = "SELECT * FROM car_info " + result + " AND img_url IS NOT NULL AND img_url != '' "

        cars = []

        try:
            # 커넥션 열기
            conn = pymysql.connect(
                host=self.host,
                port=3306,
                user=self.uid,
                password=self.pw,
                db=self.db_name,
                charset='utf8mb4',
                cursorclass=pymysql.cursors.Cursor  # 또는 DictCursor 원할 시 변경
            )

            with conn:
                with conn.cursor() as cursor:
                    cursor.execute(sql)
                    print("조회행수:", cursor.rowcount)
                    for row in cursor.fetchall():
                        if len(row) < 10:
                            row = row + ("",) * (10 - len(row))  # 부족한 필드를 빈 문자열로 채움
                        #car = Car(*row)
                        car = Car(*row)
                        cars.append(car)

        except pymysql.MySQLError as e:
            print("DB 오류:", e)
            return None

        return cars
    

    def insert_winner_info(self, car: Car) -> str:
        result = "fail"
        
        try:
            # DB 커넥션
            conn = pymysql.connect(
                host=self.host,
                port=3306,
                user=self.uid,
                password=self.pw,
                db=self.db_name,
                charset='utf8mb4',
                cursorclass=pymysql.cursors.Cursor
            )
            
            with conn:
                with conn.cursor() as cursor:
                    # 1. 기존에 해당 car_id가 있는지 확인
                    select_sql = "SELECT win_log FROM winner_info WHERE car_id = %s"
                    cursor.execute(select_sql, (car.car_id,))
                    existing = cursor.fetchone()
            
                    if existing:
            
                        # 2. 이미 있다면 win_log 1 증가시켜 업데이트
                        new_win_log = existing[0] + 1
                        update_sql = """
                        UPDATE winner_info
                        SET win_log = %s
                        WHERE car_id = %s
                        """
                        cursor.execute(update_sql, (new_win_log, car.car_id))
                    else:
            
                        # 3. 없다면 새로 insert (win_log = 1)
                        insert_sql = """
                        INSERT INTO winner_info (
                            car_id, model, img_url, price, outfit, win_log
                        ) VALUES (
                            %s, %s, %s, %s, %s, %s
                        )
                        """
                        cursor.execute(insert_sql, (
                            getattr(car, 'car_id', None),
                            getattr(car, 'model', None),
                            getattr(car, 'img_url', None),
                            getattr(car, 'price', None),
                            getattr(car, 'outfit', ""),
                            1
                        ))

                    conn.commit()
                    result = "success"

        except pymysql.MySQLError as e:
            print("DB 오류:", e)
            return None

        return result
