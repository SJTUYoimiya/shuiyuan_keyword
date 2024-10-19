import requests
from concurrent.futures import ThreadPoolExecutor
import itertools
import numpy as np
import os


class Shuiyuan:
    url: str
    cookies: str
    headers: dict

    def __init__(self, url: str) -> None:
        with open('cookies.txt', 'r', encoding='UTF-8') as f:
            cookies = f.read().strip()
        self.url = url
        self.headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh-Hans;q=0.9',
            'Connection': 'keep-alive',
            'Cookie': cookies,
            'Priority': 'u=0, i',
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            'USER-AGENT': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.1 Safari/605.1.15',
        }

    def requ(self):
        try:
            response = requests.get(self.url, headers=self.headers)
            response.raise_for_status()
        except requests.exceptions.RequestException as err:
            print(f'Failed to fetch the page: {self.url}, \nerror:', err)
            raise SystemExit(err)
        else:
            print('Successfully fetched the page:', self.url)
            return response.json()


def requ_id(username, offset):
    url = f'https://shuiyuan.sjtu.edu.cn/user_actions.json?offset={offset}&username={username}&filter=4,5'
    requ = Shuiyuan(url)
    res = requ.requ()

    # extract the topic & post id
    id_list = []
    for action in res['user_actions']:
        id_list.append([action['topic_id'], action['post_number']])

    return id_list

def requ_id_list(username, deleted_posts=100):
    # check the number of posts
    url0 = f'https://shuiyuan.sjtu.edu.cn/u/{username}/summary.json'
    requ0 = Shuiyuan(url0)
    res0 = requ0.requ()
    max_posts = res0['user_summary']['post_count']
    max_posts += deleted_posts  # add the number of deleted posts

    offsets = np.arange(0, max_posts, 30)
    id_list = []

    with ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
        futures = [executor.submit(requ_id, username, offset) for offset in offsets]
        for future in futures:
            id_list.append(future.result())
    
    id_list = list(itertools.chain(*id_list))
    return id_list


def requ_post(topic_id, post_id):
    url = f'https://shuiyuan.sjtu.edu.cn/t/topic/{topic_id}/{post_id}.json'
    requ = Shuiyuan(url)
    res = requ.requ()

    if res is None: # if the topic is deleted
        pass
    else:
        posts = res['post_stream']['posts']
        for post in posts:
            content = None  # clean the content

            if post['post_number'] == post_id:
                content = post['cooked']
                break
            else:
                continue

        return content
 

if __name__ == '__main__':
    username = 'yoimiya'
    post_id_list = requ_id_list(username)
    print('Successfully fetched the post ids, you have', len(post_id_list), 'posts.')

    with open('./tmp/post_id.txt', 'w', encoding='UTF-8') as f:
        for post_id in post_id_list:
            f.write(f'{post_id[0]},{post_id[1]}\n')
    