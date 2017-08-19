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


# class StudentRegistration(models.Model):
# 	user = models.ForeignKey(User,related_name='registration')
# 	registration_form = models.FileField()
	# user = models.OnetoOneField(User)
	# student_first_name = models.CharField(max_length=30)
	# student_last_name = models.CharField(max_length=30)
	# Male = 'Male'
	# Female = 'Female'
	# GENDER_CHOICES = (
	# 		(Male, 'Male'),
	# 		(Female, 'Female'),
	# 	)
	# student_gender = models.CharField(choices=GENDER_CHOICES)
	# student_birth_date = models.DateField()
	# student_email = models.EmailField(null=True,blank=True)
	# student_phone = models.CharField(max_length=10)

	# Yes = 'Yes'
	# No = 'No'
	# LIVING_CHOICES = (
	# 		(Yes, 'Yes'),
	# 		(No, 'No'),
	# 	)

	# father_first_name = models.CharField(max_length=30)
	# father_last_name = models.CharField(max_length=30)
	# father_phone = models.CharField(max_length=10)
	# father_email = models.EmailField()
	# father_street_adress = models.TextField()
	# father_city = models.TextField()
	# father_state = models.TextField()
	# father_zip_code = models.CharField(max_length=5)
	# father_lives_with_student = models.CharField(choices=LIVING_CHOICES)

	# mother_first_name = models.CharField(max_length=30)
	# mother_last_name = models.CharField(max_length=30)
	# mother_phone = models.CharField(max_length=10)
	# mother_email = models.EmailField()
	# mother_street_adress = models.TextField(null=True,blank=True)
	# mother_city = models.TextField(null=True,blank=True)
	# mother_state = models.TextField(null=True,blank=True)
	# mother_zip_code = models.CharField(max_length=5, null=True,blank=True)
	# mother_lives_with_student = models.CharField(choices=LIVING_CHOICES)

	# physical_disabilites = models.CharField(choices=LIVING_CHOICES,defualt=No)
	# allergies = models.CharField(choices=LIVING_CHOICES,defualt=No)
	# serious_illness = models.CharField(choices=LIVING_CHOICES,defualt=No)
	# please_explain = models.TextField(null=True,blank=True)




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
	unseen_quran_attendance = models.ManyToManyField('profiles.QuranAttendance', related_name='unseen_quran_attendance', blank=True)

	def __str__(self):
		return self.user.username



@receiver(post_save, sender=User)
def create_or_update_user_profile(sender,instance,created,**kwargs):
	if created:
		Profile.objects.create(user=instance)

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
				sheet3 = client.open("Quran Attendance Sample").sheet1
				 
				first_name = instance.first_name
				last_name = instance.last_name
				sheet.update_cell(instance.pk,1,first_name)
				sheet.update_cell(instance.pk,2,last_name)
				sheet.update_cell(instance.pk,3,instance.profile.quran_class)

				sheet2.update_cell(instance.pk,1,first_name)
				sheet2.update_cell(instance.pk,2,last_name)
				sheet2.update_cell(instance.pk,3,instance.profile.islamic_studies_class)

				sheet3.update_cell(instance.pk,1,first_name)
				sheet3.update_cell(instance.pk,2,last_name)
				sheet3.update_cell(instance.pk,3,instance.profile.quran_class)
			
			except BaseException:
				return reverse('home')

			weeks = SchoolWeek.objects.all()

			for week in weeks:
				QuranAttendance.objects.get_or_create(student=instance,week=week)

	instance.profile.save()

class SchoolWeek(models.Model):
	week_number = models.PositiveSmallIntegerField()
	date = models.DateField()

	def __str__(self):
		return 'Week '+str(self.week_number)+': '+str(self.date)

# @receiver(post_save, sender=SchoolWeek)
# def create_user_attendances(sender,instance,created,**kwargs):
# 	if created:
# 		users = User.objects.filter(profile__role='Student')
# 		for user in user:


		


class QuranAttendance(models.Model):

	week = models.ForeignKey(SchoolWeek,related_name='attendances')

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

	class_level = models.PositiveSmallIntegerField(choices=Q_CHOICES,null=True,blank=True)
	student = models.ForeignKey(User, limit_choices_to={'profile__role':'Student'},related_name='quran_attendance')

	Present = 'Present'
	Absent = 'Absent'
	Tardy = 'Tardy'
	NA = 'N/A'


	Attendance_choices = (
			(Present, 'Present'),
			(Absent, 'Absent'),
			(Tardy, 'Tardy'),
			(NA, 'N/A')
		)

	attendance = models.CharField(choices=Attendance_choices, max_length=10)

	posted_date = models.DateTimeField(default=timezone.now)

	def __str__(self):
		return self.student.first_name+' '+self.student.last_name+': '+str(self.week)+': '+self.attendance

	class Meta:
		unique_together = ('student','week')

	def get_absolute_url(self):
		return reverse('quran_attendance_list',kwargs={'pk':self.week.pk})


@receiver(post_save, sender=QuranAttendance)
def update_google_sheet_quran_attendance(sender,instance,created,**kwargs):
	try:
		# use creds to create a client to interact with the Google Drive API
		scope = ['https://spreadsheets.google.com/feeds']
		# json_data = os.path.join(BASE_DIR, 'static', "client_secret.json") NEED TO FIND HOW TO PROPERLY LINK JSON FILE
		# creds = ServiceAccountCredentials.from_json_keyfile_name('/Users/aamel786/desktop/development/arkportal/src/templates/client_secret.json', scope)
		creds = ServiceAccountCredentials.from_json_keyfile_name(CLIENT_JSON, scope)
		client = gspread.authorize(creds)
		 
		# Find a workbook by name and open the first sheet
		# Make sure you use the rit name here.
		sheet = client.open("Quran Attendance Sample").sheet1
		 
		
		sheet.update_cell(instance.student.pk,instance.week.week_number+7,instance.attendance)


	except BaseException:
		return reverse('student_detail',kwargs={'username':instance.student.username})

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







