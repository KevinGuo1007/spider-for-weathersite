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

# 设置自定义的请求头（伪装成正常浏览器）
chrome_options = Options()
chrome_options.add_argument('--ignore-certificate-errors')  # 忽略 SSL 错误
chrome_options.add_argument('--disable-extensions')  # 禁用扩展
# chrome_options.add_argument('--headless')  # 无头模式（可选）
chrome_options.add_argument('--disable-gpu')  # 禁用 GPU（可选）
chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36')

# 启动 Chrome 浏览器
browser = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

# 打开天气页面
browser.get('https://weather.com/zh-CN/weather/tenday/l/9be95861a38eec68819ff6d9e18a31947af99deeec9008bf76bb8a75ce86972a')
time.sleep(5)


# 关闭弹窗或切换到 iframe
try:
    # 切换到 iframe，如果弹窗出现
    iframe = WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.TAG_NAME, "iframe")))
    browser.switch_to.frame(iframe)  # 切换到 iframe
    print("Switched to iframe.")
    # 你可以在这里做任何关闭弹窗的操作（如点击“同意”按钮等）
except:
    # 如果没有弹窗，则继续执行
    print("No iframe found.")

# 增加调试：检查页面 HTML
print("Page HTML: ", browser.page_source[:500])  # 打印页面的前 500 个字符

    # 定位需要点击的 <svg> 元素，使用提供的属性
    # svg_element = browser.find_element(By.CSS_SELECTOR, 'svg[name="caret-up"][data-testid="Icon"]')

# 下面两种定位的区别：两种定位方式分别使用了 CSS选择器 和 XPath，
#CSS选择器：
#简洁、性能好、广泛支持。
#适用于根据ID、类名、属性等进行简单查找。
#无法像XPath那样查找文本内容或者复杂的层级结构。
#XPath：
#更加灵活，适用于查找复杂的结构、文本内容和节点关系。
#性能可能较差，语法比CSS选择器复杂。
#可以通过路径定位页面元素，支持更多条件（如兄弟节点、父节点、文本内容等）。

# 点击接受cookie并保存我的选择
# accept_button = browser.find_element(By.CSS_SELECTOR, '')

# 定位所有包含 "接受" 文本的按钮
accept_buttons = WebDriverWait(browser, 10).until(
    EC.presence_of_all_elements_located((By.XPATH, "//button[normalize-space(text())='接受']"))
)

# 遍历并点击每个按钮
for idx, button in enumerate(accept_buttons):
    print(f"Clicking accept button {idx + 1}.")
    button.click()
    time.sleep(1)  # 可根据需要调整间隔

# 定位并点击 "保存我的选择" 按钮
save_button = WebDriverWait(browser, 10).until(
    EC.presence_of_element_located((By.XPATH, "//button[@title='保存我的选择']"))
)
save_button.click()
time.sleep(5)

# 定位在 id="detailIndex0" 的 <details> 元素下的 <svg> 元素
# <svg set="ui" name="caret-up" class="Icon--icon--ySD-o Disclosure--SummaryIcon--ldYIx DaypartDetails--SummaryIcon--1UVaq" theme data-testid="Icon" viewBox="0 0 24 24">
svg_element = browser.find_element(By.CSS_SELECTOR, 'details#detailIndex0 svg[name="caret-up"][data-testid="Icon"]')

# 滚动到目标元素
browser.execute_script("arguments[0].scrollIntoView(true);", svg_element)
time.sleep(1)  # 等待滚动完成

# 等待元素可点击
wait = WebDriverWait(browser, 10)
svg_element = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'svg[name="caret-up"][data-testid="Icon"]')))

# 点击 <svg> 元素
svg_element.click()
time.sleep(2)

# 从 detailIndex0 到 detailIndex14
for i in range(15):  # 从 0 到 14
    if i == 0:
        # 定位 id="detailIndex0" 的 <details> 元素下的 <div> 元素，具有 data-testid="DetailsSummary"
        details_element = browser.find_element(By.CSS_SELECTOR, 'details#detailIndex0 div[data-testid="DetailsSummary"]')

        # 打印 id="detailIndex0" 的 <details> 元素的内容
        if details_element:
            print(f"Details Element Text (detailIndex{i}): ", details_element.text)  # 打印匹配元素的文本内容
        
    else:
        # 对于 detailIndex1 到 detailIndex14，只定位 <details> 元素
        details_element = browser.find_element(By.CSS_SELECTOR, f'details#detailIndex{i}')
        
        # 打印匹配的 <details> 元素的文本内容
        if details_element:
            print(f"Details Element Text (detailIndex{i}): ", details_element.text)

# 关闭浏览器
browser.close()

