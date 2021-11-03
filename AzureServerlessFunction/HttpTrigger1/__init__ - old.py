from io import BytesIO
import logging

import azure.functions as func
import json
import os
import pandas as pd
import math
import numpy as np

from azureml.core.authentication import ServicePrincipalAuthentication
from azureml.core import Workspace
from azureml.core.dataset import Dataset


def authentication():
    svc_pr_password = os.environ['BOOKSHELF_SPA_PASSWORD']
    #svc_pr_password = "DB17Q~ZTNxlinTG6zrz82q.H3HNiG2UfVtYqL"
    tenant_id = '894ad120-c276-4dfa-b218-d82b3fece6a7'
    application_id = '52dfe3c3-0fcc-47d0-bc76-0429bf40abc7'
    svc_pr = ServicePrincipalAuthentication(tenant_id=tenant_id, service_principal_id=application_id, service_principal_password=svc_pr_password)
    subscription_id = os.environ['AZURE_SUBSCRIPTION_ID']
    #subscription_id = "dc0050bb-8e50-4b60-8aac-034371ba1a2a"
    resource_group = 'p9bookshelffunctionapp'
    workspace_name = 'WS-IA-P9'
    ws = Workspace(subscription_id=subscription_id, resource_group=resource_group, workspace_name=workspace_name, auth=svc_pr)
    return ws


def get_data(ws):
    dataset_name = 'data_bookshelf'
    dataset_registered = Dataset.get_by_name(ws, dataset_name)
    df_data = dataset_registered.to_pandas_dataframe()
    return df_data


def get_data_train(df_data):
    df_data = df_data.sort_values(by="click_timestamp").reset_index(drop=True)
    TRAIN_TEST_SPLIT_RATIO = 0.5
    len_train = math.ceil(len(df_data) * TRAIN_TEST_SPLIT_RATIO)
    df_data_train = df_data.iloc[:len_train,:].reset_index(drop=True)
    return df_data_train


def get_articles_already_read_for_user(user_id, df_data_train):
    articles_already_read = df_data_train[df_data_train['user_id']==user_id]['article_id'].unique().tolist()
    return articles_already_read
    
    
def get_last_article_read(user_id, df_data_train):
    last_article_id = int(df_data_train[df_data_train['user_id']==user_id]['article_id'].iloc[-1])
    return last_article_id


def get_similar_articles(cos_sim_matrix, article_id, df_data):
    ids = []
    scores = []
    ids_article_read = df_data['article_id'].unique()
    article_index_id = ids_article_read.index(article_id)
    for i in range(len(cos_sim_matrix)):
        ids.append(ids_article_read[i])
        scores.append(cos_sim_matrix[i][article_index_id])
    df_ids_scores = pd.DataFrame(list(zip(ids, scores)), columns=['id', 'score'])    
    df_ids_scores_sorted = df_ids_scores.sort_values(by=['score'], axis=0, ascending=False)
    similar_articles = df_ids_scores_sorted['id'].to_list()
    return similar_articles


def get_recommendations_articles_similarities(user_id, top_n, matrix_cos_sim, df_data_train, df_data):
    if user_id in df_data_train['user_id'].values:
        last_article_id = get_last_article_read(user_id, df_data_train)
        similar_articles = get_similar_articles(matrix_cos_sim, last_article_id, df_data)
        articles_already_read_for_user = get_articles_already_read_for_user(user_id, df_data_train)
        similar_articles_not_already_read = [i for i in similar_articles if i not in set(articles_already_read_for_user)]
        top_n_similar_articles_not_already_read = similar_articles_not_already_read[:top_n]
        return top_n_similar_articles_not_already_read
    else:
        print("Error : User does not exist or user with not enough historic")


def main(req: func.HttpRequest, data: func.InputStream) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')
    
    df_data = pd.read_csv(BytesIO(data.read()))
    #matrix_cos_sim = pd.read_csv(BytesIO(cossimmat.read()))
    
    req_body = req.get_json()
    user_id = req_body.get('userId')

 
    #ws = authentication()
    
    #df_data = get_data(ws)
    
    df_data_train = get_data_train(df_data)

    #recommandations = get_recommendations_articles_similarities(user_id, 5, matrix_cos_sim, df_data_train, df_data)

    #response = {"user_id" : ws.name}
    
    recommandations = [1,2,3,4,5]

    #response = {"data" : recommandations}
    response = recommandations
    
    return func.HttpResponse(json.dumps(response), mimetype="application/json")

    """
    name = req.params.get('name')
    if not name:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            name = req_body.get('name')

    if name:
        return func.HttpResponse(f"Hello, {name}. This HTTP triggered function executed successfully.")
    else:
        return func.HttpResponse(
             "This HTTP triggered function executed successfully. Pass a name in the query string or in the request body for a personalized response.",
             status_code=200
        )
    """