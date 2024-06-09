import datetime

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Question

class QuestionModelTests(TestCase):
  def test_was_published_recently_with_future_question(self):
    """
    Test case to check the behavior of the `was_published_recently` method
    when a future question is provided.

    It creates a future question with a publication date 30 days ahead of the
    current time and asserts that the `was_published_recently` method returns
    False for this question.
    """
    time = timezone.now() + datetime.timedelta(days=30)
    future_question = Question(pub_date=time)
    self.assertIs(future_question.was_published_recently(), False)

  def test_was_publised_recently_with_old_question(self):
    """
    Test case to check the behavior of the `was_published_recently` method
    when the question's publication date is older than 24 hours.

    It creates a question with a publication date set to 1 day and 1 second ago,
    and asserts that the `was_published_recently` method returns False.
    """
    time = timezone.now() - datetime.timedelta(days=1, seconds=1)
    old_question = Question(pub_date=time)
    self.assertIs(old_question.was_published_recently(), False)

  def test_was_publised_recently_with_recent_question(self):
    """
    Test case to check if a recently published question is considered as published recently.
    """
    time = timezone.now() - datetime.timedelta(hours=23, minutes=59, seconds=59)
    recent_question = Question(pub_date=time)
    self.assertIs(recent_question.was_published_recently(), True)


def create_question(question_text, days):
  time = timezone.now() + datetime.timedelta(days=days)
  return Question.objects.create(question_text=question_text, pub_date=time)

class QuestionIndexViewTests(TestCase):
  def test_no_questions(self):
    response = self.client.get(reverse("polls:index"))
    self.assertEqual(response.status_code, 200)
    self.assertContains(response, "No polls are available")
    self.assertQuerySetEqual(response.context["latest_question_list"], [])
  
  def test_past_question(self):
    question = create_question(question_text="Past Question", days=-30)
    response = self.client.get(reverse("polls:index"))
    self.assertQuerySetEqual(
      response.context["latest_question_list"],
      [question],
    )

  def test_future_question(self):
    create_question(question_text="Future Question", days=30)
    response = self.client.get(reverse("polls:index"))
    self.assertContains(response, "No polls are available")
    self.assertQuerySetEqual(response.context["latest_question_list"], [])

  def test_future_question_and_past_question(self):
    past_question = create_question(question_text="Past Question", days=-30)
    future_question = create_question(question_text="Future Question", days=30)
    response = self.client.get(reverse("polls:index"))
    self.assertQuerySetEqual(
      response.context["latest_question_list"],
      [past_question],
    )

  def test_two_past_questions(self):
    question1 = create_question(question_text="Past Question 1", days=-30)
    question2 = create_question(question_text="Past Question 2", days=-5)
    response = self.client.get(reverse("polls:index"))
    self.assertQuerySetEqual(
      response.context["latest_question_list"],
      [question2, question1],
    )

class QuestionDetailViewTests(TestCase):
  def test_future_question(self):
      """
      The detail view of a question with a pub_date in the future
      returns a 404 not found.
      """
      future_question = create_question(question_text="Future question.", days=5)
      url = reverse("polls:detail", args=(future_question.id,))
      response = self.client.get(url)
      self.assertEqual(response.status_code, 404)

  def test_past_question(self):
      """
      The detail view of a question with a pub_date in the past
      displays the question's text.
      """
      past_question = create_question(question_text="Past Question.", days=-5)
      url = reverse("polls:detail", args=(past_question.id,))
      response = self.client.get(url)
      self.assertContains(response, past_question.question_text)