from crawl import requ_id_list
from data_cleaning import read_all_contexts
from data_stasitics import main
import os

username = input('Enter ur Shuiyuan username: ')
# create a folder for the user

if not os.path.exists(username):
    os.makedirs(username)


post_id_list = requ_id_list(username)
print('Successfully fetched the post ids, you have', len(post_id_list), 'posts.')

df_text, df_emoji = read_all_contexts(post_id_list)

# save the data
df_text.to_csv(f'{username}/context.csv', index=False, encoding='UTF-8')
# df_emoji.to_csv('data/emoji.csv', index=False, encoding='UTF-8')

# run data statistics
main(df_text, username)
