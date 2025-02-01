from googletrans import Translator


async def translate_text(text: str, source: str, target: str):
    async with Translator() as translator:
        result= await translator.translate(text, src=source, dest=target)
    return result.text