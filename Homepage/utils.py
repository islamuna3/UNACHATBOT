from .models import QuestionAnswer
# from fuzzywuzzy import fuzz
import openpyxl
# import spacy


# nlp = spacy.load('en_core_web_md')
#
# def get_similar_questions(user_question, questions, threshold=60):
#     similar_questions = []
#
#     for question in questions:
#         # Split the question into parts using commas
#         parts = [part.strip() for part in question.question.split(',')]
#
#         # Compare the user question with each part
#         for part in parts:
#             similarity = fuzz.ratio(user_question, part)
#             if similarity >= threshold:
#                 similar_questions.append(question)
#                 break  # No need to check other parts once a match is found
#
#     # Sort similar questions based on the similarity of the best match
#     return sorted(similar_questions, key=lambda x: fuzz.ratio(user_question, x.question), reverse=True)


def save_excel_to_db(uploaded_file):
    wb = openpyxl.load_workbook(uploaded_file)
    sheet = wb.active

    header = {cell.value: idx for idx, cell in enumerate(sheet[1])}
    question_col = header.get('question')
    answer_col = header.get('answer')

    if question_col is None or answer_col is None:
        raise ValueError("Excel file must contain 'question' and 'answer' columns")

    processed_data = []
    for row in sheet.iter_rows(min_row=2, values_only=True):
        question = row[question_col]
        answer = row[answer_col]
        if question and answer:
            if not QuestionAnswer.objects.filter(question=question).exists():
                question_answer = QuestionAnswer(question=question, answer=answer)
                question_answer.save()
                processed_data.append({'question': question, 'answer': answer})
    wb.close()
    return processed_data


