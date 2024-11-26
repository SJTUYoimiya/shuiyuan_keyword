"""
This module processes and analyzes text data from Shuiyuan posts,
extractingkeywords and generating word clouds.

Variables:
    stopwords:
        List of stopwords loaded from 'baidu_stopwords.txt' 
        and additional custom stopwords.
"""
import os
import itertools
from collections import Counter
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import jieba
from bs4 import BeautifulSoup
from sklearn.feature_extraction.text import TfidfVectorizer
from wordcloud import WordCloud

with open("baidu_stopwords.txt", 'r', encoding='UTF-8') as f:
    STOPWORDS = f.read().splitlines()

# add extra stopwords
EXTRA_STOPWORDS = [' ', '', ',', '，', '。', '.', ':', ':', '：', '“',
                   '”', '、', '；', '(', ')', '（', '）', '《', '》',
                   '？', '！', '!', ' ', '　', '\t', '\n', '一个', '两个',
                   '三个', '几个', '好像']
STOPWORDS.extend(EXTRA_STOPWORDS)
FONT_FAMILY = 'PingFangSC-Regular.ttf'


class ContentExtractor:
    """Extract text and emojis from Shuiyuan posts.

    Attributes:
        posts (list): The text content of the posts.
        emojis (list): The titles of the emojis used in the posts.
    """

    def __init__(self) -> None:
        self.posts = []
        self.emojis = []

    def extract_content(self, content: str) -> tuple[str, list[str]]:
        """Get text content and emojis from a Shuiyuan post.

        Parameters:
            content (str): The content of a Shuiyuan post.

        Returns:
            text (str): The text content of the post.
            emoji_title (list): The titles of the emojis used in the post.
        """
        def get_items_to_remove(soup):
            """The items to remove from the content.

            Parameters:
                soup (BeautifulSoup): The parsed content of a Shuiyuan post.

            Returns:
                items_to_remove (list): A list of items to remove from the
                                        content.
            """
            items_to_remove = []
            # 水源签名档
            items_to_remove.append(
                soup.find_all('div', attrs={'data-signature': True}))
            # 图片
            image_class = ['lightbox-wrappeyr', 'video-container']
            items_to_remove.append(soup.find_all('div', class_=image_class))
            # 嵌入视频/链接
            items_to_remove.append(
                soup.find_all('aside', class_='onebox allowlistedgeneric'))
            # 数学公式
            items_to_remove.append(soup.find_all(class_='math'))
            # 投票数据
            items_to_remove.append(soup.find_all('div', class_='poll-info'))
            # 时间
            items_to_remove.append(
                soup.find_all('span', class_='discourse-local-date'))
            # 代码块
            items_to_remove.append(soup.find_all('code'))
            # 水源引用
            quotes = soup.find_all(
                'aside', 
                class_=['quote', 'quote quote-modified', 'quote no-group']
            )
            items_to_remove.append(quotes)
            # 提及(@)/超链接/附件
            items_to_remove.append(soup.find_all('a'))
            return items_to_remove

        soup = BeautifulSoup(content, 'lxml')
        # remove unwanted items
        items_to_remove = get_items_to_remove(soup)
        for item in itertools.chain(*items_to_remove):
            item.decompose()

        text = soup.get_text(separator=',', strip=True)     # get text content
        emoji = soup.find_all('img', class_='emoji')        # get emojis
        emoji_title = [emoji['title'] for emoji in emoji]
        return text, emoji_title

    def get_content(self, posts_cooked: list[str]):
        """Extract text and emojis from a list of Shuiyuan posts.

        Parameters:
            posts_cooked (list): A list of Shuiyuan posts.

        Returns:
            posts (list): The text content of the posts.
            emojis (list): The titles of the emojis used in the posts.
        """
        for post in posts_cooked:
            text, emoji_title = self.extract_content(post)

            if text and '（帖子已被作者删除）' not in post:
                self.posts.append(text)

            self.emojis.append(emoji_title)
        return self.posts, self.emojis


class KeywordAnalyzer:
    """Extract keywords from Shuiyuan posts.

    Attributes:
        stopwords (list): A list of stopwords.
        contexts (list): The text content of the posts.
        tokens (list): The tokenized text content of the posts.
        kwd_freq (DataFrame): A DataFrame containing the keywords and
                              their frequencies.
    """
    def __init__(self, posts: list[str]) -> None:
        self.stopwords = STOPWORDS
        self.contexts = posts
        self.tokens = self._tokenization()
        self.kwd_freq = self.tfidf()

    def _tokenization(self) -> list[list[str]]:
        """
        Tokenize a list of texts and remove stopwords.

        Returns:
            list: A list of tokens.
        """
        def _cut_words(text: str) -> list[str]:
            """
            Tokenize the text and remove stopwords.

            Parameters:
                text (str): The text to tokenize.

            Returns:
                list: A list of tokens.
            """
            return [word
                    for word in jieba.cut(text)
                    if word not in self.stopwords]
        return [_cut_words(text) for text in self.contexts]

    def tfidf(self) -> pd.DataFrame:
        """
        Calculate the TF-IDF statistics of the tokens.

        Returns:
            kwd_freq (DataFrame): A DataFrame containing the keywords and
                                  their frequencies.
        """
        vectorizer = TfidfVectorizer()
        vec = vectorizer.fit_transform([' '.join(words) for words in
                                        self.tokens])
        feat_names = vectorizer.get_feature_names_out()
        freqs = np.sum(vec.toarray(), axis=0)

        # create DataFrame for better visualization
        self.kwd_freq = pd.DataFrame({'Keyword': feat_names,
                                 'Frequency':  freqs})
        self.kwd_freq = self.kwd_freq.sort_values(by='Frequency',
                                                  ascending=False)
        return self.kwd_freq

    def draw_wordcloud(self, font: str = FONT_FAMILY) -> plt.Figure:
        """
        Generate a word cloud based on the keyword frequency data.

        Returns:
            fig (Figure): The generated word cloud.
        """
        data_dict = self.kwd_freq.set_index('Keyword')['Frequency'].to_dict()
        wordcloud = WordCloud(
            width=1600,
            height=800,
            background_color='white',
            font_path=font,
            min_font_size=8
        ).generate_from_frequencies(data_dict)

        fig, ax = plt.subplots(figsize=(20, 12))
        ax.imshow(wordcloud, interpolation='bilinear')
        ax.axis('off')
        return fig

def main():
    """
    Main function to process and analyze Shuiyuan posts.
    """
    user_archive = pd.read_csv('user_archive.csv')
    user_archive.dropna(axis=0, how='any', inplace=True)
    all_posts_cooked = user_archive['post_cooked'].to_list()

    # extract text content and emojis
    extractor = ContentExtractor()
    posts, emojis = extractor.get_content(all_posts_cooked)

    # keyword statistics
    analyzer = KeywordAnalyzer(posts)
    fig = analyzer.draw_wordcloud()

    # save word cloud
    username = input('Enter ur Shuiyuan username: ')

    if not os.path.exists(username):
        os.makedirs(username)

    fig.savefig(f'{username}/{username}.png')
    print(f'你的水源关键词与词云已保存到 {username} 文件夹下.')

    # emoji statistics
    emojis = list(itertools.chain(*emojis))
    counter = Counter(emojis)
    print('你的表情统计如下，请复制到水源中查看：\n', counter)

if __name__ == '__main__':
    main()
