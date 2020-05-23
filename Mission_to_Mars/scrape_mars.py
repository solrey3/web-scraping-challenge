from splinter import Browser
from bs4 import BeautifulSoup
import requests
import pymongo
import pandas as pd
import time


def init_browser():
    # @NOTE: Replace the path with your actual path to the chromedriver
    executable_path = {"executable_path": "/usr/local/bin/chromedriver"}
    return Browser("chrome", **executable_path, headless=False)

def scrape_info():
    browser = init_browser()
    mars_data = {}

    # Retrieve headline and description
    url = "https://mars.nasa.gov/news/?page=0&per_page=40&order=publish_date+desc%2Ccreated_at+desc&search=&category=19%2C165%2C184%2C204&blank_scope=Latest"
    browser.visit(url)
    time.sleep(3)
    html = browser.html
    soup = BeautifulSoup(html, 'html.parser')
    title_results = soup.find('ul', class_="item_list") 
    news_title = title_results.find_all('h3')[0].text
    p_title = title_results.find_all('div', class_="rollover_description_inner")[0].text
    mars_data["news_title"] = news_title
    mars_data["p_title"] = p_title

    # Retireve featured image
    url = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
    browser.visit(url)
    html = browser.html
    soup = BeautifulSoup(html, 'html.parser')
    relative_featured_image_url = soup.find('a', class_='button fancybox')['data-link']
    base_url = "https://www.jpl.nasa.gov"
    image_url_page = base_url + relative_featured_image_url
    browser.visit(image_url_page)
    html = browser.html
    soup = BeautifulSoup(html, 'html.parser')
    relative_full_div = soup.find_all('div', class_='download_tiff')
    relative_full_url = relative_full_div[1].p.a['href']
    featured_image_url = "https:" + relative_full_url
    mars_data["featured_image_url"] = featured_image_url

    # Retrieve weather from Twitter
    url = 'https://twitter.com/marswxreport?lang=en'
    browser.visit(url)
    time.sleep(5)
    html = browser.html
    soup = BeautifulSoup(html, 'html.parser')
    twitter_results = soup.find('div', class_="css-901oao r-jwli3a r-1qd0xha r-a023e6 r-16dba41 r-ad9z0x r-bcqeeo r-bnwqim r-qvutc0")
    mars_weather = twitter_results.span.text
    mars_data["mars_weather"] = mars_weather

    # Retrieve Mars Facts table
    url = "https://space-facts.com/mars/"
    tables = pd.read_html(url)
    mars_info_df = tables[0]
    mars_info_df.columns = ['Metric','Value']
    mars_html = mars_info_df.to_html(header=True,index=False)
    mars_data["mars_facts"] = mars_html

    # Retrieve hemisphere pics
    url = "https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars"
    browser.visit(url)
    html = browser.html
    soup = BeautifulSoup(html, 'html.parser')
    hemi_results = soup.find_all('div', class_="item")
    titles = []
    img_urls = []
    base_url = "https://astrogeology.usgs.gov"
    for result in hemi_results:
        titles.append(result.h3.text)
        image_link = result.a['href']
        image_page = base_url + image_link
        browser.visit(image_page)
        image_html = browser.html
        soup = BeautifulSoup(image_html, 'html.parser')
        link_results = soup.find_all('a', text="Sample")
        img_urls.append(link_results[0]['href'])
    hemisphere_image_urls_df = pd.DataFrame({'title': titles, 'img_url':img_urls})
    hemisphere_image_urls = hemisphere_image_urls_df.to_dict('records')   
    mars_data["hemisphere_image_urls"] = hemisphere_image_urls

    # Close the browser after scraping
    browser.quit()

    # Return results
    return mars_data

