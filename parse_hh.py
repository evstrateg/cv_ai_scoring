# parse_hh.py

from bs4 import BeautifulSoup
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def extract_vacancy_data(html):
    soup = BeautifulSoup(html, "html.parser")

    def get_text_or_default(tag, default="Данные не указаны"):
        return tag.get_text(strip=True) if tag else default

    # Извлечение данных о вакансии
    title = get_text_or_default(soup.find("h1", {"data-qa": "vacancy-title"}), "Заголовок не найден")
    salary = get_text_or_default(soup.find("span", {"data-qa": "vacancy-salary"}), "Зарплата не указана")
    experience = get_text_or_default(soup.find("span", {"data-qa": "vacancy-experience"}), "Опыт не указан")
    employment_mode = get_text_or_default(soup.find("p", {"data-qa": "vacancy-view-employment-mode"}), "Тип занятости не указан")
    company = get_text_or_default(soup.find("a", {"data-qa": "vacancy-company-name"}), "Компания не указана")
    location = get_text_or_default(soup.find("p", {"data-qa": "vacancy-view-location"}), "Местоположение не указано")
    description = get_text_or_default(soup.find("div", {"data-qa": "vacancy-description"}), "Описание не указано")

    skills_tags = soup.find_all("span", {"data-qa": "bloko-tag__text"})
    skills = [skill.get_text(strip=True) for skill in skills_tags] if skills_tags else []

    # Формирование строки в формате Markdown
    markdown = f"""
# {title}

**Компания:** {company}  
**Зарплата:** {salary}  
**Опыт работы:** {experience}  
**Тип занятости и режим работы:** {employment_mode}  
**Местоположение:** {location}  

## Описание вакансии
{description}

## Ключевые навыки
- {'\n- '.join(skills)}
"""
    return markdown.strip()

def extract_candidate_data(html):
    soup = BeautifulSoup(html, 'html.parser')

    def get_text_or_default(tag, default="Данные не указаны"):
        return tag.get_text(strip=True) if tag else default

    name = get_text_or_default(soup.find('span', {'data-qa': 'resume-personal-name'}), "Имя не указано")
    gender_age = get_text_or_default(soup.find('span', {'data-qa': 'resume-personal-gender-age'}), "Пол и возраст не указаны")
    location = get_text_or_default(soup.find('span', {'data-qa': 'resume-personal-address'}), "Местоположение не указано")
    job_title = get_text_or_default(soup.find('span', {'data-qa': 'resume-block-title-position'}), "Должность не указана")
    job_status = get_text_or_default(soup.find('span', {'data-qa': 'resume-block-job-search-status'}), "Статус не указан")

    experiences = []
    experience_section = soup.find('div', {'data-qa': 'resume-block-experience'})
    if experience_section:
        experience_items = experience_section.find_all('div', {'data-qa': 'resume-block-item'})
        for item in experience_items:
            period = get_text_or_default(item.find('div', {'data-qa': 'resume-experience-dates'}))
            company = get_text_or_default(item.find('div', {'data-qa': 'resume-experience-company'}), "Компания не указана")
            position = get_text_or_default(item.find('div', {'data-qa': 'resume-experience-position'}), "Позиция не указана")
            description = get_text_or_default(item.find('div', {'data-qa': 'resume-experience-description'}), "Описание не указано")

            experiences.append(f"**{period}**\n\n*{company}*\n\n**{position}**\n\n{description}\n")
    else:
        experiences.append("Опыт работы не указан")

    skills_section = soup.find('div', {'data-qa': 'skills-content'})
    skills = [skill.get_text(strip=True) for skill in skills_section.find_all('span', {'data-qa': 'bloko-tag__text'})] if skills_section else []

    markdown = f"# {name}\n\n"
    markdown += f"**{gender_age}**\n\n"
    markdown += f"**Местоположение:** {location}\n\n"
    markdown += f"**Должность:** {job_title}\n\n"
    markdown += f"**Статус:** {job_status}\n\n"
    markdown += "## Опыт работы\n\n"
    for exp in experiences:
        markdown += exp + "\n"
    markdown += "## Ключевые навыки\n\n"
    markdown += ', '.join(skills) + "\n"

    return markdown.strip()
