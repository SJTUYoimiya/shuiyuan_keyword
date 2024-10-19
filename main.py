from crawl import requ_id_list
from data_cleaning import read_all_contexts

username = input('Enter ur Shuiyuan username: ')

post_id_list = requ_id_list(username)
print('Successfully fetched the post ids, you have', len(post_id_list), 'posts.')

df_text, df_emoji = read_all_contexts(post_id_list)

# save the data
df_text.to_csv('data/context.csv', index=False)
# df_emoji.to_csv('data/emoji.csv', index=False)

# run statistics
from data_stasitics import main
main(df_text)