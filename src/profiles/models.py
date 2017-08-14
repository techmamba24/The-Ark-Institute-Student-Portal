from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.utils import timezone
from django.core.urlresolvers import reverse
from . utils import code_generator
from arkportal.settings.base import CLIENT_JSON
from django.core.validators import MaxValueValidator

import gspread
from oauth2client.service_account import ServiceAccountCredentials


# Create your models here.
class Profile(models.Model):

	# Role options for each user. Either student or teacher.

	Student = 'Student'
	Teacher = 'Teacher'


	ROLE_CHOICES = (
			(Student, 'Student'),
			(Teacher, 'Teacher'),
		)

	# Quran class options.

	Q1 = 1
	Q2 = 2
	Q3 = 3
	Q4 = 4
	Q5 = 5
	Q6 = 6
	Q7 = 7
	Q8 = 8
	Q9 = 9

	Q_CHOICES = (
			(Q1, 'Q1'),
			(Q2, 'Q2'),
			(Q3, 'Q3'),
			(Q4, 'Q4'),
			(Q5, 'Q5'),
			(Q6, 'Q6'),
			(Q7, 'Q7'),
			(Q8, 'Q8'),
			(Q9, 'Q9'),
		)

	# Islamic Studies class options.

	IS1 = 1
	IS2 = 2
	IS3 = 3
	IS4 = 4
	IS5 = 5
	IS6 = 6
	IS7 = 7
	IS8 = 8
	IS9 = 9

	IS_CHOICES = (
			(IS1, 'IS1'),
			(IS2, 'IS2'),
			(IS3, 'IS3'),
			(IS4, 'IS4'),
			(IS5, 'IS5'),
			(IS6, 'IS6'),
			(IS7, 'IS7'),
			(IS8, 'IS8'),
			(IS9, 'IS9'),
		)

	user = models.OneToOneField(User, on_delete=models.CASCADE)
	role = models.CharField(choices=ROLE_CHOICES, max_length=20, null=True, blank=True)
	quran_class = models.PositiveSmallIntegerField(choices=Q_CHOICES, null=True, blank=True)
	islamic_studies_class = models.PositiveSmallIntegerField(choices=IS_CHOICES, null=True, blank=True)
	unread_quran_posts = models.ManyToManyField('profiles.QuranPost', related_name='unread_quran_posts', blank=True)
	unread_quran_comments = models.ManyToManyField('profiles.QuranComment', related_name='unread_quran_comments', blank=True)
	unread_islamic_studies_posts = models.ManyToManyField('profiles.IslamicStudiesPost', related_name='unread_islamic_studies_posts', blank=True)
	unread_islamic_studies_comments = models.ManyToManyField('profiles.IslamicStudiesComment', related_name='unread_islamic_studies_comments', blank=True)
	unseen_quran_exams = models.ManyToManyField('profiles.QuranExam', related_name='unseen_quran_exams', blank=True)
	unseen_islamic_studies_exams = models.ManyToManyField('profiles.IslamicStudiesExam', related_name='unseen_islamic_studies_exams', blank=True)
	
	def __str__(self):
		return self.user.username



@receiver(post_save, sender=User)
def create_or_update_user_profile(sender,instance,created,**kwargs):
	if created:
		Profile.objects.create(user=instance)
	instance.profile.save()

	if instance.profile.role == 'Student':
		try:
			# use creds to create a client to interact with the Google Drive API
			scope = ['https://spreadsheets.google.com/feeds']
			# json_data = os.path.join(BASE_DIR, 'static', "client_secret.json") NEED TO FIND HOW TO PROPERLY LINK JSON FILE
			# creds = ServiceAccountCredentials.from_json_keyfile_name('/Users/aamel786/desktop/development/arkportal/src/templates/client_secret.json', scope)
			creds = ServiceAccountCredentials.from_json_keyfile_name(CLIENT_JSON, scope)
			client = gspread.authorize(creds)
			 
			# Find a workbook by name and open the first sheet
			# Make sure you use the rit name here.
			sheet = client.open("Quran Exam Scores Sample").sheet1
			sheet2 = client.open("IS Exam Scores Sample").sheet1
			 
			first_name = instance.first_name
			last_name = instance.last_name
			sheet.update_cell(instance.pk,1,first_name)
			sheet.update_cell(instance.pk,2,last_name)
			sheet.update_cell(instance.pk,3,instance.profile.quran_class)

			sheet2.update_cell(instance.pk,1,first_name)
			sheet2.update_cell(instance.pk,2,last_name)
			sheet2.update_cell(instance.pk,3,instance.profile.islamic_studies_class)
		
		except BaseException:
			return reverse('home')


class QuranExam(models.Model):

	exam1 = 1
	exam2 = 2
	exam3 = 3

	Exam_choices =(
		(exam1,'Exam 1'),
		(exam2,'Exam 2'),
		(exam3,'Exam 3')
		)

	Q1 = 1
	Q2 = 2
	Q3 = 3
	Q4 = 4
	Q5 = 5
	Q6 = 6
	Q7 = 7
	Q8 = 8
	Q9 = 9

	Q_CHOICES = (
			(Q1, 'Q1'),
			(Q2, 'Q2'),
			(Q3, 'Q3'),
			(Q4, 'Q4'),
			(Q5, 'Q5'),
			(Q6, 'Q6'),
			(Q7, 'Q7'),
			(Q8, 'Q8'),
			(Q9, 'Q9'),
		)

	exam_number = models.PositiveSmallIntegerField(choices=Exam_choices)
	exam_score = models.PositiveSmallIntegerField(validators=[MaxValueValidator(100)])
	student = models.ForeignKey(User, limit_choices_to={'profile__role':'Student'} ,related_name='quran_exam_scores')
	class_level = models.PositiveIntegerField(choices=Q_CHOICES,null=True,blank=True)
	posted_date = models.DateTimeField(default=timezone.now)
	# date_taken = models.DateTimeField()

	class Meta:
		unique_together = ('student','exam_number')

	def get_absolute_url(self):
		return reverse('student_detail',kwargs={'username':self.student.username})

	def __str__(self):
		return self.student.first_name+' '+self.student.last_name+': '+'Exam'+' '+str(self.exam_number)+': '+str(self.exam_score)

@receiver(post_save, sender=QuranExam)
def update_google_sheet_quran(sender,instance,created,**kwargs):
	try:
		# use creds to create a client to interact with the Google Drive API
		scope = ['https://spreadsheets.google.com/feeds']
		# json_data = os.path.join(BASE_DIR, 'static', "client_secret.json") NEED TO FIND HOW TO PROPERLY LINK JSON FILE
		# creds = ServiceAccountCredentials.from_json_keyfile_name('/Users/aamel786/desktop/development/arkportal/src/templates/client_secret.json', scope)
		creds = ServiceAccountCredentials.from_json_keyfile_name(CLIENT_JSON, scope)
		client = gspread.authorize(creds)
		 
		# Find a workbook by name and open the first sheet
		# Make sure you use the rit name here.
		sheet = client.open("Quran Exam Scores Sample").sheet1
		 
		exam_score = instance.exam_score
		if instance.exam_number == 1:
			sheet.update_cell(instance.student.pk,4,exam_score)
		elif instance.exam_number ==2:
			sheet.update_cell(instance.student.pk,5,exam_score)
		else:
			sheet.update_cell(instance.student.pk,6,exam_score)

	except BaseException:
		return reverse('student_detail',kwargs={'username':instance.student.username})


	# print(list_of_hashes)

class IslamicStudiesExam(models.Model):

	exam1 = 1
	exam2 = 2
	exam3 = 3

	Exam_choices =(
		(exam1,'Exam 1'),
		(exam2,'Exam 2'),
		(exam3,'Exam 3')
		)

	IS1 = 1
	IS2 = 2
	IS3 = 3
	IS4 = 4
	IS5 = 5
	IS6 = 6
	IS7 = 7
	IS8 = 8
	IS9 = 9

	IS_CHOICES = (
			(IS1, 'IS1'),
			(IS2, 'IS2'),
			(IS3, 'IS3'),
			(IS4, 'IS4'),
			(IS5, 'IS5'),
			(IS6, 'IS6'),
			(IS7, 'IS7'),
			(IS8, 'IS8'),
			(IS9, 'IS9'),
		)

	exam_number = models.PositiveSmallIntegerField(choices=Exam_choices)
	exam_score = models.PositiveSmallIntegerField(validators=[MaxValueValidator(100)])
	student = models.ForeignKey(User, limit_choices_to={'profile__role':'Student'} ,related_name='islamic_studies_exam_scores')
	class_level = models.PositiveIntegerField(choices=IS_CHOICES,null=True,blank=True)
	posted_date = models.DateTimeField(default=timezone.now)
	# date_taken = models.DateTimeField()

	class Meta:
		unique_together = ('student','exam_number')

	def get_absolute_url(self):
		return reverse('student_detail',kwargs={'username':self.student.username})

	def __str__(self):
		return self.student.first_name+' '+self.student.last_name+': '+'Exam'+' '+str(self.exam_number)+': '+str(self.exam_score)

@receiver(post_save, sender=IslamicStudiesExam)
def update_google_sheet_islamic_studies(sender,instance,created,**kwargs):
	try:
		# use creds to create a client to interact with the Google Drive API
		scope = ['https://spreadsheets.google.com/feeds']
		# json_data = os.path.join(BASE_DIR, 'static', "client_secret.json") NEED TO FIND HOW TO PROPERLY LINK JSON FILE
		# creds = ServiceAccountCredentials.from_json_keyfile_name('/Users/aamel786/desktop/development/arkportal/src/templates/client_secret.json', scope)
		creds = ServiceAccountCredentials.from_json_keyfile_name(CLIENT_JSON, scope)
		client = gspread.authorize(creds)
		 
		# Find a workbook by name and open the first sheet
		# Make sure you use the rit name here.
		sheet = client.open("IS Exam Scores Sample").sheet1

		exam_score = instance.exam_score
		if instance.exam_number == 1:
			sheet.update_cell(instance.student.pk,4,exam_score)
		elif instance.exam_number ==2:
			sheet.update_cell(instance.student.pk,5,exam_score)
		else:
			sheet.update_cell(instance.student.pk,6,exam_score)
	
	except BaseException:
		return reverse('student_detail',kwargs={'username':instance.student.username})

class QuranPost(models.Model):
	author = models.ForeignKey(User, related_name='quran_posts')
	title = models.CharField(max_length=200)
	message = models.TextField()
	upload = models.FileField(null=True, blank=True)
	class_level = models.PositiveSmallIntegerField()
	posted_date = models.DateTimeField(default=timezone.now)

	def get_absolute_url(self):
		return reverse("quran_post_detail",kwargs={'pk':self.pk})

	def __str__(self):
		return self.title
		

	# def read_quran_post(self):
	# 	self.read = True
	# 	self.save()

	# class Meta:
	# 	unique_together = ['author','message']

# @receiver(pre_save, sender=QuranPost, dispatch_uid=code_generator())
# def add_quran_post_to_unread(sender,instance,*args,**kwargs):
# 	user_profiles = Profile.objects.filter(quran_class=instance.class_level)
# 	# instance.save()
# 	print(len(user_profiles))
# 	for profile in user_profiles:
# 		# print(instance.title)
# 		# print(instance.class_level)
# 		print(profile.user.username)


class QuranComment(models.Model):
    post = models.ForeignKey('profiles.QuranPost', related_name='quran_comments')
    author = models.ForeignKey(User)
    comment = models.TextField()
    posted_date = models.DateTimeField(default=timezone.now)

    def get_absolute_url(self):
        return reverse("quran_post_detail",kwargs={'pk':self.post.pk})

    def __str__(self):
        return self.comment


class IslamicStudiesPost(models.Model):
	author = models.ForeignKey(User, related_name='islamic_studies_posts')
	title = models.CharField(max_length=200)
	message = models.TextField()
	upload = models.FileField(null=True, blank=True)
	class_level = models.PositiveSmallIntegerField()
	posted_date = models.DateTimeField(default=timezone.now)

	def get_absolute_url(self):
		return reverse("islamic_studies_post_detail",kwargs={'pk':self.pk})

	def __str__(self):
		return self.title

	class Meta:
		unique_together = ['author','message']


class IslamicStudiesComment(models.Model):
    post = models.ForeignKey('profiles.IslamicStudiesPost', related_name='islamic_studies_comments')
    author = models.ForeignKey(User)
    comment = models.TextField()
    posted_date = models.DateTimeField(default=timezone.now)

    def get_absolute_url(self):
        return reverse("islamic_studies_post_detail",kwargs={'pk':self.post.pk})

    def __str__(self):
        return self.comment







