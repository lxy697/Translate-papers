import os
import sqlite3

from ai import AI_API

ai_api = AI_API("<APIkey>", "https://api.deepseek.com", "deepseek-chat", 8192)#在这里填写你的APIkey


def translate(folder_path):
    text_output_md = os.path.join(folder_path, "full.md")#输入md文件
    sql_output = os.path.join(folder_path, 'database.db')#数据库文件
    text_output_cn = os.path.join(folder_path, "output_text_cn.md")#输出中文
    text_output_en = os.path.join(folder_path, "output_text_en.md")#输出英文
    

    conn = sqlite3.connect(sql_output) 
    cursor = conn.cursor()   # 创建数据库连接并生成数据库文件


    try:#如果已经翻译完了则不继续执行函数
        cursor.execute("SELECT isdone FROM raw WHERE id=2")
        result = cursor.fetchone()  # 获取查询结果
        if result is not None:
            isdone = result[0]  # 取出 isdone 值
            if isdone == 1:
                return 0  # 终止函数
        else:
            print("发现未翻译的内容")
    except sqlite3.Error as e:
        print(f"Database error: {e}")


    with open(text_output_md, "r", encoding="utf-8") as f:
        text_md = f.read()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='raw';")
    if not cursor.fetchone():  # 如果表不存在
        #print("创建数据库表1")
        cursor.execute("CREATE TABLE IF NOT EXISTS raw (id INTEGER PRIMARY KEY,txt TEXT,isdone INTEGER)")
        cursor.executemany("INSERT INTO raw (id, txt, isdone) VALUES (?, ?, ?)", 
        [
            (1, "", 0),
            (2, "", 0)
        ])
        cursor.execute("UPDATE raw SET txt = ?, isdone = ? WHERE id = 1", (text_md, 1))
        cursor.execute("UPDATE raw SET txt = ?, isdone = ? WHERE id = 2", ("is_over", 0))
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='txt_split';")
    if not cursor.fetchone():  # 如果表不存在
        #print("创建数据库表2")
        cursor.execute("CREATE TABLE IF NOT EXISTS txt_split (id INTEGER PRIMARY KEY,txt TEXT,txt_ch TEXT,isdone INTEGER)")
        lines = text_md.splitlines()
        for line in lines:# 按行插入数据到数据库
            line = line.strip()  # 去除每行的前后空格
            cursor.execute("INSERT INTO txt_split (txt, txt_ch, isdone) VALUES (?, ?, ?)", (line, '', 0))

    print("开始分段翻译")
    cursor.execute("SELECT id, txt FROM txt_split")
    rows = cursor.fetchall()
    special_chars = ("#", "$", "[", "]", "!", "&", "*", "+", "=", "-", "_", ":", ";", "'", '"', ",", ".", "<", ">", "/", "?")
    print("正在去除特殊行")
    for row in rows: # 特殊字符不翻译
        id, txt = row
        if txt.startswith(special_chars) or not txt.strip():
            txt_ch = txt
            cursor.execute("UPDATE txt_split SET txt_ch = ?, isdone = 1 WHERE id = ?", (txt_ch, id))
            conn.commit()
    print("正在去除公式行")
    rows_list = list(rows)       
    for i in range(1, len(rows_list) - 2): # 公式不翻译
        current_row = rows_list[i]# 获取当前行及其上下两行索引
        prev_row = rows_list[i - 1]
        next_row = rows_list[i + 1]
        current_id, current_txt = current_row# 获取当前行及其上下两行内容
        prev_id, prev_txt = prev_row
        next_id, next_txt = next_row
        if prev_txt.startswith("$") and next_txt.startswith("$"):# 判断上下两行是否都以特殊字符开头
            txt_ch = current_txt
            cursor.execute("UPDATE txt_split SET txt_ch = ?, isdone = 1 WHERE id = ?", (current_txt, current_id))
            conn.commit()
            
    print("正在翻译正文") 
    cursor.execute("SELECT id, txt FROM txt_split WHERE isdone = 0")  
    rows = cursor.fetchall()   
    for row in rows: # 特殊字符不翻译
        id, txt = row
        txt_ch = ai_api.chatonce(f"请用学术语言将以下英文内容准确翻译成中文：{txt}")
        if txt_ch != "API失效":
            cursor.execute("UPDATE txt_split SET txt_ch = ?, isdone = 1 WHERE id = ?", (txt_ch, id))
            conn.commit()
            print("翻译成功+1")

    cursor.execute("SELECT * FROM txt_split WHERE isdone = 0")  
    rows = cursor.fetchall()  
    if not rows:
        print("翻译完毕")
        cursor.execute("SELECT id, txt_ch, txt FROM txt_split")  
        rows = cursor.fetchall()  
        final_text_cn = ""
        final_text_en = ""
        for row in rows:# 遍历每一行
            txt_cn = row[1].replace("\n", "").replace("\r", "")  # txt_cn在查询结果的第二列
            txt_en = row[2].replace("\n", "").replace("\r", "")  # txt_en在查询结果的第三列
            final_text_cn += txt_cn + "\n\n"  # 在每个txt_cn后面添加两行回车
            final_text_en += txt_en + "\n\n"  # 在每个txt_en后面添加两行回车
        with open(text_output_cn, "w", encoding="utf-8") as f:
            f.write(final_text_cn)
        with open(text_output_en, "w", encoding="utf-8") as f:
            f.write(final_text_en)
        print("正在输出翻译结果")

        cursor.execute("UPDATE raw SET isdone = ? WHERE id = 2", (1,))



    # 提交事务并关闭连接
    conn.commit()
    conn.close()



def main():

    paper_dir = os.path.join(os.getcwd(), "paper")
    subfolders = [
        os.path.join(paper_dir, folder)
        for folder in os.listdir(paper_dir)
        if os.path.isdir(os.path.join(paper_dir, folder))  # 确保是文件夹
    ]
    for folder in subfolders:
        folder_name = os.path.basename(folder)  # 获取文件夹名
        if not folder_name.startswith(('.', '#')):  # 排除以 . 或 # 开头的文件夹
            translate(folder)
    


if __name__ == "__main__":
    main()



