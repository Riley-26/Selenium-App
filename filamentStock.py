from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json
import os

service = Service(executable_path="chromedriver.exe")
driver = webdriver.Chrome(service=service)

driver.get("https://bambulab.com/en")

filaments = {}

def runBot():

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//div[contains(text(), 'Filament')]"))
    )

    filament_btn = driver.find_element(By.XPATH, "//div[contains(text(), 'Filament')]")
    filament_btn.click()

    #Shop filament button

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "a.item.portal-css-0"))
    )

    shop_filament_btn = driver.find_element(By.CSS_SELECTOR, "a.item.portal-css-0")
    shop_filament_btn.click()

    #Change window

    for window_handle in driver.window_handles:
        if window_handle != driver.current_window_handle:
            driver.switch_to.window(window_handle)
            break

    #Global language button

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "button.shop-show"))
    )

    global_btn = driver.find_element(By.CSS_SELECTOR, "button.shop-show")
    global_btn.click()

    #Change to UK store

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//a[contains(text(), 'UK')]"))
    )

    time.sleep(1)

    language_btn = driver.find_element(By.XPATH, "//a[contains(text(), 'UK')]")
    language_btn.click()

    #Get all product items 16/12/2023 and append to a file to compare future searches to

    filaments = {}
    while True:
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "Grid__Cell"))
        )

        all_products = driver.find_elements(By.CLASS_NAME, "Grid__Cell")
        for i in range(len(all_products)):
            each_filament = {}
            
            WebDriverWait(driver, 5).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.ProductItem__Info"))
            )
            
            current_filament = driver.find_elements(By.CSS_SELECTOR, "div.ProductItem__Info")[i]
            
            filament_name = current_filament.find_elements(By.CSS_SELECTOR, "h2.ProductItem__Title.Heading > a")[0].get_attribute("innerHTML")
            
            filament_price = current_filament.find_elements(By.CSS_SELECTOR, "div.ProductItem__PriceList.Heading > span")[0].get_attribute("innerHTML")
            filament_price = filament_price.split("£")[1].split(" ")[0]
            
            WebDriverWait(driver, 5).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "variant-swatch-king > div.swatches > div"))
            )
            
            try:
                filament_colours_path = current_filament.find_elements(By.CSS_SELECTOR, "variant-swatch-king > div.swatches > div")
                filament_option = None
                for i in filament_colours_path:
                    if i.get_attribute("option-name") == "Color":
                        filament_option = i
            
                filament_colours = filament_option.find_elements(By.CSS_SELECTOR, "div.swatch-single > fieldset > ul.swatch-view > li")
                filament_colours_list = []
                
                for j in range(len(filament_colours)):
                    filament_colour_name = filament_colours[j].get_attribute("aria-label")
                    if "Sold Out" in filament_colour_name:
                        filament_instock = "Out of stock"
                    else:
                        filament_instock = "In stock"
                    filament_colours_list.append([filament_colour_name.split(" (")[0], filament_instock])
                    
                each_filament["price"] = filament_price
                each_filament["colours"] = filament_colours_list
                filaments[filament_name] = each_filament
                
            except (IndexError, AttributeError):
                each_filament["price"] = filament_price
                each_filament["colours"] = []
                filaments[filament_name] = each_filament
            
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.Pagination__Nav"))
        )
        
        next_page = driver.find_elements(By.CSS_SELECTOR, "div.Pagination__Nav > a")
            
        if next_page[-1].get_attribute("title") == "Next page":
            next_page[-1].click()
            time.sleep(2)
        else:
            break
        
    #Use information in "filaments" to update a json file
    sibling_path = os.path.join(os.path.dirname(__file__))
    json_file_path = os.path.join(sibling_path, "stock_api\\filaments_dict.json")
    prev_json_file_path = os.path.join(sibling_path, "stock_api\\prev_filaments_dict.json")
    
    compareData(prev_json_file_path, json_file_path, filaments)
    
    return ""


def compareData(prev_json, new_json, filaments_dict):
    new_data = []
    
    #This will write to the new json file, if there are new items, and the previous json file will become the old "new" json file.
    with open(prev_json, "w") as file:
        
        
        if True:
            json.dump(new_json, file, indent=4)
        
            with open(new_json, "w") as file:
                json.dump(filaments_dict, file, indent=4)
    
    return new_data
    

#Run bot to search through website
runBot()

time.sleep(10)
driver.quit()