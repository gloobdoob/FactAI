from image_reader import ImageReader
from google_scraper import GoogleScraper
from site_predictor import SitePredictor
from similarity_checker import SimilarityChecker
from image_predictor import ImagePredictor
from headline_predictor import HeadlinePredictor
import lingua
from transformers import pipeline
from textcorrector_v2 import TextCorrectorV2
import numpy as np
import logging
import os
import joblib

N_SEARCHES = 5

os.environ['TOKENIZERS_PARALLELISM'] = 'true'  # or 'false'
os.environ['KMP_DUPLICATE_LIB_OK']='True'



import re

def retry_results(text, tcV2):
    gs = GoogleScraper(n_searches=N_SEARCHES)
    #retries 4 times with differing methods of cleaning/summarizing the text to make google search recognize the query
    tries = 0
    s_results = None
    while not s_results and tries < 4:
        if tries == 0:
            s_results = gs.get_results(text)

        elif tries == 1:
            text = re.sub(r'[^\w\s]', '', text)
            s_results = gs.get_results(text)
        elif tries == 2:
            text = tcV2.summarize(text)
            text = re.sub(r'[^\w\s]', '', text)
            s_results = gs.get_results(text)
        elif tries == 3:
            text = tcV2.summarize(text, max_tokens=40)
            text = re.sub(r'[^\w\s]', '', text)
            s_results = gs.get_results(text)

        tries = tries + 1

    if tries == 4 and not s_results:
        return []
    else:
        return s_results, text


def cut_pad(arr, n):
    #cuts an array if it's too long and pads it if it's too short
    arr = np.array(arr, dtype='float32')
    arr = arr[:n] if arr.shape[0] > n else arr
    arr = np.pad(arr, (0, n - arr.shape[0]), mode='constant', constant_values=np.nan)
    return arr


def count_vals(x, nans, ones=True):
    #counts the number of real, fake, and empty predictions in the website pred array
    unique, counts = np.unique(x, return_counts=True)
    val_dict = {}
    for i, j in zip(unique, counts):
        if np.isnan(i):
            val_dict['nan'] = j
        else:
            val_dict[i] = j

    if ones == True and nans == False and 1.0 in val_dict.keys():
        return val_dict[1.0]
    elif ones == False and  nans == False and 0.0 in val_dict.keys():
        return val_dict[0.0]
    elif nans == True and ones == False and 'nan' in val_dict.keys():
        return val_dict['nan']

    else:
        return 0

def pred_overall(arr):
    # runs inference on all the data gathered
    print(arr)
    print(arr.shape)
    model = None
    if len(arr) == 7:
        print('using full model')
        model = joblib.load('classifiers/SVM-General-Classifier91ACC.joblib')
    elif len(arr) == 6:
        print('using headline only model')
        model = joblib.load('classifiers/XGB-Text-Only-Classifier97ACC.joblib')


    result_prob = model.predict_proba([arr])[0][1]
    result_round = round(result_prob)
    return result_prob, result_round

def text_extractor(img):
    ip = ImagePredictor()
    #reads and extracts text from image using EASYOCR
    ocr = ImageReader()
    text = ocr.read_img(img)
    image_pred = ip.predict_img(img)['real']
    return text, image_pred


def predict_headline(text, img_pred=None, image_url=None):

    sp = SitePredictor()
    hp = HeadlinePredictor()
    tcV2 = TextCorrectorV2()
    sc = SimilarityChecker()
    languages = [lingua.Language.ENGLISH, lingua.Language.TAGALOG]
    lang_detector = lingua.LanguageDetectorBuilder.from_languages(*languages).build()


    query = text


    # corrects text from the OCR using gpt3 AI
    corrected_query = None
    if img_pred is not None:
        # checks whether query is long enough as corrected text may sometimes be incorrect and output nothing at all
        tmp = tcV2.correct(query).replace("\n", "")
        corrected_query = query if len(tmp) < 20 else tmp
    else:
        corrected_query = query


    #predicts language so prediction models down the line may know what weights to use
    lang_pred = lang_detector.detect_language_of(corrected_query)
    lang = 'en' if str(lang_pred) == 'Language.ENGLISH' else 'tl' if str(lang_pred) == 'Language.TAGALOG' else None

    #if results come up empty, either due to unreadable text or a special character interfering with google's search algorithm
    full_res = retry_results(corrected_query, tcV2)
    if full_res:
        s_results, corrected_query = full_res
        search_title = [title[0] for title in s_results]
        search_links = [title[1] for title in s_results]
        #predicts the reliability of the websites that come up during the search
        site_preds = sp.predict(search_links)

        #if the predictions are not empty
        if site_preds:
            prediction_data = []
            #"""'sim mean', 'site pred mean', 'n real predicted', 'n fake predicted', 'n nan predicted', 'headline real pred', 'image real pred'"""
            #order of values
            sim_vals = None
            if lang == 'tl':
                search_title_trunc = [' '.join(headline.split(' ')[:256]) for headline in search_title]
                sim_vals = sc.check_similarity(corrected_query, search_title_trunc, lang)
            else:
                sim_vals = sc.check_similarity(corrected_query, search_title, lang)

            sim_vals = cut_pad(sim_vals, N_SEARCHES)
            site_preds = cut_pad(np.array(site_preds, dtype='float32'), N_SEARCHES)

            sim_mean = np.nanmean(sim_vals)
            site_pred_mean = np.nanmean(site_preds)

            n_real_predicted = count_vals(site_preds, nans=False)/N_SEARCHES
            n_fake_predicted = count_vals(site_preds, ones=False, nans=False)/N_SEARCHES
            n_nan_predicted  = count_vals(site_preds, ones=False, nans=True)/N_SEARCHES


            headline_pred = hp.predict_headlines(corrected_query, lang)['real']

            if img_pred:
                image_pred = img_pred

                prediction_data.extend([sim_mean,
                                        site_pred_mean,
                                        n_real_predicted,
                                        n_fake_predicted,
                                        n_nan_predicted,
                                        headline_pred,
                                        image_pred])
            else:
                prediction_data.extend([sim_mean,
                                        site_pred_mean,
                                        n_real_predicted,
                                        n_fake_predicted,
                                        n_nan_predicted,
                                        headline_pred])



            prediction_data = np.array(prediction_data, dtype='float32')

            result_proba, result_round = pred_overall(prediction_data)
            print(result_proba, result_round)
            prediction = 'RELIABLE' if result_round == 1 or result_round == 1.0 else 'UNRELIABLE'
            if prediction == 'RELIABLE':
                print(prediction)
                return int(result_round), f"We predict that this is a '{prediction}' article with {result_proba} confidence." , search_links
                
            elif prediction == 'UNRELIABLE':
                print(prediction)
                return int(result_round), f"We predict that this is an '{prediction}' article with {result_proba} confidence. Please do more research regarding this topic", search_links
    
        else:
            print('no results')
            return """No search results appeared for this input, this may be risky to trust or you may need to input a better quality image"""
    else:
        print('no results')
        return """No search results appeared for this input, this may be risky to trust or you may need to input a better quality image"""
    

    
    
