from io import BytesIO
import logging
import azure.functions as func
import json
import pandas as pd


def get_most_popular_category_for_user(user_id, df_data):
    most_popular_category_for_user = df_data[df_data['user_id']==user_id].groupby(['category_id']).size().sort_values(ascending=False).index[0]
    return most_popular_category_for_user

def get_most_popular_articles_for_category(category_id, df_data):
    most_popular_articles_for_category = df_data[df_data['category_id']==category_id].groupby(['article_id']).size().sort_values(ascending=False).index.to_list()
    return most_popular_articles_for_category

def get_articles_already_read_for_user(user_id, df_data):
    articles_already_read = df_data[df_data['user_id']==user_id]['article_id'].unique().tolist()
    return articles_already_read

def get_recommendations_articles_category(user_id, top_n, df_data):
    if user_id in df_data['user_id'].values:
        most_popular_category_for_user = get_most_popular_category_for_user(user_id, df_data)
        most_popular_articles_for_category = get_most_popular_articles_for_category(most_popular_category_for_user, df_data)
        articles_already_read_for_user = get_articles_already_read_for_user(user_id, df_data)    
        most_popular_articles_for_category_not_already_read = [i for i in most_popular_articles_for_category if i not in set(articles_already_read_for_user)]
        top_n_most_popular_articles_for_category_not_already_read = most_popular_articles_for_category_not_already_read[:top_n]
        return top_n_most_popular_articles_for_category_not_already_read
    else:
        logging.info(f"Error : User does not exist or user with not enough historic")        

def main(req: func.HttpRequest, data: func.InputStream) -> func.HttpResponse:

    req_body = req.get_json()
    id_bookshelf = req_body.get('userId')
    logging.info(f"id_bookshelf : {id_bookshelf}")

    df_data = pd.read_csv(BytesIO(data.read()))
    #As there are 10 000 users in the Bookshelf application, we keep the first 10 000 users in our dataset 
    user_id = sorted(df_data['user_id'].unique().tolist())[:10000][int(id_bookshelf)]
    #user_id = sorted(df_data['user_id'].unique().tolist())[int(id_bookshelf)]
    logging.info(f"user_id : {user_id}")
    
    nb_recommandations = 5
    recommandations = get_recommendations_articles_category(user_id, nb_recommandations, df_data)

    return func.HttpResponse(json.dumps(recommandations), mimetype="application/json")