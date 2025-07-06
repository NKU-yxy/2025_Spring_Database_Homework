from db import init_database

def main():
    print("开始初始化数据库...")
    init_database()
    print("数据库初始化完成！")

if __name__ == '__main__':
    main() 