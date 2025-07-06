# db.py
import pymysql

def get_connection():
    return pymysql.connect(
        host="localhost",
        user="root",
        password="123456",
        database="test01",
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor
    )

# 初始化数据库对象（创建表、触发器、存储过程和视图）
def init_database():
    conn = get_connection()
    with conn.cursor() as cursor:
        # 创建电影表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Movies (
                movie_id INT AUTO_INCREMENT PRIMARY KEY,
                title VARCHAR(200) NOT NULL,
                release_year INT,
                director VARCHAR(100),
                genre VARCHAR(50),
                box_office DECIMAL(15,2),
                description TEXT
            )
        """)
        
        # 创建公司表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Companies (
                company_id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(200) NOT NULL,
                country VARCHAR(100),
                founded_year INT,
                industry VARCHAR(100),
                revenue DECIMAL(15,2),
                description TEXT
            )
        """)

        # 创建日志表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS operation_logs (
                log_id INT AUTO_INCREMENT PRIMARY KEY,
                operation_type VARCHAR(50),
                table_name VARCHAR(50),
                record_id INT,
                operation_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 创建奖项表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Awards (
                award_id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(200) NOT NULL,
                category VARCHAR(100),
                year INT,
                description TEXT
            )
        """)
        
        # 创建人物-奖项关系表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS People_Awards (
                people_award_id INT AUTO_INCREMENT PRIMARY KEY,
                people_id INT,
                award_id INT,
                award_year INT,
                FOREIGN KEY (people_id) REFERENCES People(people_id) ON DELETE CASCADE,
                FOREIGN KEY (award_id) REFERENCES Awards(award_id) ON DELETE CASCADE
            )
        """)
        
        # 创建电影-奖项关系表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Movie_Awards (
                movie_award_id INT AUTO_INCREMENT PRIMARY KEY,
                movie_id INT,
                award_id INT,
                award_year INT,
                FOREIGN KEY (movie_id) REFERENCES Movies(movie_id) ON DELETE CASCADE,
                FOREIGN KEY (award_id) REFERENCES Awards(award_id) ON DELETE CASCADE
            )
        """)
        
        # 创建电影-公司关系表（制作和发行）
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Movie_Companies (
                movie_company_id INT AUTO_INCREMENT PRIMARY KEY,
                movie_id INT,
                company_id INT,
                relationship_type ENUM('制作', '发行') NOT NULL,
                FOREIGN KEY (movie_id) REFERENCES Movies(movie_id) ON DELETE CASCADE,
                FOREIGN KEY (company_id) REFERENCES Companies(company_id) ON DELETE CASCADE
            )
        """)

        # 创建演员-电影关系表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Movie_Actors (
                movie_actor_id INT AUTO_INCREMENT PRIMARY KEY,
                movie_id INT,
                people_id INT,
                role VARCHAR(100),  -- 角色名称
                is_protagonist BOOLEAN DEFAULT FALSE,  -- 是否是主演
                FOREIGN KEY (movie_id) REFERENCES Movies(movie_id) ON DELETE CASCADE,
                FOREIGN KEY (people_id) REFERENCES People(people_id) ON DELETE CASCADE
            )
        """)

        # 创建UI设置表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS UI_Settings (
                setting_id INT AUTO_INCREMENT PRIMARY KEY,
                setting_name VARCHAR(100) NOT NULL,
                setting_value LONGTEXT,
                setting_type VARCHAR(50),
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
        """)

        # 创建触发器 - People表
        cursor.execute("DROP TRIGGER IF EXISTS after_person_insert")
        cursor.execute("""
            CREATE TRIGGER after_person_insert
            AFTER INSERT ON People
            FOR EACH ROW
            BEGIN
                INSERT INTO operation_logs (operation_type, table_name, record_id)
                VALUES ('INSERT', 'People', NEW.people_id);
            END
        """)
        
        # 创建触发器 - Movies表
        cursor.execute("DROP TRIGGER IF EXISTS after_movie_insert")
        cursor.execute("""
            CREATE TRIGGER after_movie_insert
            AFTER INSERT ON Movies
            FOR EACH ROW
            BEGIN
                INSERT INTO operation_logs (operation_type, table_name, record_id)
                VALUES ('INSERT', 'Movies', NEW.movie_id);
            END
        """)
        
        # 创建触发器 - Companies表
        cursor.execute("DROP TRIGGER IF EXISTS after_company_insert")
        cursor.execute("""
            CREATE TRIGGER after_company_insert
            AFTER INSERT ON Companies
            FOR EACH ROW
            BEGIN
                INSERT INTO operation_logs (operation_type, table_name, record_id)
                VALUES ('INSERT', 'Companies', NEW.company_id);
            END
        """)
        
        # 创建触发器 - Awards表
        cursor.execute("DROP TRIGGER IF EXISTS after_award_insert")
        cursor.execute("""
            CREATE TRIGGER after_award_insert
            AFTER INSERT ON Awards
            FOR EACH ROW
            BEGIN
                INSERT INTO operation_logs (operation_type, table_name, record_id)
                VALUES ('INSERT', 'Awards', NEW.award_id);
            END
        """)
        
        # 创建存储过程 - People表
        cursor.execute("DROP PROCEDURE IF EXISTS update_person_info")
        cursor.execute("""
            CREATE PROCEDURE update_person_info(
                IN p_id INT,
                IN p_name VARCHAR(100),
                IN p_country VARCHAR(100),
                IN p_masterpiece TEXT,
                IN p_brief_intro TEXT
            )
            BEGIN
                UPDATE People 
                SET name = p_name,
                    country = p_country,
                    masterpiece = p_masterpiece,
                    brief_intro = p_brief_intro
                WHERE people_id = p_id;
                
                INSERT INTO operation_logs (operation_type, table_name, record_id)
                VALUES ('UPDATE', 'People', p_id);
            END
        """)
        
        # 创建存储过程 - Movies表
        cursor.execute("DROP PROCEDURE IF EXISTS update_movie_info")
        cursor.execute("""
            CREATE PROCEDURE update_movie_info(
                IN m_id INT,
                IN m_title VARCHAR(200),
                IN m_year INT,
                IN m_director VARCHAR(100),
                IN m_genre VARCHAR(50),
                IN m_box_office DECIMAL(15,2),
                IN m_description TEXT
            )
            BEGIN
                UPDATE Movies 
                SET title = m_title,
                    release_year = m_year,
                    director = m_director,
                    genre = m_genre,
                    box_office = m_box_office,
                    description = m_description
                WHERE movie_id = m_id;
                
                INSERT INTO operation_logs (operation_type, table_name, record_id)
                VALUES ('UPDATE', 'Movies', m_id);
            END
        """)
        
        # 创建存储过程 - Companies表
        cursor.execute("DROP PROCEDURE IF EXISTS update_company_info")
        cursor.execute("""
            CREATE PROCEDURE update_company_info(
                IN c_id INT,
                IN c_name VARCHAR(200),
                IN c_country VARCHAR(100),
                IN c_year INT,
                IN c_industry VARCHAR(100),
                IN c_revenue DECIMAL(15,2),
                IN c_description TEXT
            )
            BEGIN
                UPDATE Companies 
                SET name = c_name,
                    country = c_country,
                    founded_year = c_year,
                    industry = c_industry,
                    revenue = c_revenue,
                    description = c_description
                WHERE company_id = c_id;
                
                INSERT INTO operation_logs (operation_type, table_name, record_id)
                VALUES ('UPDATE', 'Companies', c_id);
            END
        """)
        
        # 创建存储过程 - Awards表
        cursor.execute("DROP PROCEDURE IF EXISTS update_award_info")
        cursor.execute("""
            CREATE PROCEDURE update_award_info(
                IN a_id INT,
                IN a_name VARCHAR(200),
                IN a_category VARCHAR(100),
                IN a_year INT,
                IN a_description TEXT
            )
            BEGIN
                UPDATE Awards 
                SET name = a_name,
                    category = a_category,
                    year = a_year,
                    description = a_description
                WHERE award_id = a_id;
                
                INSERT INTO operation_logs (operation_type, table_name, record_id)
                VALUES ('UPDATE', 'Awards', a_id);
            END
        """)
        
        # 创建视图 - People
        cursor.execute("DROP VIEW IF EXISTS people_summary")
        cursor.execute("""
            CREATE VIEW people_summary AS
            SELECT people_id, name, country, masterpiece
            FROM People
        """)
        
        # 创建视图 - Movies
        cursor.execute("DROP VIEW IF EXISTS movies_summary")
        cursor.execute("""
            CREATE VIEW movies_summary AS
            SELECT movie_id, title, release_year, director, genre
            FROM Movies
        """)
        
        # 创建视图 - Companies
        cursor.execute("DROP VIEW IF EXISTS companies_summary")
        cursor.execute("""
            CREATE VIEW companies_summary AS
            SELECT company_id, name, country, industry, founded_year
            FROM Companies
        """)
        
        # 创建视图 - Awards
        cursor.execute("DROP VIEW IF EXISTS awards_summary")
        cursor.execute("""
            CREATE VIEW awards_summary AS
            SELECT award_id, name, category, year
            FROM Awards
        """)
        
        # 创建获奖情况视图（人物）
        cursor.execute("DROP VIEW IF EXISTS people_awards_view")
        cursor.execute("""
            CREATE VIEW people_awards_view AS
            SELECT 
                p.people_id,
                p.name as person_name,
                a.name as award_name,
                a.category as award_category,
                pa.award_year
            FROM People p
            JOIN People_Awards pa ON p.people_id = pa.people_id
            JOIN Awards a ON pa.award_id = a.award_id
        """)
        
        # 创建获奖情况视图（电影）
        cursor.execute("DROP VIEW IF EXISTS movie_awards_view")
        cursor.execute("""
            CREATE VIEW movie_awards_view AS
            SELECT 
                m.movie_id,
                m.title as movie_title,
                a.name as award_name,
                a.category as award_category,
                ma.award_year
            FROM Movies m
            JOIN Movie_Awards ma ON m.movie_id = ma.movie_id
            JOIN Awards a ON ma.award_id = a.award_id
        """)
        
        # 创建电影公司关系视图
        cursor.execute("DROP VIEW IF EXISTS movie_companies_view")
        cursor.execute("""
            CREATE VIEW movie_companies_view AS
            SELECT 
                m.movie_id,
                m.title as movie_title,
                c.name as company_name,
                mc.relationship_type
            FROM Movies m
            JOIN Movie_Companies mc ON m.movie_id = mc.movie_id
            JOIN Companies c ON mc.company_id = c.company_id
        """)
        
        # 创建演员参演情况视图
        cursor.execute("DROP VIEW IF EXISTS movie_actors_view")
        cursor.execute("""
            CREATE VIEW movie_actors_view AS
            SELECT 
                m.movie_id,
                m.title as movie_title,
                p.people_id,
                p.name as actor_name,
                ma.role,
                ma.is_protagonist
            FROM Movies m
            JOIN Movie_Actors ma ON m.movie_id = ma.movie_id
            JOIN People p ON ma.people_id = p.people_id
        """)

        # 创建人物获奖汇总视图
        cursor.execute("DROP VIEW IF EXISTS people_awards_summary")
        cursor.execute("""
            CREATE VIEW people_awards_summary AS
            SELECT 
                p.people_id,
                p.name,
                GROUP_CONCAT(
                    CONCAT(a.name, ' (', pa.award_year, ')')
                    ORDER BY pa.award_year DESC
                    SEPARATOR '; '
                ) as awards_list,
                COUNT(*) as total_awards
            FROM People p
            LEFT JOIN People_Awards pa ON p.people_id = pa.people_id
            LEFT JOIN Awards a ON pa.award_id = a.award_id
            GROUP BY p.people_id, p.name
        """)

        # 创建电影获奖汇总视图
        cursor.execute("DROP VIEW IF EXISTS movies_awards_summary")
        cursor.execute("""
            CREATE VIEW movies_awards_summary AS
            SELECT 
                m.movie_id,
                m.title,
                GROUP_CONCAT(
                    CONCAT(a.name, ' (', ma.award_year, ')')
                    ORDER BY ma.award_year DESC
                    SEPARATOR '; '
                ) as awards_list,
                COUNT(*) as total_awards
            FROM Movies m
            LEFT JOIN Movie_Awards ma ON m.movie_id = ma.movie_id
            LEFT JOIN Awards a ON ma.award_id = a.award_id
            GROUP BY m.movie_id, m.title
        """)

    conn.commit()
    conn.close()

# Movies表操作
def fetch_all_movies():
    conn = get_connection()
    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM Movies")
        result = cursor.fetchall()
    conn.close()
    return result

def insert_movie(title, release_year, director, genre, box_office, description):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            sql = """INSERT INTO Movies (title, release_year, director, genre, box_office, description) 
                    VALUES (%s, %s, %s, %s, %s, %s)"""
            cursor.execute(sql, (title, release_year, director, genre, box_office, description))
        conn.commit()
    finally:
        conn.close()

def update_movie_with_procedure(movie_id, title, release_year, director, genre, box_office, description):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("CALL update_movie_info(%s, %s, %s, %s, %s, %s, %s)",
                         (movie_id, title, release_year, director, genre, box_office, description))
        conn.commit()
    finally:
        conn.close()

def delete_movie_with_transaction(movie_id):
    conn = get_connection()
    try:
        conn.begin()
        with conn.cursor() as cursor:
            cursor.execute("INSERT INTO operation_logs (operation_type, table_name, record_id) VALUES ('DELETE', 'Movies', %s)", (movie_id,))
            cursor.execute("DELETE FROM Movies WHERE movie_id = %s", (movie_id,))
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def get_movies_summary():
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM movies_summary")
            result = cursor.fetchall()
        return result
    finally:
        conn.close()

# Companies表操作
def fetch_all_companies():
    conn = get_connection()
    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM Companies")
        result = cursor.fetchall()
    conn.close()
    return result

def insert_company(name, country, founded_year, industry, revenue, description):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            sql = """INSERT INTO Companies (name, country, founded_year, industry, revenue, description) 
                    VALUES (%s, %s, %s, %s, %s, %s)"""
            cursor.execute(sql, (name, country, founded_year, industry, revenue, description))
        conn.commit()
    finally:
        conn.close()

def update_company_with_procedure(company_id, name, country, founded_year, industry, revenue, description):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("CALL update_company_info(%s, %s, %s, %s, %s, %s, %s)",
                         (company_id, name, country, founded_year, industry, revenue, description))
        conn.commit()
    finally:
        conn.close()

def delete_company_with_transaction(company_id):
    conn = get_connection()
    try:
        conn.begin()
        with conn.cursor() as cursor:
            cursor.execute("INSERT INTO operation_logs (operation_type, table_name, record_id) VALUES ('DELETE', 'Companies', %s)", (company_id,))
            cursor.execute("DELETE FROM Companies WHERE company_id = %s", (company_id,))
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def get_companies_summary():
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM companies_summary")
            result = cursor.fetchall()
        return result
    finally:
        conn.close()

# 保留原有的People表操作函数
def fetch_all_people():
    conn = get_connection()
    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM People")
        result = cursor.fetchall()
    conn.close()
    return result

def insert_person(name, country, masterpiece, brief_intro):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            sql = "INSERT INTO People (name, country, masterpiece, brief_intro) VALUES (%s, %s, %s, %s)"
            cursor.execute(sql, (name, country, masterpiece, brief_intro))
        conn.commit()
    finally:
        conn.close()

def update_person_with_procedure(people_id, name, country, masterpiece, brief_intro):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("CALL update_person_info(%s, %s, %s, %s, %s)",
                         (people_id, name, country, masterpiece, brief_intro))
        conn.commit()
    finally:
        conn.close()

def delete_person_with_transaction(people_id):
    conn = get_connection()
    try:
        conn.begin()
        with conn.cursor() as cursor:
            cursor.execute("INSERT INTO operation_logs (operation_type, table_name, record_id) VALUES ('DELETE', 'People', %s)", (people_id,))
            cursor.execute("DELETE FROM People WHERE people_id = %s", (people_id,))
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def get_people_summary():
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM people_summary")
            result = cursor.fetchall()
        return result
    finally:
        conn.close()

def get_operation_logs():
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM operation_logs ORDER BY operation_time DESC")
            result = cursor.fetchall()
        return result
    finally:
        conn.close()

# 奖项相关操作
def fetch_all_awards():
    conn = get_connection()
    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM Awards")
        result = cursor.fetchall()
    conn.close()
    return result

def insert_award(name, category, year, description):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            sql = """INSERT INTO Awards (name, category, year, description) 
                    VALUES (%s, %s, %s, %s)"""
            cursor.execute(sql, (name, category, year, description))
        conn.commit()
    finally:
        conn.close()

def update_award_with_procedure(award_id, name, category, year, description):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("CALL update_award_info(%s, %s, %s, %s, %s)",
                         (award_id, name, category, year, description))
        conn.commit()
    finally:
        conn.close()

def delete_award_with_transaction(award_id):
    conn = get_connection()
    try:
        conn.begin()
        with conn.cursor() as cursor:
            cursor.execute("INSERT INTO operation_logs (operation_type, table_name, record_id) VALUES ('DELETE', 'Awards', %s)", (award_id,))
            cursor.execute("DELETE FROM Awards WHERE award_id = %s", (award_id,))
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

# 关系操作函数
def add_person_award(people_id, award_id, award_year):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            sql = """INSERT INTO People_Awards (people_id, award_id, award_year) 
                    VALUES (%s, %s, %s)"""
            cursor.execute(sql, (people_id, award_id, award_year))
        conn.commit()
    finally:
        conn.close()

def add_movie_award(movie_id, award_id, award_year):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            sql = """INSERT INTO Movie_Awards (movie_id, award_id, award_year) 
                    VALUES (%s, %s, %s)"""
            cursor.execute(sql, (movie_id, award_id, award_year))
        conn.commit()
    finally:
        conn.close()

def add_movie_company(movie_id, company_id, relationship_type):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            sql = """INSERT INTO Movie_Companies (movie_id, company_id, relationship_type) 
                    VALUES (%s, %s, %s)"""
            cursor.execute(sql, (movie_id, company_id, relationship_type))
        conn.commit()
    finally:
        conn.close()

# 获取关系数据
def get_person_awards(people_id):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT * FROM people_awards_view
                WHERE people_id = %s
            """, (people_id,))
            return cursor.fetchall()
    finally:
        conn.close()

def get_movie_awards(movie_id):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT * FROM movie_awards_view
                WHERE movie_id = %s
            """, (movie_id,))
            return cursor.fetchall()
    finally:
        conn.close()

def get_movie_companies(movie_id):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT * FROM movie_companies_view
                WHERE movie_id = %s
            """, (movie_id,))
            return cursor.fetchall()
    finally:
        conn.close()

# 添加新的关系操作函数
def add_movie_actor(movie_id, people_id, role, is_protagonist=False):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            sql = """INSERT INTO Movie_Actors (movie_id, people_id, role, is_protagonist) 
                    VALUES (%s, %s, %s, %s)"""
            cursor.execute(sql, (movie_id, people_id, role, is_protagonist))
        conn.commit()
    finally:
        conn.close()

def get_movie_actors(movie_id):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT * FROM movie_actors_view
                WHERE movie_id = %s
                ORDER BY is_protagonist DESC, actor_name
            """, (movie_id,))
            return cursor.fetchall()
    finally:
        conn.close()

def get_actor_movies(people_id):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT * FROM movie_actors_view
                WHERE people_id = %s
                ORDER BY movie_title
            """, (people_id,))
            return cursor.fetchall()
    finally:
        conn.close()

# 获取获奖汇总信息
def get_person_awards_summary(people_id=None):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            if people_id:
                cursor.execute("SELECT * FROM people_awards_summary WHERE people_id = %s", (people_id,))
            else:
                cursor.execute("SELECT * FROM people_awards_summary ORDER BY total_awards DESC")
            return cursor.fetchall()
    finally:
        conn.close()

def get_movie_awards_summary(movie_id=None):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            if movie_id:
                cursor.execute("SELECT * FROM movies_awards_summary WHERE movie_id = %s", (movie_id,))
            else:
                cursor.execute("SELECT * FROM movies_awards_summary ORDER BY total_awards DESC")
            return cursor.fetchall()
    finally:
        conn.close()

# 获取综合信息
def get_person_details(people_id):
    """获取人物的综合信息，包括获奖情况和参演作品"""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            # 基本信息
            cursor.execute("SELECT * FROM People WHERE people_id = %s", (people_id,))
            person = cursor.fetchone()
            if not person:
                return None

            # 获奖信息
            cursor.execute("""
                SELECT 
                    a.name as award_name,
                    a.category as award_category,
                    pa.award_year
                FROM People_Awards pa
                JOIN Awards a ON pa.award_id = a.award_id
                WHERE pa.people_id = %s
                ORDER BY pa.award_year DESC
            """, (people_id,))
            awards = cursor.fetchall()

            # 参演作品
            cursor.execute("""
                SELECT 
                    m.title,
                    ma.role,
                    ma.is_protagonist
                FROM Movie_Actors ma
                JOIN Movies m ON ma.movie_id = m.movie_id
                WHERE ma.people_id = %s
                ORDER BY m.release_year DESC
            """, (people_id,))
            movies = cursor.fetchall()

            return {
                'basic_info': person,
                'awards': awards,
                'movies': movies
            }
    finally:
        conn.close()

def get_movie_details(movie_id):
    """获取电影的综合信息，包括获奖情况、演员阵容和相关公司"""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            # 基本信息
            cursor.execute("SELECT * FROM Movies WHERE movie_id = %s", (movie_id,))
            movie = cursor.fetchone()
            if not movie:
                return None

            # 获奖信息
            cursor.execute("""
                SELECT 
                    a.name as award_name,
                    a.category as award_category,
                    ma.award_year
                FROM Movie_Awards ma
                JOIN Awards a ON ma.award_id = a.award_id
                WHERE ma.movie_id = %s
                ORDER BY ma.award_year DESC
            """, (movie_id,))
            awards = cursor.fetchall()

            # 演员阵容
            cursor.execute("""
                SELECT 
                    p.name,
                    ma.role,
                    ma.is_protagonist
                FROM Movie_Actors ma
                JOIN People p ON ma.people_id = p.people_id
                WHERE ma.movie_id = %s
                ORDER BY ma.is_protagonist DESC, p.name
            """, (movie_id,))
            actors = cursor.fetchall()

            # 相关公司
            cursor.execute("""
                SELECT 
                    c.name,
                    mc.relationship_type
                FROM Movie_Companies mc
                JOIN Companies c ON mc.company_id = c.company_id
                WHERE mc.movie_id = %s
            """, (movie_id,))
            companies = cursor.fetchall()

            return {
                'basic_info': movie,
                'awards': awards,
                'actors': actors,
                'companies': companies
            }
    finally:
        conn.close()

# UI设置相关函数
def save_ui_setting(setting_name, setting_value, setting_type="string", description=None):
    """保存UI设置到数据库"""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            sql = """INSERT INTO UI_Settings (setting_name, setting_value, setting_type, description)
                    VALUES (%s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE 
                    setting_value = VALUES(setting_value),
                    setting_type = VALUES(setting_type),
                    description = VALUES(description)"""
            cursor.execute(sql, (setting_name, setting_value, setting_type, description))
        conn.commit()
    finally:
        conn.close()

def get_ui_setting(setting_name):
    """获取UI设置"""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM UI_Settings WHERE setting_name = %s", (setting_name,))
            return cursor.fetchone()
    finally:
        conn.close()

def get_all_ui_settings():
    """获取所有UI设置"""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM UI_Settings ORDER BY setting_name")
            return cursor.fetchall()
    finally:
        conn.close()

def delete_ui_setting(setting_name):
    """删除UI设置"""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM UI_Settings WHERE setting_name = %s", (setting_name,))
        conn.commit()
    finally:
        conn.close()
