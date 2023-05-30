from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = 'your-secret-key'

# 路由：首頁 
@app.route('/')
def index():
    if 'username' in session:
        return render_template('welcome.html', username=session['username'])
    else:
        return redirect('/login')

# 路由：使用者註冊
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # 從表單獲取使用者註冊資訊
        username = request.form['username']
        password = request.form['password']
        
        # 將使用者資訊儲存到資料庫，這裡使用SQLite作為範例
        with sqlite3.connect('database.db') as conn:
            cursor = conn.cursor()
            cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
            conn.commit()
        
        return redirect('/login')
    
    return render_template('register.html')

# 路由：使用者登入
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # 從表單獲取使用者登入資訊
        username = request.form['username']
        password = request.form['password']
        
        # 在資料庫中驗證使用者資訊，這裡使用SQLite作為範例
        with sqlite3.connect('database.db') as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
            user = cursor.fetchone()
            
            if user:
                # 使用者驗證成功，儲存使用者資訊到session
                session['username'] = user[1]
                return redirect('/')
        
        # 使用者驗證失敗，返回登入頁面
        return render_template('login.html', message='Invalid username or password')
    
    return render_template('login.html')

# 路由：使用者登出
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect('/login')

if __name__ == '__main__':
    app.run(debug=True)
