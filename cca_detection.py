import tkinter as tk
import multthread_cca

def usr_login():
    global cookies
    name = var_usr_name.get()
    password = var_usr_pwd.get()

    cookies = multthread_cca.get_access_token(name, password)

    print(cookies)
    if cookies:
        result.set('登录成功，请输入房源编号')
        start_search_home()
    else:
        result.set('登录失败，请重新登录')

def start_search_home():
    home_detail.set('房源编号')
    btn_submit.set('submit')

def submit_home_keyword():
    keyword = home_detail.get()
    global cookies
    home_id, home_name = multthread_cca.get_home_detail(keyword, cookies)
    if home_id:
        try:
            multthread_cca.gen_final_file(home_id, home_name, cookies)
            result.set('数据获取完毕')
        except Exception as e:
            print(e)
            result.set('数据获取异常')
    else:
        result.set('房源未搜到，请输入正确房源')

# def process_data():
#     global cookies
#     try:
#         keyword = home_detail.get()
#         multthread_cca.gen_final_file(keyword, cookies)
#         result.set('数据获取完毕')
#     except Exception as e:
#         print(e)
#         result.set('数据获取异常')

if __name__ == '__main__':
    cookies = 0

    window = tk.Tk()
    window.title('Login')
    window.geometry('500x300')

    #创建标签
    tk.Label(window, text='User name:', font=('Arial', 14)).place(x=10, y=10)
    tk.Label(window, text='Password:', font=('Arial', 14)).place(x=10, y=50)

    #创建entry
    var_usr_name = tk.StringVar()
    var_usr_name.set('账号')
    entry_usr_name = tk.Entry(window, textvariable=var_usr_name, font=('Arial', 14))
    entry_usr_name.place(x=120, y=10)

    var_usr_pwd = tk.StringVar()
    var_usr_pwd.set('密码')
    entry_usr_pwd = tk.Entry(window, textvariable=var_usr_pwd, font=('Arial', 14), show='')
    entry_usr_pwd.place(x=120, y=50)

    #创建登录按钮
    btn_login = tk.Button(window, text='Login', command=usr_login)
    btn_login.place(x=120, y=80)

    home_detail = tk.StringVar()
    home_entry = tk.Entry(window, textvariable=home_detail, width=30)
    home_entry.place(x=80, y=130)

    # 创建一个submit按钮
    btn_submit = tk.StringVar()
    submit = tk.Button(window, textvariable=btn_submit, command=submit_home_keyword)
    submit.place(x=120, y=160)

    #创建反馈标签
    result = tk.StringVar()
    result_label = tk.Label(window, width=30, height=1, textvariable=result)
    result_label.place(x=80, y=250)

    window.mainloop()