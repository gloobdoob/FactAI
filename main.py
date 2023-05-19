import os
from image_reader import ImageReader
from text_corrector import TextCorrector
from similarity_checker import SimilarityChecker
from google_scraper import GoogleScraper
from knapsack_checker import KnapsackChecker
import warnings
import logging
os.environ['TOKENIZERS_PARALLELISM'] = 'true'  # or 'false'

class SearchResultException(Exception):
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)

def check(text, c, gs, sc):
    query = None
    # if the text is not that long, it will not summarize
    if len(text) > 48:
        print('summarizing text')
        query = c.summarize(text)

    else:
        query = text

    print('To search:', query)

    s_result = gs.get_results(query)
    if s_result:
        search_title = [title[0] for title in s_result]
        search_body = [title[1] for title in s_result]
        search_links = [title[2] for title in s_result]
        print("checking similarities")
        sim_rating_title = sc.check_similarity(query, search_title)
        sim_rating_body = sc.check_similarity(query, search_body)
        # print(len(s_result))
        return sim_rating_title, sim_rating_body, search_links

    else:
        raise Exception('Image did not yield any results on google, try a picture with better quality and clearer text')
    

def text_extractor(img):
    

    ocr = ImageReader()
    print('extracting text from image')
    text = ocr.read_img(img)
    print("extracted:", text)
    print('correcting text')

    return text




def predict_headline(text):
    logger = logging.getLogger()
    logging.disable(logging.CRITICAL)
    
    c = TextCorrector()

    logger.disabled = True
    corrected = c.correct(text)
    article = c.decide_text(text, corrected)

    gs = GoogleScraper()
    sc = SimilarityChecker()
    print('scraper initialized')
    print('rating')
    t_sim_rating, b_sim_rating, urls = check(article, c, gs, sc)
    logger.disabled = False
    kc = KnapsackChecker(t_sim_rating, urls)
    res_url_wts, res_sim, sites = kc.checker()
    print(res_sim)
    prediction = kc.truth_checker_k(res_sim, len(res_url_wts))

    logger = logging.getLogger()
    logging.disable(logging.CRITICAL)
    try:

        if prediction == 'Real':
            return f'''We predict that this is a, '{prediction}' article.
                      These are the articles from credible sites that we ran across when searching for this image: 
                     {sites}'''


        elif prediction == 'Risky' and sites:
            return f'''We predict that this is a, '{prediction}' article. Please do more research regarding this topic
                       These are the articles from credible sites that we ran across when searching for this image
                       {sites}'''

        elif prediction == 'Risky' and not sites:
            return f'''We predict that this is a ,'{prediction}' article. Please do more research regarding this topic
                       There were no credible websites that appeared while searching for this image
                       These are the risky websites that came up when searching: 
                       {urls}'''

    except Exception as e:
        print(e)







def main(img):
    logger = logging.getLogger()
    logging.disable(logging.CRITICAL)

    ocr = ImageReader()
    print('extracting text from image')
    text = ocr.read_img(img)
    print("extracted:", text)
    print('correcting text')

    c = TextCorrector()

    logger.disabled = True
    corrected = c.correct(text)
    article = c.decide_text(text, corrected)

    gs = GoogleScraper()
    sc = SimilarityChecker()

    t_sim_rating, b_sim_rating, urls = check(article, c, gs, sc)
    logger.disabled = False
    kc = KnapsackChecker(t_sim_rating, urls)
    res_url_wts, res_sim, sites = kc.checker()
    print(res_sim)
    prediction = kc.truth_checker_k(res_sim, len(res_url_wts))

    logger = logging.getLogger()
    logging.disable(logging.CRITICAL)
    try:

        if prediction == 'Real':
            return f'''We predict that this is', {prediction}.
                      These are the articles from credible sites that we ran across when searching for this image: 
                     {sites}'''


        elif prediction == 'Risky' and sites:
            return f'''We predict that this is', {prediction}. Please do more research regarding this topic
                       These are the articles from credible sites that we ran across when searching for this image
                       {sites}'''

        elif prediction == 'Risky' and not sites:
            return f'''We predict that this is a {prediction} article. Please do more research regarding this topic
                       There were no credible websites that appeared while searching for this image
                       These are the risky websites that came up when searching: 
                       {urls}'''

    except Exception as e:
        print(e)

def main2(input_text):
    logger = logging.getLogger()
    logging.disable(logging.CRITICAL)

    # Extract text from headline input
    text = input_text

    c = TextCorrector()
    corrected = c.correct(text)
    article = c.decide_text(text, corrected)

    gs = GoogleScraper()
    sc = SimilarityChecker()

    t_sim_rating, b_sim_rating, urls = check(article, c, gs, sc)
    kc = KnapsackChecker(t_sim_rating, urls)
    res_url_wts, res_sim, sites = kc.checker()

    prediction = kc.truth_checker_k(res_sim, len(res_url_wts))

    logger = logging.getLogger()
    logging.disable(logging.CRITICAL)

    try:

        if prediction == 'Real':
            return f'''We predict that this is', {prediction}.
                      These are the articles from credible sites that we ran across when searching for this image: 
                     {sites}'''


        elif prediction == 'Risky' and sites:
            return f'''We predict that this is', {prediction}. Please do more research regarding this topic
                       These are the articles from credible sites that we ran across when searching for this image
                       {sites}'''

        elif prediction == 'Risky' and not sites:
            return f'''We predict that this is a {prediction} article. Please do more research regarding this topic
                       There were no credible websites that appeared while searching for this image
                       These are the risky websites that came up when searching: 
                       {urls}'''

    except Exception as e:
        print(e)
