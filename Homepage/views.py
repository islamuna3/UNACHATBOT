from .forms import QuestionForm, UploadFileForm, AddQuestionForm, EditUnAnswerQuestionForm, FixedQuestionForm
from .models import QuestionAnswer, UnansweredQuestion, FixedQuestions
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
from rest_framework import viewsets, status
from bs4 import BeautifulSoup
from django.contrib import messages
from .utils import save_excel_to_db
from dotenv import load_dotenv
from django.db import models
from django.views import View
import urllib.parse
import requests
import json
import logging
import openai
import os
import re


class AskQuestionView(View):

    def __init__(self):
        load_dotenv()
        openai.api_key = os.getenv('OPENAI_API_KEY')

    def compare_with_openai1(self, question, db_questions):
        db_texts = "\n".join([f"Q{i + 1}: {q}" for i, q in enumerate(db_questions)])
        prompt = f"""
            سؤال المستخدم: "{question}"

            قائمة الأسئلة من قاعدة البيانات:
            {db_texts}

            يرجى مقارنة سؤال المستخدم مع الأسئلة في القائمة.
            إذا كان هناك أكثر من سؤال يتطابق، يرجى الرد فقط على شكل "Q<number>: question text".
            يرجى عدم تقديم أي معلومات إضافية مثل "الجواب" أو "السلام عليكم".
            إذا لم يكن هناك أي سؤال متشابه، يرجى الرد بـ "none".
        """
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=300,
                temperature=0.0
            )

            message = response.choices[0].message['content'].strip()

            if "none" in message.lower() or not message:
                return "none"

            # Parse the similar questions and ensure proper formatting
            similar_questions = message.splitlines()
            formatted_questions = []

            for q in similar_questions:
                # تعديل الـ regex للسماح ببعض النصوص الإضافية غير المتوقعة
                match = re.search(r'Q\d+:', q.strip())
                if match:
                    formatted_questions.append(q.strip())
                else:
                    print(f"Unexpected format: {q.strip()}")  # Log unexpected format for debugging

            # Return the first question if only one match is found
            if len(formatted_questions) == 1:
                return formatted_questions[0]

            return formatted_questions if formatted_questions else "none"

        # except openai.error.RateLimitError:
        #     print("Rate limit error. Retrying...")
        #     sleep(10)
        #     return self.compare_with_openai(question, db_questions)
        except Exception as e:
            print(f"An error occurred: {e}")
            return str(e)

    def compare_with_openai2(self, question):

        prompt = f"""
        أعد صياغة الجملة التالية بحيث تصبح مناسبة للبحث في موقع إخباري.
        استخدم لغة عربية دقيقة جدًا، خالية من الأخطاء الإملائية والنحوية، مع التأكد من وجود الهمزات.
        فقط أعد الكلمات المفتاحية الضرورية بدون أي تفاصيل أو كلمات إضافية.
        مثال:"اخر اخبار غزة دلوقتي"
        تصبح : أخبار غزة
        إذا كانت الجملة مناسبة بالفعل أعد إرسالها كما هي بدون أي إضافات أو تعديلات. إذا كانت الجملة غير صالحة، أرسل "none".

        الجملة: {question}
            """
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=300,
                temperature=0.0
            )

            message = response.choices[0].message['content'].strip()

            # Remove any quotation marks if present
            cleaned_message = message.replace('"', '').replace("'", "")

            if "none" in cleaned_message.lower() or not cleaned_message:
                return "none"

            return cleaned_message  # Return cleaned message without quotes

        except Exception as e:
            print(f"Error in OpenAI response: {e}")
            return "none"

    @csrf_exempt
    def question_view(self, request):
        logger = logging.getLogger(__name__)

        if request.method == 'OPTIONS':
            response = HttpResponse()
            response['Access-Control-Allow-Origin'] = '*'
            response['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
            response['Access-Control-Allow-Headers'] = 'Content-Type, X-CSRFToken'
            return response

        if request.method == 'POST':
            try:
                data = json.loads(request.body)
                question = data.get('question', '').strip()

                all_questions = QuestionAnswer.objects.all()
                best_matches = self.compare_with_openai1(question, [q.question for q in all_questions])

                logger.debug(f'Best match response: {best_matches}')

                if best_matches != "none":
                    if isinstance(best_matches, str):
                        match = re.match(r'^Q(\d+):', best_matches)
                        if match:
                            question_number = int(match.group(1))
                            selected_question = all_questions[question_number - 1]

                            selected_question.count += 1
                            selected_question.save()

                            return JsonResponse({
                                'answer': selected_question.answer
                            })
                    else:
                        # التعامل مع عدة أسئلة متشابهة
                        similar_questions_data = []
                        for best_question in best_matches:
                            match = re.match(r'^Q(\d+):', best_question)
                            if match:
                                question_number = int(match.group(1))
                                selected_question = all_questions[question_number - 1]
                                similar_questions_data.append({
                                    'id': selected_question.id,
                                    'question': selected_question.question,
                                    'answer': selected_question.answer
                                })
                                selected_question.count += 1
                                selected_question.save()

                        return JsonResponse({'similar_questions': similar_questions_data})

                UnansweredQuestion.objects.create(question=question)
                return JsonResponse({
                    'answer': 'عذراً لا يمكنني توفير إجابة لهذا السؤال. أنا لازلت تحت التدريب للإجابة على كل الأسئلة في سياق مجال عملنا. إذا كان سؤالك في هذا المجال، أعدك بتوفير الإجابة في المرة القادمة.'
                })

            except json.JSONDecodeError:
                return JsonResponse({'error': 'Invalid JSON'}, status=400)
            except Exception as e:
                logger.error(f"Unexpected error: {e}")
                return JsonResponse({'error': str(e)}, status=500)

        elif request.method == 'GET':
            question_id = request.GET.get('question_id')
            if question_id:
                try:
                    question = QuestionAnswer.objects.get(id=question_id)
                    return JsonResponse({'answer': question.answer})
                except QuestionAnswer.DoesNotExist:
                    return JsonResponse({'error': 'Question not found'}, status=404)
            else:
                return render(request, 'question.html')

        return JsonResponse({'error': 'Invalid request method'}, status=405)

    def get(self, request, question_id):
        try:
            question = QuestionAnswer.objects.get(id=question_id)
            return JsonResponse({'answer': question.answer})
        except QuestionAnswer.DoesNotExist:
            return JsonResponse({'error': 'Question not found'}, status=404)

    def search_in_una(self, query):
        encoded_query = urllib.parse.quote(query)
        search_url = f'https://una-oic.org/?s={encoded_query}'
        try:
            response = requests.get(search_url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            articles = []
            for post_item in soup.find_all('li', class_='post-item'):
                title_tag = post_item.find('h2', class_='post-title')
                link_tag = title_tag.find('a') if title_tag else None
                excerpt_tag = post_item.find('p', class_='post-excerpt')
                image_tag = post_item.find('img')
                date_tag = post_item.find('span', class_='date')
                search_url = search_url

                if link_tag and excerpt_tag:
                    title = link_tag.text.strip()
                    link = link_tag['href']
                    content = excerpt_tag.text.strip()
                    image_url = image_tag['src'] if image_tag else None
                    date = date_tag.text.strip()

                    articles.append({
                        'date': date,
                        'title': title,
                        'link': link,
                        'content': content,
                        'image_url': image_url,
                    })
                if len(articles) >= 5:
                    articles.append({
                        'search_url': search_url
                    })
                    break
            return articles
        except Exception as e:
            print(f"Error fetching search results: {e}")
            return []

    @csrf_exempt
    def una_question(self, request):
        if request.method == 'OPTIONS':
            response = HttpResponse()
            response['Access-Control-Allow-Origin'] = '*'
            response['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
            response['Access-Control-Allow-Headers'] = 'Content-Type, X-CSRFToken'
            return response

        if request.method == 'POST':
            try:
                data = json.loads(request.body)
                question = data.get('question', '').strip()
                question = self.compare_with_openai2(question)
                print(question)
                if question == 'none':
                    return JsonResponse({
                        'answer': 'عذراً لا يمكنني توفير إجابة لهذا السؤال. أنا لازلت تحت التدريب للإجابة على كل الأسئلة في سياق مجال عملنا. إذا كان سؤالك في هذا المجال، أعدك بتوفير الإجابة في المرة القادمة.'
                    })
                search_results = self.search_in_una(question)
                if search_results:
                    return JsonResponse({'question': question, 'answer': search_results}, status=200)
                else:
                    return JsonResponse({
                        'answer': 'عذراً لا يمكنني توفير إجابة لهذا السؤال. أنا لازلت تحت التدريب للإجابة على كل الأسئلة في سياق مجال عملنا. إذا كان سؤالك في هذا المجال، أعدك بتوفير الإجابة في المرة القادمة.'
                    })
            except json.JSONDecodeError:
                return JsonResponse({'error': 'Invalid JSON format'}, status=400)
                return JsonResponse({
                    'answer': 'عذراً لا يمكنني توفير إجابة لهذا السؤال. أنا لازلت تحت التدريب للإجابة على كل الأسئلة في سياق مجال عملنا. إذا كان سؤالك في هذا المجال، أعدك بتوفير الإجابة في المرة القادمة.'
                })
            except Exception as e:
                return JsonResponse({
                    'answer': 'عذراً لا يمكنني توفير إجابة لهذا السؤال. أنا لازلت تحت التدريب للإجابة على كل الأسئلة في سياق مجال عملنا. إذا كان سؤالك في هذا المجال، أعدك بتوفير الإجابة في المرة القادمة.'
                })
                return JsonResponse({'error': str(e)}, status=500)
                print(e)


class QuestionsView:

    def questions(self, request):
        all_data = QuestionAnswer.objects.all().order_by('-created_at')
        return render(request, 'upload.html', {'all_data': all_data})

    def upload_file_view(self, request):
        if request.method == 'POST':
            form = UploadFileForm(request.POST, request.FILES)
            if form.is_valid():
                try:
                    processed_data = save_excel_to_db(form.cleaned_data['file'])
                    return redirect('questions_view')
                except Exception as e:
                    return render(request, 'upload.html', {'form': form, 'error': str(e)})
        else:
            form = UploadFileForm()
        return render(request, 'upload.html', {'form': form})

    def add_question(self, request):

        form = AddQuestionForm(request.POST) if request.method == 'POST' else AddQuestionForm()

        if request.method == 'POST' and form.is_valid():
            question_text = form.cleaned_data['question']
            answer_text = form.cleaned_data['answer']

            # Check if a question with the same text already exists
            if not QuestionAnswer.objects.filter(question=question_text).exists():
                # If no duplicate is found, save the new question
                QuestionAnswer.objects.create(question=question_text, answer=answer_text)
                messages.success(request, "Question added successfully.")
                return redirect('questions_view')
            else:
                messages.warning(request, "This question already exists. Please enter a new question.")

        return redirect('questions_view')

    def edit_question(self, request, id):
        question_answer = get_object_or_404(QuestionAnswer, id=id)
        form = AddQuestionForm(request.POST, instance=question_answer) if request.method == 'POST' else AddQuestionForm(
            instance=question_answer)

        if request.method == 'POST' and form.is_valid():
            form.save()
            return redirect('questions_view')

        return render(request, 'edit_question.html', {'form': form})

    def delete_question(self, request, id):
        try:
            question_answer = QuestionAnswer.objects.get(id=id)
            if question_answer.fixed_question:
                messages.info(request, "This question cannot be deleted as it is linked to a fixed question.")
            else:
                question_answer.delete()
                messages.success(request, "Question deleted successfully.")
        except QuestionAnswer.DoesNotExist:
            messages.error(request, "The question you are trying to delete does not exist.")
        return redirect('questions_view')


class FixedQuestionsView:

    def fixed_questions(self, request):
        if request.method == 'POST':
            form = FixedQuestionForm(request.POST)
            if form.is_valid():
                question_text = form.cleaned_data['question']
                answer_text = form.cleaned_data['answer']

                # Check if a fixed question with the same text already exists
                if FixedQuestions.objects.filter(question=question_text).exists():
                    messages.warning(request, "This question already exists. Please enter a new question.")
                else:
                    # Save the fixed question and create a QuestionAnswer linked to it
                    fixed_question = form.save()
                    QuestionAnswer.objects.create(
                        question=question_text,
                        answer=answer_text,
                        fixed_question=fixed_question
                    )
                    messages.success(request, "Fixed question and answer saved successfully.")
                    return redirect('fixed_questions')
        else:
            form = FixedQuestionForm()

        fixed_questions = FixedQuestions.objects.all()
        return render(request, 'Fixed_question.html', {
            'form': form,
            'fixed_questions': fixed_questions
        })

    def edit_question(self, request, id):
        question = get_object_or_404(FixedQuestions, id=id)
        form = FixedQuestionForm(request.POST or None, instance=question)

        if request.method == 'POST' and form.is_valid():
            form.save()
            messages.success(request, "Question updated successfully.")
            # Also update the linked QuestionAnswer
            linked_answer = QuestionAnswer.objects.filter(fixed_question=question).first()
            if linked_answer:
                linked_answer.question = form.cleaned_data['question']
                linked_answer.answer = form.cleaned_data['answer']
                linked_answer.save()
            return redirect('fixed_questions')

        return render(request, 'edit_question.html', {'form': form, 'question': question})

    def delete_question(self, request, id):
        question = get_object_or_404(FixedQuestions, id=id)
        question.delete()
        messages.success(request, "Question deleted successfully.")
        return redirect('fixed_questions')

# class QuestionsView:
#
#     def questions(self, request):
#         all_data = QuestionAnswer.objects.all().order_by('-created_at')
#         print(all_data)
#         return render(request, 'upload.html', {'all_data': all_data})
#
#     def upload_file_view(self, request):
#         if request.method == 'POST':
#             form = UploadFileForm(request.POST, request.FILES)
#             if form.is_valid():
#                 try:
#                     processed_data = save_excel_to_db(form.cleaned_data['file'])
#                     return redirect('questions_view')
#                 except Exception as e:
#                     return render(request, 'upload.html', {'form': form, 'error': str(e)})
#         else:
#             form = UploadFileForm()
#         return render(request, 'upload.html', {'form': form})
#
#     def add_question(self, request):
#         form = AddQuestionForm(request.POST) if request.method == 'POST' else AddQuestionForm()
#
#         if request.method == 'POST' and form.is_valid():
#             question_text = form.cleaned_data['question']
#             answer_type = form.cleaned_data['answer_type']
#             answers_text = form.cleaned_data['answers']
#
#             # التحقق من وجود السؤال مسبقًا
#             if not QuestionAnswer.objects.filter(question=question_text).exists():
#                 # إنشاء السؤال بناءً على البيانات
#                 QuestionAnswer.objects.create(
#                     question=question_text,
#                     answer_type=answer_type,
#                     answers=answers_text
#                 )
#                 messages.success(request, "تم إضافة السؤال بنجاح.")
#                 return redirect('questions_view')
#             else:
#                 messages.warning(request, "هذا السؤال موجود بالفعل. من فضلك أدخل سؤالًا جديدًا.")
#
#         return render(request, 'upload.html', {'form': form})
#
#     def edit_question(self, request, id):
#         question_answer = get_object_or_404(QuestionAnswer, id=id)
#         form = AddQuestionForm(request.POST, instance=question_answer) if request.method == 'POST' else AddQuestionForm(
#             instance=question_answer)
#
#         if request.method == 'POST' and form.is_valid():
#             form.save()
#             return redirect('questions_view')
#
#         return render(request, 'edit_question.html', {'form': form})
#
#     def delete_question(self, request, id):
#         try:
#             question_answer = QuestionAnswer.objects.get(id=id)
#             if question_answer.fixed_question:
#                 messages.info(request, "This question cannot be deleted as it is linked to a fixed question.")
#             else:
#                 question_answer.delete()
#                 messages.success(request, "Question deleted successfully.")
#         except QuestionAnswer.DoesNotExist:
#             messages.error(request, "The question you are trying to delete does not exist.")
#         return redirect('questions_view')


class FixedQuestionsView:

    def fixed_questions(self, request):
        if request.method == 'POST':
            form = FixedQuestionForm(request.POST)
            if form.is_valid():
                question_text = form.cleaned_data['question']
                answer_text = form.cleaned_data['answer']

                # Check if a fixed question with the same text already exists
                if FixedQuestions.objects.filter(question=question_text).exists():
                    messages.warning(request, "This question already exists. Please enter a new question.")
                else:
                    # Save the fixed question and create a QuestionAnswer linked to it
                    fixed_question = form.save()
                    QuestionAnswer.objects.create(
                        question=question_text,
                        answer=answer_text,
                        fixed_question=fixed_question
                    )
                    messages.success(request, "Fixed question and answer saved successfully.")
                    return redirect('fixed_questions')
        else:
            form = FixedQuestionForm()

        fixed_questions = FixedQuestions.objects.all()
        return render(request, 'Fixed_question.html', {
            'form': form,
            'fixed_questions': fixed_questions
        })

    def edit_question(self, request, id):
        question = get_object_or_404(FixedQuestions, id=id)
        form = FixedQuestionForm(request.POST or None, instance=question)

        if request.method == 'POST' and form.is_valid():
            form.save()
            messages.success(request, "Question updated successfully.")
            # Also update the linked QuestionAnswer
            linked_answer = QuestionAnswer.objects.filter(fixed_question=question).first()
            if linked_answer:
                linked_answer.question = form.cleaned_data['question']
                linked_answer.answer = form.cleaned_data['answer']
                linked_answer.save()
            return redirect('fixed_questions')

        return render(request, 'edit_question.html', {'form': form, 'question': question})

    def delete_question(self, request, id):
        question = get_object_or_404(FixedQuestions, id=id)
        question.delete()
        messages.success(request, "Question deleted successfully.")
        return redirect('fixed_questions')


class UnAnsweredQuestionsView:

    def unanswered_questions(self, request):
        return render(request, 'unanswered_questions.html', {
            'unanswered_questions': UnansweredQuestion.objects.all()
        })

    def add_answer_to_question(self, request, question_id):
        question = get_object_or_404(UnansweredQuestion, id=question_id)
        form = AddQuestionForm(request.POST) if request.method == 'POST' else AddQuestionForm(
            initial={'question': question.question})

        if request.method == 'POST' and form.is_valid():
            answer = form.cleaned_data['answer']
            QuestionAnswer.objects.create(question=question.question, answer=answer)
            question.delete()
            return redirect('unanswered_questions')

        return render(request, 'add_answer.html', {'form': form, 'question': question})

    def edit_unanswer_question(self, request, question_id):
        question = get_object_or_404(UnansweredQuestion, id=question_id)
        form = EditUnAnswerQuestionForm(request.POST,
                                        instance=question) if request.method == 'POST' else EditUnAnswerQuestionForm(
            instance=question)

        if request.method == 'POST' and form.is_valid():
            form.save()
            return redirect('unanswered_questions')

        return render(request, 'edit_question.html', {'form': form, 'question': question})

    def delete_unanswer_question(self, request, question_id):
        get_object_or_404(UnansweredQuestion, id=question_id).delete()
        return redirect('unanswered_questions')

    def delete_all_unanswered_questions(self, request):
        UnansweredQuestion.objects.all().delete()
        return redirect('unanswered_questions')


class CounterView:

    def most_asked_questions(self, request):
        total_questions = QuestionAnswer.objects.aggregate(total=models.Sum('count'))['total'] or 1
        top_questions = QuestionAnswer.objects.all().order_by('-count')[:10]
        questions_data = []
        for question in top_questions:
            percentage = (question.count / total_questions) * 100
            questions_data.append({
                'question': question.question,
                'count': question.count,
                'percentage': round(percentage, 2)
            })

        return render(request, 'counter.html', {'questions_data': questions_data})


def custom_404(request, exception=None):
    return render(request, '404.html', status=404)


def custom_500(request):
    return render(request, '404.html', status=500)


def custom_403(request, exception=None):
    return render(request, '404.html', status=403)


def custom_400(request, exception=None):
    return render(request, '404.html', status=400)

# class AskQuestionView(View):
#
#     def __init__(self):
#         load_dotenv()
#         openai.api_key = os.getenv('OPENAI_API_KEY')
#
#     def get_embedding(self, text):
#         response = openai.Embedding.create(input=text, model="text-embedding-ada-002")
#         return response['data'][0]['embedding']
#
#     def ensure_embeddings_in_db(self):
#         questions_without_embeddings = QuestionAnswer.objects.filter(embedding__isnull=True)
#         if questions_without_embeddings :
#             print(questions_without_embeddings)
#         else:
#             print('NONE')
#         for question in questions_without_embeddings:
#             question.embedding = self.get_embedding(question.question)
#             print(f'this question : {question} sent to openai')
#             question.save()
#
#     def find_most_similar_question(self, user_embedding, db_questions):
#         db_embeddings = [np.array(q.embedding) for q in db_questions]
#         similarities = cosine_similarity([user_embedding], db_embeddings)
#         best_match_index = np.argmax(similarities)
#         best_match_score = similarities[0][best_match_index]
#
#         if best_match_score < 0.7:
#             return None, 0
#         else:
#             return db_questions[best_match_index], best_match_score
#
#     @csrf_exempt
#     def question_view(self, request):
#         if request.method == 'POST':
#             try:
#                 data = json.loads(request.body)
#                 question_text = data.get('question', '').strip()
#
#                 # تأكد من أن كل سؤال في قاعدة البيانات يحتوي على Embedding
#                 self.ensure_embeddings_in_db()
#
#                 # إنشاء Embedding لسؤال المستخدم
#                 user_embedding = self.get_embedding(question_text)
#
#                 # جلب جميع الأسئلة مع Embeddings من قاعدة البيانات
#                 db_questions = list(QuestionAnswer.objects.all())
#
#                 # العثور على الأسئلة المتشابهة بناءً على التشابه مع Embedding المستخدم
#                 similarities = []
#                 for question in db_questions:
#                     question_embedding = np.array(question.embedding)
#                     similarity_score = cosine_similarity([user_embedding], [question_embedding])[0][0]
#                     if similarity_score >= 0.85:  # حد التشابه
#                         similarities.append((question, similarity_score))
#
#                 # إذا وجد أكثر من سؤال مشابه، نقوم بإرجاع جميع الأسئلة المتشابهة
#                 if similarities:
#                     # ترتيب الأسئلة حسب درجة التشابه (الأعلى أولاً)
#                     similarities.sort(key=lambda x: x[1], reverse=True)
#                     similar_questions_data = []
#                     for question, score in similarities:
#                         similar_questions_data.append({
#                             'id': question.id,
#                             'question': question.question,
#                             'answer': question.answer,
#                             'similarity_score': score
#                         })
#                         # تحديث عداد السؤال
#                         question.count += 1
#                         question.save()
#
#                     return JsonResponse({'similar_questions': similar_questions_data})
#
#                 # إذا لم يتم العثور على تطابق قوي، حفظه كسؤال غير مجاب عليه
#                 UnansweredQuestion.objects.create(question=question_text)
#                 return JsonResponse({
#                     'answer': 'عذراً لا يمكنني توفير إجابة لهذا السؤال. أنا لازلت تحت التدريب للإجابة على كل الأسئلة في سياق مجال عملنا. إذا كان سؤالك في هذا المجال، أعدك بتوفير الإجابة في المرة القادمة.'
#                 })
#
#             except json.JSONDecodeError:
#                 return JsonResponse({'error': 'Invalid JSON'}, status=400)
#             except Exception as e:
#                 return JsonResponse({'error': str(e)}, status=500)
#
#         elif request.method == 'GET':
#             question_id = request.GET.get('question_id')
#             if question_id:
#                 try:
#                     question = QuestionAnswer.objects.get(id=question_id)
#                     return JsonResponse({'answer': question.answer})
#                 except QuestionAnswer.DoesNotExist:
#                     return JsonResponse({'error': 'Question not found'}, status=404)
#             else:
#                 return render(request, 'question.html')
#
#         return JsonResponse({'error': 'Invalid request method'}, status=405)
