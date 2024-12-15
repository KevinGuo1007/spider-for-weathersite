import pymysql
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By  # 导入 By
import time
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from concurrent.futures import ThreadPoolExecutor

def main():
    # 获取省份和市区输入
    locations = input("请输入省份和市区（如：北京+北京，广东省+广州市，浙江省杭州市）：").split('，')

    # 使用线程池进行并行处理
    with ThreadPoolExecutor(max_workers=5) as executor:
        # 为每个城市/省份对提交一个爬取任务
        futures = [executor.submit(spider, location.strip()) for location in locations]

        # 等待所有线程完成任务
        for future in futures:
            future.result()  # 阻塞，等待线程的返回值（如果有的话）

# 爬虫
def spider(location):
# 设置自定义的请求头（伪装成正常浏览器）
    chrome_options = Options()
    chrome_options.add_argument('--ignore-certificate-errors')  # 忽略 SSL 错误
    chrome_options.add_argument('--disable-extensions')  # 禁用扩展
    chrome_options.add_argument('--headless')  # 无头模式（可选）
    chrome_options.add_argument('--disable-gpu')  # 禁用 GPU（可选）
    # chrome_options.add_argument("--no-sandbox")  # 跳过沙盒模式
    chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36')

    # 启动 Chrome 浏览器
    # 使用 Service 来指定 ChromeDriver 路径
    service = Service(r"E:\Code-Libary\Python\CrawlerPro\chromedriver-win64\chromedriver.exe")
    browser = webdriver.Chrome(service=service, options=chrome_options)
    chrome_options.set_capability("pageLoadStrategy", "eager")  # 设置为 'normal'、'eager' 或 'none'

    # 打开天气页面
    browser.get('https://weather.com/zh-CN/weather/today/l/CHXX0008:1:CH')
    time.sleep(2)

    # # 模拟点击解决 cookie 弹窗
    # # 调试：打印当前页面源代码，查看是否存在“接受”按钮
    # print(browser.page_source)

    # # 定位所有包含 "接受" 文本的按钮
    # accept_buttons = WebDriverWait(browser, 20).until(EC.presence_of_all_elements_located((By.XPATH, "//button[normalize-space(text())='接受']")))

    # # 遍历并点击每个按钮
    # for idx, button in enumerate(accept_buttons):
    #     print(f"Clicking accept button {idx + 1}.")
    #     button.click()
    #     time.sleep(1)  # 可根据需要调整间隔

    # # 定位并点击 "保存我的选择" 按钮
    # save_button = WebDriverWait(browser, 10).until(
    #     EC.presence_of_element_located((By.XPATH, "//button[@title='保存我的选择']"))
    # )
    # save_button.click()

    # 定位 placeholder="搜索城市或邮编" 的 <input> 元素·并将location输入
    input_element = browser.find_element(By.CSS_SELECTOR, 'input[placeholder="搜索城市或邮编"]')
    input_element.send_keys(location)

    try:
        # 等待输入框出现并获取元素
        input_element = WebDriverWait(browser, 5).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "input[aria-controls='LocationSearch_listbox']"))
        )
        
        # 获取输入框的位置和尺寸
        input_location = input_element.location
        input_size = input_element.size

        # 计算点击位置（以输入框的正中间偏下200像素）
        click_x = input_location['x'] + input_size['width'] / 2
        click_y = input_location['y'] + input_size['height'] / 2 + 30  # 向下偏移30像素
        time.sleep(1)
        # 使用 ActionChains 进行鼠标点击
        actions = ActionChains(browser)
        actions.move_to_element_with_offset(input_element, click_x - input_location['x'], click_y - input_location['y'])
        actions.click().perform()
        # 通过 JavaScript 隐藏广告元素
        ad_elements = browser.find_elements(By.CSS_SELECTOR, "div.Card--content--I0ayG")
        for ad in ad_elements:
            browser.execute_script("arguments[0].style.display = 'none';", ad)

    except Exception as e:
        print(f"Error: {e}")

    # 定位 data-from-string="localsuiteNav_3_10 天" 的 <a> 元素并点击
    a_element = browser.find_element(By.CSS_SELECTOR, 'a[data-from-string="localsuiteNav_3_10 天"]')
    a_element.click()

    # 定位在 id="detailIndex0" 的 <details> 元素下的 <svg> 元素
    # <svg set="ui" name="caret-up" class="Icon--icon--ySD-o Disclosure--SummaryIcon--ldYIx DaypartDetails--SummaryIcon--1UVaq" theme data-testid="Icon" viewBox="0 0 24 24">
    svg_element = browser.find_element(By.CSS_SELECTOR, 'details#detailIndex0 svg[name="caret-up"][data-testid="Icon"]')

    # 滚动到目标元素
    browser.execute_script("arguments[0].scrollIntoView(true);", svg_element)
    time.sleep(1)  # 等待滚动完成

    # 查找等待元素并点击
    wait = WebDriverWait(browser, 10)
    svg_element = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'svg[name="caret-up"][data-testid="Icon"]')))
    svg_element.click()

    # 初始化一个列表，用于存储每个 detailIndex 的天气数据
    weather_data_list = []

    # 从 detailIndex0 到 detailIndex14
    for i in range(15):  # 从 0 到 14
        if i == 0:
            # 定位 id="detailIndex0" 的 <details> 元素下的 <div> 元素，具有 data-testid="DetailsSummary"
            details_element = browser.find_element(By.CSS_SELECTOR, 'details#detailIndex0 div[data-testid="DetailsSummary"]')

            # 打印 id="detailIndex0" 的 <details> 元素的内容
            if details_element:
                print(f"Details Element Text (detailIndex{i}): ", details_element.text)  # 打印匹配元素的文本内容
                weather_data_list.append(details_element.text)  # 将文本内容添加到列表中
        
        else:
            # 对于 detailIndex1 到 detailIndex14，只定位 <details> 元素
            details_element = browser.find_element(By.CSS_SELECTOR, f'details#detailIndex{i}')
            
            # 打印匹配的 <details> 元素的文本内容
            if details_element:
                print(f"Details Element Text (detailIndex{i}): ", details_element.text)
                weather_data_list.append(details_element.text)  # 将文本内容添加到列表中

    # 获取当前天气预报的城市名称
    city_name = browser.find_element(By.CSS_SELECTOR, 'span[data-testid="PresentationName"].LocationPageTitle--PresentationName--YxTV7').text

    # 调用 database 函数将所有爬取的天气数据存入数据库
    if weather_data_list:
        print(city_name)
        database(city_name, weather_data_list)
    else:
        print("No weather data was fetched.")

# 数据清洗
def process_weather_data(weather_data):
    # 按 \n 分割数据
    parts = weather_data.split('\n')

    # 去除  '/' 符号
    for i in range(len(parts)):
        parts[i] = parts[i].replace('/', '')

    # 根据数据的顺序命名
    date = parts[0]
    weather = parts[1]
    maxtemperature = parts[2]
    mintemperature = parts[3]
    humidity = parts[4]
    windy = parts[5]

    # 返回一个字典，包含各个字段
    return {
        'date': date,
        'weather': weather,
        'maxtemperature': maxtemperature,
        'mintemperature': mintemperature,
        'humidity': humidity,
        'windy': windy
    }

def database(location, weather_data_list):

    processed_data = [process_weather_data(data) for data in weather_data_list]
    # 输出结果
    for entry in processed_data:
        print(entry)

    # 连接MySQL数据库
    conn = pymysql.connect(
        host='localhost',
        user='root',
        password='20050123gyq',
        database='spider_weather_db'
    )
    cursor = conn.cursor()
    
    # 删除已有的表格
    drop_table_query = f"DROP TABLE IF EXISTS `{location}`;"
    cursor.execute(drop_table_query)

    # 创建表格（表名为用户输入的省份+市区），并添加时间戳字段
    create_table_query = f"""
    CREATE TABLE `{location}` (
        id INT AUTO_INCREMENT PRIMARY KEY,
        date VARCHAR(255),
        weather VARCHAR(255),
        maxtemperature VARCHAR(255),
        mintemperature VARCHAR(255),
        humidity VARCHAR(255),
        windy VARCHAR(255),
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP  -- 时间戳字段
    )
    """
    cursor.execute(create_table_query)


    # 批量插入数据
    insert_query = f"""
    INSERT INTO `{location}` (date, weather, maxtemperature, mintemperature, humidity, windy) 
    VALUES (%s, %s, %s, %s, %s, %s)
    """
    
    # 使用 executemany 插入批量数据
    cursor.executemany(insert_query, [
        (entry['date'], entry['weather'], entry['maxtemperature'], entry['mintemperature'], entry['humidity'], entry['windy'])
        for entry in processed_data
    ])


    # 提交事务
    conn.commit()
    
    # 查询并打印整个表单
    cursor.execute(f"SELECT * FROM `{location}`")
    rows = cursor.fetchall()
    for row in rows:
        print(row)
    
    # 关闭连接
    cursor.close()
    conn.close()

if __name__ == "__main__":
    main()
