import re
import nltk 
from bs4 import BeautifulSoup
import requests
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

class Web:
    def __init__(self):
        nltk.download('punkt')
        nltk.download('stopwords')
        nltk.download('wordnet')
        nltk.download('punkt_tab')
    def getContent(self , url ):
        headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
        }      
        response = requests.get(url , headers=headers) 
        if(response.status_code == 200):
            html = response.text
            soup = BeautifulSoup(html, 'html.parser')
            for script in soup(["script", "style"]):
                script.decompose()  
            text = soup.get_text()
            text = self.preprocessText(text)
            updated_text = " ".join(text)
            print(updated_text)
            return updated_text
        return "Error"

    def preprocessText(self , text):
        words = word_tokenize(text)
        stop_words = set(stopwords.words('english'))
        filtered_words = [word for word in words if word.lower() not in stop_words and word.isalpha()]
        lemmatizer = WordNetLemmatizer()
        lemmatized_words = [lemmatizer.lemmatize(word) for word in filtered_words]
        return lemmatized_words
    def is_valid_url(self , url ) :
        pattern = r'^(https?://)(www\.)?[\w\-]+(\.[a-z]{2,6})+(/[^\s]*)?$'
        if re.match(pattern, url):
            return True
        return False


if __name__ == "__main__":
    mod = Web("https://pypi.org/project/beautifulsoup4/")
    mod.getContent()

        
