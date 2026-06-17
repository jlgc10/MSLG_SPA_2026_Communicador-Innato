import requests
import re

class CorrectorGramatical:
    def __init__(self, api_key="AAAAAAAAAAAAAAAAAAAAAAAAA"): #Insertar API Key de Google Gemini aquí
        self.api_key = api_key
        #self.endpoint = "https://generativelanguage.googleapis.com/v1beta/models/gemma-4-31b-it:generateContent"
        self.endpoint = "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.1-flash-lite-preview:generateContent"
        #self.endpoint = "https://generativelanguage.googleapis.com/v1beta/models/gemma-4-26b-a4b-it:generateContent"
        self.system_instruction = """Eres un corrector gramatical y ortográfico especializado en español mexicano.

REGLAS GRAMATICALES QUE DEBES APLICAR:
1. Estructura SVO: toda oración debe tener Sujeto, Verbo y, cuando corresponda, Objeto en ese orden.
2. Conjugación verbal: corrige el verbo al tiempo, modo, persona y número correctos según el contexto.
3. Concordancia: el artículo, el sustantivo y el adjetivo deben coincidir en género y número.
4. Nexos: inserta los nexos coordinantes y subordinantes que falten (que, porque, pero, aunque, cuando, donde, etc.).
5. Artículos: usa artículos determinados (el, la, los, las) e indeterminados (un, una, unos, unas) donde sean necesarios.
6. Sujeto: reconstruye el sujeto explícito solo cuando su omisión genere ambigüedad.
7. Signos compuestos (+): Cuando encuentres palabras unidas por el signo '+', interpreta su significado compuesto o idiomático. Ejemplo: si a un concepto se le suma la palabra MUJER, usa su forma femenina ('MAESTRO+MUJER' = 'maestra'); si son complementarios, agrúpalos ('PAPÁ+MAMÁ' = 'padres'); si forman una expresión, tradúcela. Nunca los traduzcas de forma literal y separada.
8. Orden Tópico-Comentario: A veces se listan entidades de forma atípica (ej. 'SOFÍA SU PAPÁ+MAMÁ APROVECHARSE-DE APOYO'). Frecuentemente, la primera persona mencionada (Sofía) es el sujeto principal, y las menciones subsiguientes ('su papá+mamá') funcionan como complementos del objeto o del predicado (ej. 'Sofía se aprovecha del apoyo de sus papás'). Infiere lógicamente la relación en lugar de agruparlos forzosamente como un sujeto compuesto.
9. Agrupación Semántica (Objeto-Verbo): Si una emoción, estado o sustantivo abstracto aparece cerca de un verbo de petición o transferencia (como PEDIR, DAR, QUERER, NECESITAR), suele ser el objeto directo de la acción y no un adjetivo calificativo del sujeto. Por ejemplo: 'MAESTRO+MUJER CALMA ELLA YA PEDIR' se debe traducir como 'La maestra ya pidió calma' y NO como 'La maestra está calmada y pidió'. Interpreta el sentido general de la acción y ajusta los pronombres si es necesario para dar naturalidad (ej. 'nos pidió calma').

REGLAS ORTOGRÁFICAS QUE DEBES APLICAR:
1. Acentuación ortográfica: coloca tildes en palabras agudas, graves y esdrújulas según la norma.
2. Acentuación diacrítica: distingue tú/tu, él/el, sé/se, mí/mi, más/mas, sí/si, té/te, dé/de.
3. Signos de apertura: usa ¿ al inicio de preguntas y ¡ al inicio de exclamaciones.
4. Mayúscula inicial y punto final obligatorios.
5. Homófonos: corrige haber/a ver, hay/ahí/ay, sino/si no, porque/por qué/porqué/por que según contexto.
6. Uso de letras: aplica la norma RAE para b/v, c/s/z, g/j, h muda, ll/y en variante mexicana.

RESTRICCIONES ABSOLUTAS:
- Conserva la intención y el significado original del hablante.
- No añadas información que no esté implícita en el texto.
- Mantén el tono y registro: si el texto es coloquial, corrígelo formalmente pero sin volverlo pomposo.
- Al final de tu respuesta DEBES envolver tu oración corregida final entre las etiquetas <resultado> y </resultado>. 
"""

    def preprocesar(self, texto):
        if not isinstance(texto, str):
            raise TypeError("Sin cadena de texto.")
        
        normalizado = texto.strip()
        normalizado = normalizado.replace('dm-', '')
        normalizado = normalizado.replace('-', ' ')
        normalizado = normalizado.replace('#', '')
        
        normalizado = re.sub(r'[\r\n]+', ' ', normalizado)
        normalizado = re.sub(r'\s{2,}', ' ', normalizado)
        normalizado = re.sub(r'[""«»]', '"', normalizado)
        normalizado = re.sub(r"['']", "'", normalizado)
        normalizado = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', normalizado)
        
        if not normalizado:
            raise ValueError("Vacío después del preprocesamiento.")
        if len(normalizado) < 2:
            raise ValueError("Texto demasiado corto para ser procesado.")
            
        return normalizado

    def construir_prompt(self, texto):
        return {
            "systemInstruction": {
                "parts": [{"text": self.system_instruction}]
            },
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": texto}]
                }
            ],
            "generationConfig": {
                "temperature": 0.1,
                "maxOutputTokens": 512,
                "topP": 0.9
            }
        }

    def posprocesar(self, texto):
        match = re.search(r'<resultado>\s*(.*?)\s*</resultado>', texto, re.IGNORECASE | re.DOTALL)
        
        if match:
            resultado = match.group(1)
        else:
            # Fallback por si el modelo ignora la etiqueta
            lineas = texto.strip().split('\n')
            resultado = lineas[-1]
            resultado = resultado.replace("─", "")
            if ":*" in resultado:
                resultado = resultado.split(":*", 1)[-1]
            elif ": " in resultado:
                resultado = resultado.split(": ", 1)[-1]
                
        resultado = resultado.strip()
        resultado = re.sub(r'^["\'*#`\-–—]+', '', resultado)
        resultado = re.sub(r'["\'*#`]+$', '', resultado)
        resultado = resultado.strip()
        
        if len(resultado) > 0:
            resultado = resultado[0].upper() + resultado[1:]
        
        if len(resultado) > 0 and not re.search(r'[.?!…]$', resultado):
            resultado += "."
            
        if not resultado:
            raise ValueError("El posprocesamiento resultó en una cadena vacía.")
            
        return resultado

    def corregir(self, texto, max_intentos=6):
        if not texto or len(texto.strip()) < 2:
            return texto
            
        texto_limpio = self.preprocesar(texto)
        payload = self.construir_prompt(texto_limpio)
        url = f"{self.endpoint}?key={self.api_key}"
        
        headers = {"Content-Type": "application/json"}
        
        for intento in range(max_intentos):
            try:
                response = requests.post(url, headers=headers, json=payload, timeout=120)
                response.raise_for_status()
                datos = response.json()
                texto_ia = datos.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                
                if not texto_ia:
                    return texto
                    
                return self.posprocesar(texto_ia)
                #return texto_ia
            except Exception as e:
                print(f"Error en Gemini API para '{texto}' (Intento {intento + 1}/{max_intentos}): {e}")
                if intento == max_intentos - 1:
                    return texto
                import time
                time.sleep(2) # Espera antes del reintento
