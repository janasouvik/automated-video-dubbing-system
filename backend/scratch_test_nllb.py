import os
from transformers import pipeline

print("Loading pipeline...")
try:
    p = pipeline("translation", model="facebook/nllb-200-distilled-600M", src_lang="hin_Deva", tgt_lang="eng_Latn", device=-1, max_length=512)
    print("Success")
except Exception as e:
    import traceback
    traceback.print_exc()
