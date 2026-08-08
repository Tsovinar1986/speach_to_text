import json
import os
import urllib.request

# Rewrites standard (literary) Eastern Armenian transcripts as colloquial
# spoken Yerevan Armenian, via a local Ollama model. Applied only when the
# transcribed language is Armenian.
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/chat")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:7b")

SYSTEM_PROMPT = (
    "Դու հայերենի բարբառագետ և սրբագրիչ ես։ Ստորև տրված ստանդարտ (գրական) "
    "արևելահայերեն տեքստը վերաշարադրիր Երևանի խոսակցական հայերենով, ինչպես "
    "երևանցին կխոսեր առօրյայում։\n"
    "Կանոններ.\n"
    "1. Իմաստը մի փոխիր, ոչինչ մի ավելացրու, մի բացատրիր և մի կրճատիր։\n"
    "2. Հատուկ անուններն ու թվերը (քաղաքներ, հաստատություններ, ամսաթվեր, "
    "ժամեր) գրիր ուղիղ և ճիշտ, առանց սխալների կամ այլ լեզվի բառերի։\n"
    "3. Ուղղագրական և տառասխալ մի թույլ տուր. ամեն բառ պետք է ճիշտ գրված "
    "հայերեն բառ լինի։\n"
    "4. Պատասխանիր բացառապես վերաշարադրված տեքստով, առանց նախաբանի կամ "
    "մեկնաբանության։"
)


def to_yerevan_dialect(text: str) -> str:
    """Rewrite standard Eastern Armenian text as colloquial spoken Yerevan Armenian."""
    if not text.strip():
        return text

    payload = {
        "model": OLLAMA_MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": text},
        ],
        "stream": False,
        "options": {"temperature": 0.2},
    }
    req = urllib.request.Request(
        OLLAMA_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        data = json.loads(resp.read())
    return data["message"]["content"].strip()
