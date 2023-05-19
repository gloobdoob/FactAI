from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd

pd.set_option('display.max_colwidth', None)
pd.set_option("display.max_columns", 10)

#checks the similarity between text and returns a rating from 0.0 to 1.0 depending on how similar they are
# uses cosine similarity
class SimilarityChecker:
    def __init__(self):
        self.comp_model = SentenceTransformer('bert-base-nli-mean-tokens')#this is outdated, change this when recreating (the bert-base thing i mean)

    def check_similarity(self, orig_text, comp_text):

        orig_text_embeddings = self.comp_model.encode(orig_text, show_progress_bar = False)
        comp_text_embeddings = self.comp_model.encode(comp_text, show_progress_bar = False)

        if isinstance(orig_text, str) and isinstance(comp_text, list):
            sim_rating = cosine_similarity(
                [orig_text_embeddings],
                comp_text_embeddings
            )

        elif isinstance(orig_text, list) and isinstance(comp_text, list):
            sim_rating = cosine_similarity(
                orig_text_embeddings,
                comp_text_embeddings
            )
        else:
            sim_rating = cosine_similarity(
                [orig_text_embeddings],
                [comp_text_embeddings]
            )
        #print(sim_rating[0])
        return sim_rating[0]
