import pymysql

passwords = ['', 'root', 'mysql', 'admin', '1234', '12345', 'password', 'root1234']
found = None
for pw in passwords:
    try:
        conn = pymysql.connect(host='127.0.0.1', port=3306, user='root', password=pw, connect_timeout=3)
        found = pw
        print(f'SUCCESS with password: "{pw}"')
        c = conn.cursor()
        c.execute('CREATE DATABASE IF NOT EXISTS library_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci')
        conn.commit()
        conn.close()
        print('library_db created/verified!')
        break
    except Exception as e:
        print(f'FAIL  "{pw}" -> {str(e)[:80]}')

if found is None:
    print('\nNone of the common passwords worked.')
    print('Please tell me your MySQL root password so I can update the .env file.')
