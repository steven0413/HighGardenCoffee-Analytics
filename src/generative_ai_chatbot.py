# src/generative_ai_chatbot.py
from openai import OpenAI
import pandas as pd

class CoffeeAnalyticsChatbot:
    def __init__(self, df, api_key):
        self.df = df
        self.client = OpenAI(api_key=api_key)
    
    def generate_context(self):
        """Generar contexto basado en los datos disponibles"""
        context = f"""
        Datos de consumo de café (1990-2020):
        - Países: {', '.join(self.df['country'].unique())}
        - Tipos de café: {', '.join(self.df['coffee_type'].unique())}
        - Rango temporal: {self.df['year'].min()} a {self.df['year'].max()}
        - Consumo total: {self.df['consumption_cups'].sum():,} tazas
        - Precio promedio: ${self.df['price_per_cup'].mean():.2f}
        
        Datos específicos para 2020:
        """
        
        # Agregar datos específicos de 2020
        data_2020 = self.df[self.df['year'] == 2020]
        if not data_2020.empty:
            consumption_by_country = data_2020.groupby('country')['consumption_cups'].sum()
            context += f"\nConsumo por país en 2020:\n"
            for country, consumption in consumption_by_country.items():
                context += f"- {country}: {consumption} tazas\n"
        
        return context
    
    def ask_question(self, question):
        """Responder pregunta basada en los datos"""
        context = self.generate_context()
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Eres un analista de datos especializado en café. Responde preguntas basándote en los datos proporcionados. Sé conciso y preciso."},
                    {"role": "user", "content": f"{context}\n\nPregunta: {question}\nRespuesta:"}
                ],
                max_tokens=500,
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error al procesar la pregunta: {str(e)}"