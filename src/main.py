import requests
from bs4 import BeautifulSoup
import re
from config import  api_endpoint, api_key, api_version
from openai import AzureOpenAI
import cssutils

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup


class website_design:

    def __init__(self, url):
        self.url = url

    def fetch_css_with_selenium(self):
        """Fetch CSS content using Selenium to render the page including any dynamically loaded CSS."""
        # Setup Selenium WebDriver
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')

        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service,options=options)
        
        # Open the URL
        driver.get(url)

        # Get the rendered page source
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        # Extract CSS from both <link> and <style> tags
        # css_links = [link['href'] for link in soup.find_all('link', rel='stylesheet')]
        inline_styles = '\n'.join(style.text for style in soup.find_all('style'))

        driver.quit()  # Close the browser
        
        return inline_styles #inline_styles

    def parse_css(self,inline_css):
        pattern = r'([^{]*?)\s*\{\s*([^}]*?\bcolor\b\s*:\s*(#[0-9a-fA-F]{3,6}|rgba?\(\s*\d+\s*,\s*\d+\s*,\s*\d+\s*(?:,\s*[\d.]+\s*)?\)|\b[a-zA-Z]+\b)[^;}]*;)'
        # Find all matches
        css_match = re.findall(pattern, inline_css)
        return css_match

    def openai_completion(self,parsed_css_content, engine="gpt-35", temperature=0.1, max_tokens=1200):
        """
        General function to interact with OpenAI's completion endpoint.
        """
        client = AzureOpenAI(
        azure_endpoint = api_endpoint, 
        api_key=api_key,  
        api_version=api_version
        )
        prompt_text = [
            {"role": "system", "content": "You are equipped with the capability to analyze CSS."},
            {"role": "user", "content": (
                "As an expert CSS analyst, examine the following CSS content and identify the primary and secondary colors, "
                "as well as the primary fonts used. Provide your findings in a clear and structured format.\n\n"
                f"CSS Content:\n{parsed_css_content}\n\n"
                "I need to create a similar design so can you please list the primary color hex code and the secondary colors hex code used. Structure your response in the following format:\n\n"
                "Primary: #HexCode\n"
                "Secondary: #HexCodes"
            )}
        ]
        response = client.chat.completions.create(
            model=engine, # model = "deployment_name"
            messages =prompt_text,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=0.95,
            frequency_penalty=0,
            presence_penalty=0,
            stop=None
        )
        return response.choices[0].message.content

# Usage
url = 'https://tnthomeservicesco.com/'
css_analyzer = website_design(url)
css_content = css_analyzer.fetch_css_with_selenium()
parsed_css = css_analyzer.parse_css(css_content)
gpt_response = css_analyzer.openai_completion(parsed_css, engine='gpt-35-16k')
print(gpt_response)