import pymysql
# mariadb연동을 위한 모듈 import


# 컨넥트를 미리 만들어준다.
# 접속할 host, uesr, password, db, 인코딩 입력
connect = pymysql.connect(host='localhost', port=3307, user='root', password='fiberpro1230',
                          db='fbgi_ms', charset='utf8')

# 커서 생성
cur = connect.cursor()

# sql문 실행
sql = "select * from db_test"

cur.execute(sql)
# DB결과를 모두 가져올 때 사용
rows = cur.fetchall()

# 한번에 다 출력
print(rows)

# 원하는 행만 출력
print(rows[0])

# for문으로 출력
for row in rows:
    print(row)

# 연결 해제
connect.close()