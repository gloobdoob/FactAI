from transformers import T5Tokenizer, T5ForConditionalGeneration
from happytransformer import HappyTextToText, TTSettings
from similarity_checker import SimilarityChecker

# text corrector class to correct and summarize a text since the OCR can glitch and produce incorrect text depending
# on the image quality
# uses pretrained transformer models from huggingface
class TextCorrector:
    def __init__(self):
        self.tokenizer = T5Tokenizer.from_pretrained('t5-small')
        self.model = T5ForConditionalGeneration.from_pretrained('t5-small')
        self.happy_tt = HappyTextToText("T5", "prithivida/grammar_error_correcter_v1")
        self.sim_checker = SimilarityChecker()

    def correct(self, text):
        # print("corrected")
        args = TTSettings(do_sample=True, top_k=20, temperature=0.7, min_length=1, max_length=110, early_stopping=True)
        sentence = self.happy_tt.generate_text(text, args=args).text

        return sentence

    def summarize(self, text):
        inputs = self.tokenizer.batch_encode_plus(["summarize: " + text], max_length=1024, return_tensors="pt",
                                                  padding='max_length', truncation=True)  # Batch size 1
        token_l = (inputs['attention_mask'][0] == 1.).sum(dim=0)
        outputs = self.model.generate(inputs['input_ids'], num_beams=4, max_length=int(0.8 * int(token_l)),
                                      early_stopping=True)

        return [self.tokenizer.decode(g, skip_special_tokens=True, clean_up_tokenization_spaces=False) for g in outputs][0]


    # decides whether the original text and correct text are similar in meaning, if they are similar
    # the corrected text is used
    # if they are not, the extracted text is used
    # this is because sometimes, the corrected text is wrong or can be very far from the original meaning of the
    # extracted text
    def decide_text(self, text, corrected):
        article = None
        sim_rating = self.sim_checker.check_similarity(text, corrected)[0]
        status = None
        if sim_rating > 0.92:
            status = 'Corrected'
            article = corrected
        else:
            status = 'Not corrected'
            article = text

        print(status, ':', article)

        return article
