from io import BytesIO
import logging

import azure.functions as func
import tempfile
import json
import os
import implicit
import pandas as pd
import numpy as np
import pickle
from scipy.sparse import csr_matrix

from azureml.core.authentication import ServicePrincipalAuthentication
from azureml.core import Workspace
from azureml.core.dataset import Dataset


def get_recommendations_als_model(user_num, top_n, df_data_train_implicit, als_model):
    articles_users_sparse = csr_matrix((df_data_train_implicit['nb_interactions'].astype(float), (df_data_train_implicit['article_num'], df_data_train_implicit['user_num'])))
    users_articles_sparse = articles_users_sparse.T.tocsr()
    if user_num in range(users_articles_sparse.shape[0]):
        recommendations = als_model.recommend(user_num, users_articles_sparse, N=top_n, filter_already_liked_items=True)
        
        articles_recommended = []
        for item in recommendations:
            idx, _ = item
            articles_recommended.append(df_data_train_implicit['article_id'].loc[df_data_train_implicit['article_num'] == idx].iloc[0])
        
        return articles_recommended
    else:
        print("Error : User num does not exist")

def main(req: func.HttpRequest, data: func.InputStream, model: bytes) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    req_body = req.get_json()
    user_id = req_body.get('userId')

    logging.info(f"user_id {user_id}")

    df_data = pd.read_csv(BytesIO(data.read()))

    """
    tempFilePath = tempfile.gettempdir()
    fp = tempfile.NamedTemporaryFile(delete=False)
    #fp.name="bookshelf_best_model_saved.pickle"
    fp.write(model.read())
    fp.close
    files = os.listdir(tempFilePath)
    logging.info(f"temp file {files}")

    data = open(fp.name).read()
    model_pickle = pickle.load(data)
    """
    """
    with open(fp.name, 'rb') as pickle_in:
        model_pickle = pickle.load(pickle_in)
    """

    """
    with open("./bookshelf_best_model_saved.pickle", "wb") as outfile:
        outfile.write(model.read())
    
    with open("bookshelf_best_model.pickle", 'rb') as pickle_in:
        model_pickle = pickle.load(pickle_in)
    """

    #model_bytes = model.read()
    #model_to_read = BytesIO(model_bytes)

    """
    with model as pickle_in:
        model_pickle = pickle.load(pickle_in)
    """
    model_pickle = pickle.load(model)

    #model_pickle = pickle.load(model.read())
    
    #model_pickle = pickle.loads(model.read())    

    #model = pd.read_csv(BytesIO(model.read()))
    
    top_n = 5
    user_num = df_data['user_num'].loc[df_data['user_id'] == 1].iloc[0]

    #recommandations = get_recommendations_als_model(user_num, top_n, df_data, model_pickle)

    #response = {"user_id" : ws.name}
    
    recommandations = [1,2,3,4,5]

    #response = {"data" : recommandations}

    return func.HttpResponse(json.dumps(recommandations), mimetype="application/json")
