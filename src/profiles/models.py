from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.utils import timezone
from django.core.urlresolvers import reverse
from . utils import code_generator
from arkportal.settings.base import CLIENT_JSON
from django.core.validators import MaxValueValidator
from django.db import transaction
from django.conf import settings
from django.core.mail import send_mail
from profiles.utils import code_generator


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
	IS10 = 10

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
			(IS10, 'IS10'),

		)

	user = models.OneToOneField(User, on_delete=models.CASCADE)
	parent_email = models.EmailField(null=True,blank=True)
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
	unseen_islamic_studies_attendance = models.ManyToManyField('profiles.IslamicStudiesAttendance', related_name='unseen_islamic_studies_attendance', blank=True)
	activation_email_sent = models.BooleanField(default=False)
	original_population = models.BooleanField(default=False)
	updated_google_sheets = models.BooleanField(default=False)

	def __str__(self):
		return self.user.username



@receiver(post_save, sender=User)
def create_or_update_user_profile(sender,instance,created,**kwargs):

	if created:
		Profile.objects.create(user=instance)
		

	new_teacher_pass = instance.last_name+code_generator()

	if instance.profile.role == 'Teacher' and instance.profile.activation_email_sent is False:

		instance.set_password(new_teacher_pass)

		subject = f"Your Ark Institute Student Portal Account Has Been Created"
		from_email = settings.DEFAULT_FROM_EMAIL
		message = ''
		recipient_list = [instance.email]
		html_message = f"Dear Teacher,<br><br>Your Ark Institute Student Portal account has been created. Here are your login credentials:<br><br>Username: {instance.username}<br>Password: {new_teacher_pass}<br><br>If you have trouble logging in, email student.portal@thearkinstitute.org so we can resolve the issue for you.<br><br> Thank You,<br><br>The Ark Institute."
		send_mail(subject, message, from_email, recipient_list, fail_silently=False, html_message=html_message)
			
		instance.profile.activation_email_sent = True

	if instance.profile.role == 'Teacher' and instance.profile.updated_google_sheets is False:

		try:
			# print('HELLO')
			# use creds to create a client to interact with the Google Drive API
			scope = ['https://spreadsheets.google.com/feeds']
			# json_data = os.path.join(BASE_DIR, 'static', "client_secret.json") NEED TO FIND HOW TO PROPERLY LINK JSON FILE
			# creds = ServiceAccountCredentials.from_json_keyfile_name('/Users/aamel786/desktop/development/arkportal/src/templates/client_secret.json', scope)
			creds = ServiceAccountCredentials.from_json_keyfile_name(CLIENT_JSON, scope)
			client = gspread.authorize(creds)
			 
			# Find a workbook by name and open the first sheet
			# Make sure you use the rit name here.
			sheet = client.open("Teacher Accounts 2017-2018").sheet1

			sheet.update_cell(instance.pk,1,instance.first_name)
			sheet.update_cell(instance.pk,2,instance.last_name)
			sheet.update_cell(instance.pk,3,instance.username)
			sheet.update_cell(instance.pk,4,new_teacher_pass)
			sheet.update_cell(instance.pk,5,instance.profile.quran_class)
			sheet.update_cell(instance.pk,6,instance.profile.islamic_studies_class)

		except BaseException as e:
			# print(e)
			return reverse('home')

		instance.profile.updated_google_sheets = True
		instance.profile.original_population = True



	new_student_pass = instance.last_name+code_generator()

	if instance.profile.role == 'Student' and instance.profile.original_population is False:

		weeks = SchoolWeek.objects.all()
		q_attd = []
		is_attd = []

		for week in weeks:
			qattd = QuranAttendance(student=instance,week=week,class_level=instance.profile.quran_class)
			isattd = IslamicStudiesAttendance(student=instance,week=week,class_level=instance.profile.islamic_studies_class)
			q_attd.append(qattd)
			is_attd.append(isattd)

		try:
			with transaction.atomic():
				QuranAttendance.objects.bulk_create(q_attd)
				IslamicStudiesAttendance.objects.bulk_create(is_attd)
		except BaseException:
			pass

		instance.profile.original_population = True


	if instance.profile.role == 'Student' and instance.profile.activation_email_sent is False:

		instance.set_password(new_student_pass)

		subject = f"Your Ark Institute Student Portal Account Has Been Created"
		from_email = settings.DEFAULT_FROM_EMAIL
		message = ''
		recipient_list = [instance.email,instance.profile.parent_email]
		html_message = f"Dear Student and Parent,<br><br>Your Ark Institute Student Portal account has been created. Here are your login credentials:<br><br>Username: {instance.username}<br>Password: {new_student_pass}<br><br>If you have trouble logging in, email student.portal@thearkinstitute.org so we can resolve the issue for you.<br><br> Thank You,<br><br>The Ark Institute."
		send_mail(subject, message, from_email, recipient_list, fail_silently=False, html_message=html_message)
		
		instance.profile.activation_email_sent = True

	if instance.profile.role == 'Student' and instance.profile.updated_google_sheets is False:

		try:
			# print('HELLO')
			# use creds to create a client to interact with the Google Drive API
			scope = ['https://spreadsheets.google.com/feeds']
			# json_data = os.path.join(BASE_DIR, 'static', "client_secret.json") NEED TO FIND HOW TO PROPERLY LINK JSON FILE
			# creds = ServiceAccountCredentials.from_json_keyfile_name('/Users/aamel786/desktop/development/arkportal/src/templates/client_secret.json', scope)
			creds = ServiceAccountCredentials.from_json_keyfile_name(CLIENT_JSON, scope)
			client = gspread.authorize(creds)
			 
			# Find a workbook by name and open the first sheet
			# Make sure you use the rit name here.
			sheet = client.open("Student Accounts 2017-2018").sheet1

			sheet.update_cell(instance.pk,1,instance.first_name)
			sheet.update_cell(instance.pk,2,instance.last_name)
			sheet.update_cell(instance.pk,3,instance.username)
			sheet.update_cell(instance.pk,4,new_student_pass)

		except BaseException:
			return reverse('home')

		instance.profile.updated_google_sheets = True

	instance.profile.save()


@receiver(post_save,sender=Profile)
def misc_updates(sender,instance,created,**kwargs):

	if instance.role == 'Student' and instance.updated_google_sheets is False:
		try:
			# print('HELLO')
			# use creds to create a client to interact with the Google Drive API
			scope = ['https://spreadsheets.google.com/feeds']
			# json_data = os.path.join(BASE_DIR, 'static', "client_secret.json") NEED TO FIND HOW TO PROPERLY LINK JSON FILE
			# creds = ServiceAccountCredentials.from_json_keyfile_name('/Users/aamel786/desktop/development/arkportal/src/templates/client_secret.json', scope)
			creds = ServiceAccountCredentials.from_json_keyfile_name(CLIENT_JSON, scope)
			client = gspread.authorize(creds)
			 
			# Find a workbook by name and open the first sheet
			# Make sure you use the rit name here.
			sheet = client.open("Quran Exam Scores Sample").sheet1
			sheet2 = client.open("Islamic Studies Exam Scores").sheet1
			sheet3 = client.open("Quran Attendance Sample").sheet1
			sheet4 = client.open("Islamic Studies Attendance Sample").sheet1

				 
			first_name = instance.user.first_name
			last_name = instance.user.last_name
			sheet.update_cell(instance.user.pk,1,first_name)
			sheet.update_cell(instance.user.pk,2,last_name)
			sheet.update_cell(instance.user.pk,3,instance.quran_class)

			sheet2.update_cell(instance.user.pk,1,first_name)
			sheet2.update_cell(instance.user.pk,2,last_name)
			sheet2.update_cell(instance.user.pk,3,instance.islamic_studies_class)

			sheet3.update_cell(instance.user.pk,1,first_name)
			sheet3.update_cell(instance.user.pk,2,last_name)
			sheet3.update_cell(instance.user.pk,3,instance.user.email)
			sheet3.update_cell(instance.user.pk,4,instance.parent_email)
			sheet3.update_cell(instance.user.pk,5,instance.quran_class)

			sheet4.update_cell(instance.user.pk,1,first_name)
			sheet4.update_cell(instance.user.pk,2,last_name)
			sheet4.update_cell(instance.user.pk,3,instance.user.email)
			sheet4.update_cell(instance.user.pk,4,instance.parent_email)
			sheet4.update_cell(instance.user.pk,5,instance.islamic_studies_class)

			instance.updated_google_sheets = True
			instance.save()
			
		except BaseException:
			return reverse('home')





class SchoolWeek(models.Model):
	week_number = models.PositiveSmallIntegerField()
	date = models.DateField()

	def __str__(self):
		return 'Week '+str(self.week_number)+': '+str(self.date)

	class Meta:
		unique_together = ('week_number','date')

# @receiver(post_save, sender=SchoolWeek)
# def create_user_attendances(sender,instance,created,**kwargs):
# 	if created:
# 		users = User.objects.filter(profile__role='Student')
# 		for user in user:

class QuranAttendance(models.Model):

	week = models.ForeignKey(SchoolWeek,related_name='quran_attendances')

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
		 
		
		sheet.update_cell(instance.student.pk,instance.week.week_number+8,instance.attendance)


	except BaseException:
		return reverse('student_detail',kwargs={'username':instance.student.username})



class IslamicStudiesAttendance(models.Model):

	week = models.ForeignKey(SchoolWeek,related_name='islamic_studies_attendances')

	IS1 = 1
	IS2 = 2
	IS3 = 3
	IS4 = 4
	IS5 = 5
	IS6 = 6
	IS7 = 7
	IS8 = 8
	IS9 = 9
	IS10 = 10

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
			(IS10, 'IS10'),

		)

	class_level = models.PositiveSmallIntegerField(choices=IS_CHOICES,null=True,blank=True)
	student = models.ForeignKey(User, limit_choices_to={'profile__role':'Student'},related_name='islamic_studies_attendance')

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
		return reverse('islamic_studies_attendance_list',kwargs={'pk':self.week.pk})


@receiver(post_save, sender=IslamicStudiesAttendance)
def update_google_sheet_islamic_studies_attendance(sender,instance,created,**kwargs):
	try:
		# use creds to create a client to interact with the Google Drive API
		scope = ['https://spreadsheets.google.com/feeds']
		# json_data = os.path.join(BASE_DIR, 'static', "client_secret.json") NEED TO FIND HOW TO PROPERLY LINK JSON FILE
		# creds = ServiceAccountCredentials.from_json_keyfile_name('/Users/aamel786/desktop/development/arkportal/src/templates/client_secret.json', scope)
		creds = ServiceAccountCredentials.from_json_keyfile_name(CLIENT_JSON, scope)
		client = gspread.authorize(creds)
		 
		# Find a workbook by name and open the first sheet
		# Make sure you use the rit name here.
		sheet = client.open("Islamic Studies Attendance Sample").sheet1
		 
		
		sheet.update_cell(instance.student.pk,instance.week.week_number+8,instance.attendance)


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
		# return reverse('student_detail',kwargs={'username':self.student.username})
		return reverse('quran_student_list')

	def __str__(self):
		return self.student.first_name+' '+self.student.last_name+': '+'Exam'+' '+str(self.exam_number)+': '+str(self.exam_score)

	def send_email(self):
		subject = f"Quran Exam {self.exam_number} Score Posted"
		from_email = settings.DEFAULT_FROM_EMAIL
		message = ''
		recipient_list = [self.student.email, self.student.profile.parent_email]
		html_message = f"Dear {self.student.first_name},<br><br>Your Quran teacher has posted an exam score for Exam {self.exam_number}. To view your score please login to your Student Portal account.<br><br> Thank You,<br><br>The Ark Institute."
		send_mail(subject, message, from_email, recipient_list, fail_silently=False, html_message=html_message)
		

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
	IS10 = 10

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
			(IS10, 'IS10'),
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
		# return reverse('student_detail',kwargs={'username':self.student.username})
		return reverse('islamic_studies_student_list')

	def __str__(self):
		return self.student.first_name+' '+self.student.last_name+': '+'Exam'+' '+str(self.exam_number)+': '+str(self.exam_score)


	def send_email(self):
		subject = f"Islamic Studies Exam {self.exam_number} Score Posted"
		from_email = settings.DEFAULT_FROM_EMAIL
		message = ''
		recipient_list = [self.student.email,self.student.profile.parent_email]
		html_message = f"Dear {self.student.first_name},<br><br>Your Islamic Studies teacher has posted an exam score for Exam {self.exam_number}. To view your score please login to your Student Portal account.<br><br> Thank You,<br><br>The Ark Institute."
		send_mail(subject, message, from_email, recipient_list, fail_silently=False, html_message=html_message)

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
		sheet = client.open("Islamic Studies Exam Scores").sheet1

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
		

	def teacherpost_send_email(self):
		recipients = list(User.objects.filter(profile__quran_class=self.class_level,profile__role='Student'))
		recipient_emails = []
		for item in recipients:
			if item.email:
				recipient_emails.append(item.email)

		subject = f"Your Quran Teacher Posted in the Classroom Discussion"
		from_email = settings.DEFAULT_FROM_EMAIL
		message = ''
		recipient_list = recipient_emails
		html_message = f"Dear Student,<br><br>Your Quran teacher has posted in the Classroom Discussion. To view their post please login to your Student Portal account.<br><br> Thank You,<br><br>The Ark Institute."
		send_mail(subject, message, from_email, recipient_list, fail_silently=False, html_message=html_message)

	def studentpost_send_email(self):
		recipients = list(User.objects.filter(profile__quran_class=self.class_level,profile__role='Teacher'))
		recipient_emails = []
		for item in recipients:
			if item.email:
				recipient_emails.append(item.email)

		subject = f"{self.author.first_name} {self.author.last_name} Posted in the Classroom Discussion"
		from_email = settings.DEFAULT_FROM_EMAIL
		message = ''
		recipient_list = recipient_emails
		html_message = f"Dear Teacher,<br><br>{self.author.first_name} {self.author.last_name} has posted in the Classroom Discussion of your Quran Class. To view their post please login to your Student Portal account.<br><br> Thank You,<br><br>The Ark Institute."
		send_mail(subject, message, from_email, recipient_list, fail_silently=False, html_message=html_message)

class QuranComment(models.Model):
	post = models.ForeignKey('profiles.QuranPost', related_name='quran_comments')
	author = models.ForeignKey(User)
	comment = models.TextField()
	posted_date = models.DateTimeField(default=timezone.now)

	def get_absolute_url(self):
		return reverse("quran_post_detail",kwargs={'pk':self.post.pk})

	def __str__(self):
		return self.comment

	def send_email_to_post_author(self):
		subject = f"{self.author.first_name} Commented On Your Quran Post"
		from_email = settings.DEFAULT_FROM_EMAIL
		message = ''
		recipient_list = [self.post.author.email]
		html_message = f"Dear User,<br><br>{self.author.first_name} {self.author.last_name} has commented on your post in the Quran Classroom Discussion. To view their comment please login to your Student Portal account.<br><br> Thank You,<br><br>The Ark Institute."
		send_mail(subject, message, from_email, recipient_list, fail_silently=False, html_message=html_message)


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

	def teacherpost_send_email(self):
		recipients = list(User.objects.filter(profile__islamic_studies_class=self.class_level,profile__role='Student'))
		recipient_emails = []
		for item in recipients:
			if item.email:
				recipient_emails.append(item.email)

		subject = f"Your Islamic Studies Teacher Posted in the Classroom Discussion"
		from_email = settings.DEFAULT_FROM_EMAIL
		message = ''
		recipient_list = recipient_emails
		html_message = f"Dear Student,<br><br>Your Islamic Studies teacher has posted in the Classroom Discussion. To view their post please login to your Student Portal account.<br><br> Thank You,<br><br>The Ark Institute."
		send_mail(subject, message, from_email, recipient_list, fail_silently=False, html_message=html_message)


	def studentpost_send_email(self):
		recipients = list(User.objects.filter(profile__islamic_studies_class=self.class_level,profile__role='Teacher'))
		recipient_emails = []
		for item in recipients:
			if item.email:
				recipient_emails.append(item.email)

		subject = f"{self.author.first_name} {self.author.last_name} Posted in the Classroom Discussion"
		from_email = settings.DEFAULT_FROM_EMAIL
		message = ''
		recipient_list = recipient_emails
		html_message = f"Dear Teacher,<br><br>{self.author.first_name} {self.author.last_name} has posted in the Classroom Discussion of your Islamic Studies Class. To view their post please login to your Student Portal account.<br><br> Thank You,<br><br>The Ark Institute."
		send_mail(subject, message, from_email, recipient_list, fail_silently=False, html_message=html_message)

class IslamicStudiesComment(models.Model):
	post = models.ForeignKey('profiles.IslamicStudiesPost', related_name='islamic_studies_comments')
	author = models.ForeignKey(User)
	comment = models.TextField()
	posted_date = models.DateTimeField(default=timezone.now)

	def get_absolute_url(self):
		return reverse("islamic_studies_post_detail",kwargs={'pk':self.post.pk})

	def __str__(self):
		return self.comment

	def send_email_to_post_author(self):
		subject = f"{self.author.first_name} Commented On Your Islamic Studies Post"
		from_email = settings.DEFAULT_FROM_EMAIL
		message = ''
		recipient_list = [self.post.author.email]
		html_message = f"Dear User,<br><br>{self.author.first_name} {self.author.last_name} has commented on your post in the Islamic Studies Classroom Discussion. To view their comment please login to your Student Portal account.<br><br> Thank You,<br><br>The Ark Institute."
		send_mail(subject, message, from_email, recipient_list, fail_silently=False, html_message=html_message)






