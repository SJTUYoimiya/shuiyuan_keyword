from crawl import requ_post
from bs4 import BeautifulSoup
import itertools
from concurrent.futures import ThreadPoolExecutor
import pandas as pd
import os
from tqdm import tqdm

def get_context(content):
    soup = BeautifulSoup(content, 'lxml')

    # delete the following items that are not related to the context
    items_to_remove = []

    items_to_remove.append(soup.find_all('div', attrs={'data-signature': True}))        # 水源签名档
    items_to_remove.append(soup.find_all('div', class_=['lightbox-wrapper', 'video-container']))                # 图片
    items_to_remove.append(soup.find_all('aside', class_='onebox allowlistedgeneric'))  # 嵌入视频/链接
    items_to_remove.append(soup.find_all(class_='math'))                                # 数学公式
    items_to_remove.append(soup.find_all('div', class_='poll-info'))                    # 投票数据
    items_to_remove.append(soup.find_all('span', class_='discourse-local-date'))        # 本地时间
    items_to_remove.append(soup.find_all('code'))                                       # 代码块
    items_to_remove.append(soup.find_all('aside', class_=['quote', 'quote quote-modified', 'quote no-group']))  # 水源引用
    items_to_remove.append(soup.find_all('a'))                                          # 提及(@)/超链接/附件

    for item in itertools.chain(*items_to_remove):
        item.decompose()
    
    text = soup.get_text(separator=',', strip=True)
    emoji = soup.find_all('img', class_='emoji')
    emoji_title = [emoji['title'] for emoji in emoji]
    return text, emoji_title


def read_context(topic_id, post_id):
    content = requ_post(topic_id, post_id)
    if content is None:
        pass
    else:
        text, emoji_title = get_context(content)
        return text, emoji_title, topic_id, post_id


def read_all_contexts(record):
    df_text = pd.DataFrame(columns=['topic', 'post', 'context'])
    df_emoji = pd.DataFrame(columns=['topic', 'post', 'emoji_list'])

    with ThreadPoolExecutor(max_workers=max(12, os.cpu_count())) as executor:
        futures = [executor.submit(read_context, topic_id, post_id) for topic_id, post_id in record]
        for future in tqdm(futures, total=len(futures), desc='Fetching post context', ncols=80, unit='post'):
            if future.result() is None:
                continue
            text, _, topic_id, post_id = future.result()

            if text != '':
                data = {'topic': topic_id, 'post': post_id, 'context':text}
                df_text = pd.concat([df_text, pd.DataFrame(data, index=[0])], ignore_index=True)

            # if emoji_list != [] and emoji_list != None:
            #     data = {'topic': topic_id, 'post': post_id, 'emoji_list': emoji_list}
            #     df_emoji = pd.concat([df_emoji, pd.DataFrame(data, index=[0])], ignore_index=True)
    return df_text, df_emoji

if __name__ == '__main__':
    with open('tmp/post_id.txt', 'r', encoding='UTF-8') as f:
        record = []
        for line in f:
            topic_id, post_id = line.strip().split(',')
            topic_id = int(topic_id)
            post_id = int(post_id)
            record.append([topic_id, post_id])

    contexts, emojis = read_all_contexts(record[:10])
    
    contexts.to_csv('./tmp/context.csv', index=False, encoding='UTF-8')
    # emojis.to_csv('./tmp/emoji.csv', index=False, encoding='UTF-8')
