"""
python3 -m pip install  googletrans==4.0.0-rc1
"""
from googletrans import Translator
import googletrans

def get_translator():
    return Translator()

def get_languages():
    """
    {'af': 'afrikaans', 'sq': 'albanian', 'am': 'amharic', 'ar': 'arabic', 'hy': 'armenian', 'az': 'azerbaijani', ...}
    """
    return googletrans.LANGUAGES

def translate_text(translator, text, src, dest):
    """ Translates a sentence, 

        returns string if succesfull
        returns None if failed
    """
    try:
        translation = translator.translate(text, src=src, dest=dest)
        return translation.text
    except TypeError:
        # TypeError: the JSON object must be str, bytes or bytearray, not NoneType
        # ^ This occurs when too many requests are passed to googletrans?
        return None 

def guaranteed_translate_text(translator, text, src, dest):
    """ Keep requesting for translation, can take up to an infite time due to while loop,

    DO NOT USE IN PRODUCTION CODE
    """
    out = None
    while out is None:
        out = translate_text(translator, text, src, dest)
    return out 

def get_word_list(sentence):
    return [word.strip() for word in sentence.split(" ") if len(word.strip()) > 0]

def translate_word_list(translator, word_list, src, dest, use_guaranteed=False):
    """
    returns: 
            Dict with input_word <str> : output_word <str>.
            Example:
                {'Это': 'This',
                 'работает': 'works'}
            None if failed.
                Set use_guaranteed to True to never fail (but can run for a very long (infinite) time)
    """
    joined_words = "\n".join(word_list)

    if use_guaranteed:
        translation = guaranteed_translate_text(translator=translator, text=joined_words, src=src, dest=dest)
    else:
        translation = translate_text(translator=translator, text=joined_words, src=src, dest=dest)
        if translation is None:
            return None
    
    # convert the line separated sentence translation to a dict
    translation_words = translation.split("\n")
    translate_dict = dict()
    for word, translation in zip(word_list, translation_words):
        translate_dict[word.strip()] = translation.strip()

    return translate_dict


def start_live_translation(loaded_subtitles, translation_dict, input_language, output_language,
                           combine_n_sentences=5):
    """
    combine_n_sentences: more sentences = less time to wait for googletrans.
                         downside is that long sentences may cause the api to return none
    """
    furthest_index = -1
    translator = get_translator()
    sentence_input = ""
    number_of_combined_sentences = 0
    while True:
        try:
            for index, (start_time, end_time, sentence) in enumerate(loaded_subtitles):
                # if never seen this sentence before
                if index > furthest_index and len(sentence) > 0:
                    furthest_index = index
                    sentence_input = f"{sentence_input} {sentence}"
                    number_of_combined_sentences += 1
                    
                    if number_of_combined_sentences >= combine_n_sentences:
                        # get the words
                        word_list = sentence_input.split()
                        sentence_translate_dict = translate_word_list(translator=translator, word_list=word_list,
                                                            src=input_language, dest=output_language, 
                                                            use_guaranteed=True)
                        # combine new sentences after this
                        sentence_input = ""
                        number_of_combined_sentences = 0
                        
                        # add words to translation dict
                        if sentence_translate_dict is not None:
                            for word_key, word_val in sentence_translate_dict.items():
                                translation_dict[word_key] = word_val 

        except Exception as error:
            print(error)


if __name__ == "__main__":
    print(googletrans.LANGUAGES)
    print("\n")

    translation = translate_text(get_translator(), text="Nu moet je stil zijn", src="nl", dest="en")
    print(translation)

    translation = guaranteed_translate_text(get_translator(), text="Nu moet je stil zijn", src="nl", dest="en")
    print(translation)

    trans_dict = translate_word_list(get_translator(), word_list=["Это", "работает"], src='ru', dest='en', use_guaranteed=True)    
    print(trans_dict)

