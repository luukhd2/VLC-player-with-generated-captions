"""
A python whisper script that can run in the terminal
"""

import whisper

import os 
import pathlib
import argparse


def get_model_set():
    models = "tiny.en,tiny,base.en,base,small.en,small,medium.en,medium,large-v1,large-v2,large"
    return models.split(",")

def get_language_set():
    langs = """af,am,ar,as,az,ba,be,bg,bn,bo,br,bs,ca,cs,cy,da,de,el,en,es,et,eu,fa,fi,fo,fr,gl,gu,ha,haw,he,
    hi,hr,ht,hu,hy,id,is,it,ja,jw,ka,kk,km,kn,ko,la,lb,ln,lo,lt,lv,mg,mi,mk,ml,mn,mr,ms,mt,my,ne,nl,nn,no,
    oc,pa,pl,ps,pt,ro,ru,sa,sd,si,sk,sl,sn,so,sq,sr,su,sv,sw,ta,te,tg,th,tk,tl,tr,tt,uk,ur,uz,vi,yi,yo,zh,Afrikaans,
    Albanian,Amharic,Arabic,Armenian,Assamese,Azerbaijani,Bashkir,Basque,Belarusian,Bengali,Bosnian,Breton,Bulgarian,Burmese,
    Castilian,Catalan,Chinese,Croatian,Czech,Danish,Dutch,English,Estonian,Faroese,Finnish,Flemish,French,Galician,Georgian,German,
    Greek,Gujarati,Haitian,Haitian Creole,Hausa,Hawaiian,Hebrew,Hindi,Hungarian,Icelandic,Indonesian,Italian,Japanese,Javanese,Kannada,
    Kazakh,Khmer,Korean,Lao,Latin,Latvian,Letzeburgesch,Lingala,Lithuanian,Luxembourgish,Macedonian,Malagasy,Malay,Malayalam,Maltese,
    Maori,Marathi,Moldavian,Moldovan,Mongolian,Myanmar,Nepali,Norwegian,Nynorsk,Occitan,Panjabi,Pashto,Persian,Polish,Portuguese,Punjabi,Pushto,
    Romanian,Russian,Sanskrit,Serbian,Shona,Sindhi,Sinhala,Sinhalese,Slovak,Slovenian,Somali,Spanish,Sundanese,Swahili,Swedish,Tagalog,Tajik,
    Tamil,Tatar,Telugu,Thai,Tibetan,Turkish,Turkmen,Ukrainian,Urdu,Uzbek,Valencian,Vietnamese,Welsh,Yiddish,Yoruba"""
    langs = langs.replace("\n", "")
    langs = langs.split(",")
    return list(map(str.strip, langs))

def run_whisper_in_terminal(model, download_root, audio_path, language, verbose=True):
    """
    model: <str>, example 'tiny'
    download_root: <pathlib.Path> dir where models are stored.
    language: <str> language of thet audio that will be transcribed.

    """
    model = whisper.load_model(model, download_root=download_root)
    result = model.transcribe(str(audio_path), verbose=verbose, language=language)
    print(result)


if __name__ == "__main__":
    PARSER = argparse.ArgumentParser()

    PARSER.add_argument("--model", choices=get_model_set(), required=True)
    PARSER.add_argument("--model_dir", type=pathlib.Path, required=True)
    PARSER.add_argument("--audio_path", type=pathlib.Path, required=True)
    PARSER.add_argument("--lan", choices=get_language_set(), required=True)
    
    ARGS = PARSER.parse_args()

    run_whisper_in_terminal(model=ARGS.model, download_root=ARGS.model_dir,
                            audio_path=ARGS.audio_path, language=ARGS.lan)
