import nltk
import tiktoken
from nltk.tokenize import PunktSentenceTokenizer

class TextChunker:
    def __init__(self, max_tokens=50):
        if not nltk.download('punkt', quiet=True):
            nltk.download('punkt')
        self.max_tokens = max_tokens
        self.tokenizer = PunktSentenceTokenizer()
        self.encoding = tiktoken.get_encoding("cl100k_base")

    def count_tokens(self, text):
        return len(self.encoding.encode(text))

    def chunk_text_by_sentences(self, text):
        sentences = self.tokenizer.tokenize(text)
        chunks = []
        current_chunk = ""
        current_tokens = 0

        for sentence in sentences:
            sentence_tokens = self.count_tokens(sentence)

            if current_tokens + sentence_tokens <= self.max_tokens:
                current_chunk += " " + sentence
                current_tokens += sentence_tokens
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence
                current_tokens = sentence_tokens

        if current_chunk:
            chunks.append(current_chunk.strip())

        return chunks

    def chunk(self, text):
        return self.chunk_text_by_sentences(text)

if __name__ == "__main__":
    texte = """Bonjour ! Voici un long texte d’exemple. Il contient plusieurs phrases. 
    Chaque phrase sera analysée et regroupée intelligemment pour créer des morceaux 
    utilisables dans une base vectorielle sans dépasser les limites de token."""

    chunker = TextChunker()
    chunks = chunker.chunk(texte)
    for i, chunk in enumerate(chunks):
        print(f"Chunk {i+1} ({chunker.count_tokens(chunk)} tokens) :\n{chunk}\n")
