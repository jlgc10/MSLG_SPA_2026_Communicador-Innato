import sys
import spacy

class RuleEngine:
    def __init__(self):
        try:
            self.nlp = spacy.load("es_core_news_md")
        except OSError:
            import subprocess
            subprocess.run([sys.executable, "-m", "spacy", "download", "es_core_news_sm"])
            self.nlp = spacy.load("es_core_news_sm")

    def spa_to_mslg(self, spa_text):
        doc = self.nlp(spa_text)
        mslg_tokens = []
        # Stopwords estándar de PNL
        stopwords = [
                "el", "la", "los", "las", "un", "una", "unos", "unas", 
                "este", "esta", "estos", "estas", "ese", "esa", "esos", "esas", 
                "mi", "tu", "su", "mis", "tus", "sus", "nuestro", "nuestra",
                "a", "ante", "bajo", "cabe", "con", "contra", "de", "desde", 
                "en", "entre", "hacia", "hasta", "para", "por", "según", 
                "sin", "so", "sobre", "tras", "y", "e", "ni", "que", "o", "u", 
                "pero", "aunque", "mas", "sino"
            ]
            
        verb_tokens = []
            
        for token in doc:
            t_upper = token.text.upper()
            t_lower = token.text.lower()
                
            # Conservar signos
            if token.text in ["¿", "?", "¡", "!"]:
                mslg_tokens.append(token.text)
                continue
                    
            # Eliminar stopwords
            if t_lower in stopwords or token.pos_ == "PUNCT":
                continue
                    
            w = t_upper
            is_verb = False
            
            # Obtener lemmatización
            if token.pos_ in ["VERB", "AUX"] and token.lemma_:
                w = token.lemma_.upper()
                is_verb = True
            # Regla #
            elif token.text.isupper() and len(token.text) > 1 and token.pos_ not in ["PUNCT"]:
                w = "#" + t_upper
            # Etiquetas PROPN -> dm-
            elif token.pos_ == "PROPN" and not is_verb and t_upper not in ["QUÉ", "CÓMO", "DÓNDE"]:
                w = "dm-" + t_upper
                    
            mslg_tokens.append(w)
            if is_verb:
                verb_tokens.append(w)
                    
        # Mover el verbo al final
        if verb_tokens:
            last_verb = verb_tokens[-1]
            for i in reversed(range(len(mslg_tokens))):
                if mslg_tokens[i] == last_verb:
                    v = mslg_tokens.pop(i)
                    if mslg_tokens and mslg_tokens[-1] in ["?", "!"]:
                        mslg_tokens.insert(len(mslg_tokens) - 1, v)
                    else:
                        mslg_tokens.append(v)
                    break
                        
            # Eliminar "SER"
        mslg_tokens = [t for t in mslg_tokens if t != "SER"]
        sentence = " ".join(mslg_tokens)
        # Eliminar espacios entre los signos de puntuación
        sentence = sentence.replace("¿ ", "¿").replace("¡ ", "¡").replace(" ?", "?").replace(" !", "!")

        return sentence
    
    