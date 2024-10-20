import pandas as pd
import itertools
from collections import Counter
import numpy as np
from bs4 import BeautifulSoup
import jieba
from sklearn.feature_extraction.text import TfidfVectorizer
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import os

############################################
# Remove unnecessary items from the context
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

############################################
# Load stopwords
with open('baidu_stopwords.txt', 'r', encoding='UTF-8') as f:
    stopwords = f.read().splitlines()

# add stopwords
stopwords_extra = [' ', '', ',', '，', '。', '.', ':', ':', '：', '“', '”', '、', '；', '(', ')', '（', '）', '《', '》', '？', '！', '!', ' ', '　', '\t', '\n', '一个', '两个', '三个', '几个', '好像']
stopwords.extend(stopwords_extra)

# tokenize
def cut_words(text):
    return [word for word in jieba.cut(text) if word not in stopwords]

def tokenization(texts):
    tokens = [cut_words(text) for text in texts]
    return tokens

# TF-IDF statistics
def tfidf(tokens):
    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform([' '.join(words) for words in tokens])
    feature_names = vectorizer.get_feature_names_out()
    frequencies = np.sum(X.toarray(), axis=0)

    # create DataFrame for better visualization
    df = pd.DataFrame({'Keyword': feature_names, 'Frequency': frequencies})
    df = df.sort_values(by='Frequency', ascending=False)
    return df


def draw_wordcloud(df):
    data_dict = df.set_index('Keyword')['Frequency'].to_dict()
    font_path = 'PingFangSC-Regular.ttf'
    wordcloud = WordCloud(width=1600, height=800, background_color='white', font_path=font_path, min_font_size=8).generate_from_frequencies(data_dict)
    
    fig, ax = plt.subplots(figsize=(20, 12))
    ax.imshow(wordcloud, interpolation='bilinear')
    ax.axis('off')
    return fig

############################################
def main(username):
    user_archive = pd.read_csv('user_archive.csv')
    user_archive.dropna(axis=0, how='any', inplace=True)
    all_posts_cooked = user_archive['post_cooked'].to_list()

    contexts = []
    emojis = []

    for post in all_posts_cooked:
        post, emoji = get_context(post)
        
        if len(post) > 0 and '（帖子已被作者删除）' not in post:
            contexts.append(post)
            
        emojis.append(emoji)

    # keyword statistics
    tokens = tokenization(contexts)
    df_tfidf = tfidf(tokens)
    df_tfidf.to_csv(f'{username}/keywords.csv', index=False, encoding='UTF-8')
    fig = draw_wordcloud(df_tfidf)
    fig.savefig(f'{username}/{username}.png')
    print(f'你的水源关键词与词云已保存到 {username} 文件夹下.')

    # emoji statistics
    emojis = list(itertools.chain(*emojis))
    counter = Counter(emojis)
    print('你的表情统计如下，请复制到水源中查看：\n', counter)

if __name__ == '__main__':
    username = input('Enter ur Shuiyuan username: ')
    if not os.path.exists(username):
        os.makedirs(username)
    main(username)