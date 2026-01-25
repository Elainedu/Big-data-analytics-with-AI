import pandas as pd

def save_comment(comment, item_id):
    # 读取CSV文件
    df = pd.read_csv('cna_news_200_preprocessed.csv', sep='|')
    
    # 检查是否有comment列，如果没有则添加
    if 'comment' not in df.columns:
        df['comment'] = ""
    
    # 找到指定的item_id所在的行并写入comment
    df.loc[df['item_id'] == item_id, 'comment'] = comment
    
    # 保存回CSV文件
    df.to_csv('cna_news_200_preprocessed.csv', sep='|',index=None)

# 使用示例
save_comment('這是一條評論', "電影情報_2024-04-14_2")  # 替換成實際的comment和item_id
