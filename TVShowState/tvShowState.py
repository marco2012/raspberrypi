import requests
from bs4 import BeautifulSoup
import argparse  

# import telegram
# TOKEN = "794889497:AAGQ20Rorv-dQ-ECELP5z-KcNCsi3JMYOww"
# bot = telegram.Bot(token=TOKEN)

def search_show(query):
    try:
        response = requests.post(
            url="https://premieredate.news/index.php",
            params={
                "option": "com_ncatalogues",
                "controller": "ajaxscript",
                "task": "search_results",
            },
            headers={
                #"Cookie":"267576093de65e1e9c5bf420c1562857=lg0bn01e3tf1ppekpl6nd2h9e2",
                "Content-Type": "application/x-www-form-urlencoded; charset=utf-8"
            },
            data={
                "value": query.strip(),
                "option": "com_ncatalogues",
                "task": "search_results",
                "controller": "ajaxscript",
            },
        )
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            if soup.findAll('a'):
                link = "https://premieredate.news{}".format(soup.find('a').get('href'))
                return link
            else:
                return False

    except requests.exceptions.RequestException:
        print('HTTP Request failed')
        return False


def get_show(link):
    if link is not False:
        try:
            response = requests.get(url=link)
            html = response.content
            soup = BeautifulSoup(html, 'html.parser')
            return soup

        except requests.exceptions.RequestException:
            print('HTTP Request failed')
            return False
    else:
        print("Show not found")
        return False


def get_show_status(soup):
    if soup is not False:
        return soup.find("div", {"id": "status_date"}).text + '.'
    

def get_show_news(soup):
    if soup is not False and soup.select('div > p') and soup.select('div > p')[0].text == 'Latest news':
        return soup.select('div > p')[1].get_text(strip=True)
    else: return "Info not available."


def str_to_bool(value):
    if isinstance(value, bool):
        return value
    if value.lower() in {'false', 'f', '0', 'no', 'n'}:
        return False
    elif value.lower() in {'true', 't', '1', 'yes', 'y'}:
        return True
    raise argparse.ArgumentTypeError('Boolean value expected. [y/n]')


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('search', type=str, help='TV Show to search', nargs='+')
    parser.add_argument('--info', type=str_to_bool,
                        nargs='?', const=True, default=False)
    args = parser.parse_args()
    
    query  = ' '.join(args.search)
    link   = search_show(query)
    soup   = get_show(link)
    status = get_show_status(soup)
    print(status)
    if args.info:
        info = get_show_news(soup)
        print(info)
