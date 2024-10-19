import pandas as pd
import numpy as np
import jieba
from sklearn.feature_extraction.text import TfidfVectorizer
from wordcloud import WordCloud
import matplotlib.pyplot as plt

# load baidu stopwords
with open('baidu_stopwords.txt', 'r') as f:
    stopwords = f.read().splitlines()

# add stopwords
stopwords_extra = [' ', '', ',', '，', '。', '.', ':', ':', '：', '“', '”', '、', '；', '(', ')', '（', '）', '《', '》', '？', '！', '!', ' ', '　', '\t', '\n', '一个', '两个', '三个', '几个', '好像']
stopwords.extend(stopwords_extra)

# cut words
def cut_words(text):
    return [word for word in jieba.cut(text) if word not in stopwords]

def tokenization(texts):
    tokens = [cut_words(text) for text in texts]
    return tokens

# TF-IDF statistics
def tfidf(tokens):
    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform([' '.join(words) for words in tokens])
    # 获取关键词
    feature_names = vectorizer.get_feature_names_out()

    # 统计关键词的频率
    frequencies = np.sum(X.toarray(), axis=0)

    # 创建 DataFrame 以便更好地查看结果
    df = pd.DataFrame({'Keyword': feature_names, 'Frequency': frequencies})

    # 按频率排序
    df = df.sort_values(by='Frequency', ascending=False)
    return df


def draw_wordcloud(df, username):
    data_dict = df.set_index('Keyword')['Frequency'].to_dict()
    font_path = 'PingFangSC-Regular.ttf'
    wordcloud = WordCloud(width=1600, height=800, background_color='white', font_path=font_path, min_font_size=8).generate_from_frequencies(data_dict)
    
    plt.figure(figsize=(20, 12))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.savefig(f'data/{username}.png')

def main(df):
    texts = df['context'].tolist()

    tokens = tokenization(texts)
    df_tfidf = tfidf(tokens)

    df_tfidf.to_csv('data/keywords.csv', index=False)
    draw_wordcloud(df_tfidf, 'yoimiya')

if __name__ == '__main__':
    df = pd.read_csv('tmp/context.csv')
    main(df)