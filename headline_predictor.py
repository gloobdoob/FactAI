from transformers import pipeline
from lingua import Language, LanguageDetectorBuilder


class HeadlinePredictor:
    def __init__(self):
        self.en_model = pipeline(model="gloobdoob/english-headline-classifier-fake-news", top_k=None, use_auth_token=True)
        self.tl_model = pipeline(model="gloobdoob/tagalog-fake-news-headline-classifier-distilbert", top_k=None)
        self.languages = [Language.ENGLISH, Language.TAGALOG]
        self.detector = LanguageDetectorBuilder.from_languages(*self.languages).build()


    def get_preds(self, text, lang):
        preds = None
        if lang == 'en':
            print('using english model')
            preds = self.en_model([text])
            print(preds)
        if lang == 'tl':
            print('using tagalog model')
            preds = self.tl_model([text])
            print(preds)

        return preds

    def predict_headlines(self, text, lang):
        preds = self.get_preds(text, lang)
        pred_dic = {}
        for pred in preds[0]:
            if pred['label'] == 'LABEL_0':
                pred_dic['fake'] = pred['score']
            if pred['label'] == 'LABEL_1':
                pred_dic['real'] = pred['score']

        return pred_dic








