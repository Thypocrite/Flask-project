# -*- coding: utf-8 -*-
"""
Created on Sun Oct  8 15:08:33 2023

@author: User
"""

import pandas as pd
import sqlite3
from surprise import Dataset, Reader, SVD
from surprise.model_selection import cross_validate


# 连接到SQLite数据库
conn = sqlite3.connect('merged.db')
members = pd.read_sql_query('SELECT * FROM lccnet', conn)
products = pd.read_sql_query('SELECT * FROM products', conn)
purchases = pd.read_sql_query('SELECT * FROM totall', conn)
conn.close()

# 计算年龄并进行分组
CURRENT_YEAR = 2023
members['age'] = CURRENT_YEAR - \
    pd.to_datetime(members['birthday'], format='%Y-%m-%d').dt.year
bins = [15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 100]
labels = ['15-19', '20-24', '25-29', '30-34', '35-39',
          '40-44', '45-49', '50-54', '55-59', '60+']
members['age_group'] = pd.cut(
    members['age'], bins=bins, labels=labels, right=False)

# 将购买历史和用户年龄组合在一起
purchases = purchases.merge(members[['user', 'age_group']], on='user')

# 模拟"评分"列，你可以根据需要替换这个逻辑
purchases['purchase_dummy'] = 1

# 使用协同过滤模型
reader = Reader(rating_scale=(0, 1))  # 我们的评分列是购买/未购买
data = Dataset.load_from_df(
    purchases[['user', 'salePageId', 'purchase_dummy']], reader)

# 使用SVD模型
model = SVD()
cross_validate(model, data, measures=['RMSE'], cv=5, verbose=True)

# 训练模型
trainset = data.build_full_trainset()
model.fit(trainset)

# 函数来获取推荐


def get_top_n_recommendations(user_id, n=4):
    # 获取用户还未购买过的商品
    all_products = products['salePageId'].unique()
    purchased_products = purchases[purchases['user']
                                   == user_id]['salePageId'].unique()
    not_purchased_products = set(all_products) - set(purchased_products)

    # 预测用户对未购买商品的评分
    predictions = []
    for product_id in not_purchased_products:
        predictions.append(
            (product_id, model.predict(user_id, product_id).est))

    # 获取评分最高的前n个商品
    top_n_product_ids = [x[0] for x in sorted(
        predictions, key=lambda x: x[1], reverse=True)[:n]]

    # 获取这些商品的详细信息
    top_n_products = products[products['salePageId'].isin(
        top_n_product_ids)][['salePageId', 'title', 'price', 'image_url']]

    return top_n_products


# 示例用户推荐
user_id_example = 'w@g'  # 使用实际用户电子邮件地址
top_recommendations = get_top_n_recommendations(user_id_example, n=4)

# 显示推荐的商品
print(top_recommendations)
