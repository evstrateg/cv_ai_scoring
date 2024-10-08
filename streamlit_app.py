import openai
import os
import streamlit as st
from parse_hh import extract_candidate_data, extract_vacancy_data
import requests
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Укажите ваш API ключ OpenAI
openai.api_key = "OPENAI_API_KEY"  # Вставьте свой ключ API

SYSTEM_PROMPT = """
Оцените кандидата, насколько он подходит для данной вакансии.

Сначала напишите короткий анализ, который объяснит вашу оценку.
Отдельно оцените качество заполнения резюме (понятно ли, с какими задачами сталкивался кандидат и каким образом их решал?). Эта оценка должна учитываться при выставлении финальной оценки - нам важно нанимать таких кандидатов, которые могут рассказать про свою работу.
Потом представьте результат в виде оценки от 1 до 10.
""".strip()


def request_gpt(system_prompt, user_prompt):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",  # Убедитесь, что вы используете правильную модель
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=1000,
            temperature=0,
        )
        return response.choices[0].message.content.strip() 
    except Exception as e:
        logger.error(f"Ошибка при вызове OpenAI: {e}")
        return f"Ошибка при вызове OpenAI: {e}"


def get_html_content(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.85 Safari/537.36'
    }
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.text
        else:
            logger.error(f"Ошибка при получении HTML: {response.status_code}")
            logger.error(f"Ответ от сервера:\n{response.text}")  # Логирование HTML ответа
            return ''
    except Exception as e:
        logger.error(f"Ошибка при получении HTML: {e}")
        return ''


st.title("Оценка резюме кандидата")

job_description_url = st.text_area("Введите URL описания вакансии")
cv_url = st.text_area("Введите URL резюме кандидата")

if st.button("Оценить резюме"):
    # Проверяем, что URL корректные
    if not (job_description_url.startswith("http://") or job_description_url.startswith("https://")):
        st.error("Пожалуйста, введите корректный URL для описания вакансии.")
    elif not (cv_url.startswith("http://") or cv_url.startswith("https://")):
        st.error("Пожалуйста, введите корректный URL для резюме кандидата.")
    else:
        with st.spinner("Оцениваем резюме..."):
            # Получаем данные с сайтов вакансии и резюме
            job_description_html = get_html_content(job_description_url)
            if not job_description_html:
                st.error("Не удалось получить данные вакансии.")
                st.stop()  # Остановить выполнение

            job_description = extract_vacancy_data(job_description_html)

            cv_html = get_html_content(cv_url)
            if not cv_html:
                st.error("Не удалось получить данные резюме кандидата.")
                st.stop()  # Остановить выполнение

            cv = extract_candidate_data(cv_html)

            st.write("Описание вакансии:")
            st.write(job_description)
            st.write("Резюме кандидата:")
            st.write(cv)

            # Формируем запрос к GPT
            user_prompt = f"# ВАКАНСИЯ\n{job_description}\n\n# РЕЗЮМЕ\n{cv}"
            response = request_gpt(SYSTEM_PROMPT, user_prompt)

            # Отображаем ответ
            st.write(response)

