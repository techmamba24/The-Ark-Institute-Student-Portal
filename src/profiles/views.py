from django.shortcuts import render, get_object_or_404, redirect, HttpResponse, render_to_response, Http404
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.models import User
from . forms import QuranPostForm, QuranCommentForm, IslamicStudiesPostForm, IslamicStudiesCommentForm, QuranExamForm, IslamicStudiesExamForm, QuranAttendanceForm, IslamicStudiesAttendanceForm
from profiles.models import QuranPost, QuranComment, IslamicStudiesPost,IslamicStudiesComment, Profile, QuranExam, IslamicStudiesExam, SchoolWeek, QuranAttendance, IslamicStudiesAttendance
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.db.models import Q
from itertools import chain
from operator import attrgetter
from django.db import IntegrityError
from django.utils import timezone
from django.contrib import messages


User = get_user_model()

weekcount = 0

# Create your views here.
class DashboardView(LoginRequiredMixin, TemplateView):
	template_name = 'dashboardhome.html'

	def get_context_data(self,*args,**kwargs):
		context = super(DashboardView, self).get_context_data(*args,**kwargs)

		recent_quran_posts = QuranPost.objects.filter(class_level=self.request.user.profile.quran_class)
		recent_islamic_studies_posts = IslamicStudiesPost.objects.filter(class_level=self.request.user.profile.islamic_studies_class)
		recent_quran_comments = QuranComment.objects.filter(post__class_level=self.request.user.profile.quran_class)
		recent_islamic_studies_comments = IslamicStudiesComment.objects.filter(post__class_level=self.request.user.profile.islamic_studies_class)
		recent_quran_exams = QuranExam.objects.filter(student=self.request.user)
		recent_islamic_studies_exams = IslamicStudiesExam.objects.filter(student=self.request.user)
		# recent_quran_attendance = QuranAttendance.objects.filter(student=self.request.user)
		recent_quran_activity = sorted(chain(recent_quran_posts,recent_quran_comments, recent_quran_exams), key=attrgetter('posted_date'))
		recent_islamic_studies_activity = sorted(chain(recent_islamic_studies_posts, recent_islamic_studies_comments, recent_islamic_studies_exams), key=attrgetter('posted_date'))
		context['recent_quran'] = list(reversed(recent_quran_activity[-3:]))
		context['recent_islamic_studies'] = list(reversed(recent_islamic_studies_activity[-3:]))

		return context




class QuranClassListView(LoginRequiredMixin, ListView):
	template_name = 'qroster.html'

	def get_queryset(self):
		return User.objects.filter(profile__quran_class=self.request.user.profile.quran_class, profile__role='Student')

	def get_context_data(self,*args,**kwargs):
		context = super(QuranClassListView, self).get_context_data(*args,**kwargs)
		teachers = User.objects.filter(profile__quran_class=self.request.user.profile.quran_class, profile__role='Teacher')
		context['teachers'] = teachers
		return context

class ISClassListView(LoginRequiredMixin, ListView):
	template_name = 'isroster.html'

	def get_queryset(self):
		return User.objects.filter(profile__islamic_studies_class=self.request.user.profile.islamic_studies_class, profile__role='Student')
	
	def get_context_data(self,*args,**kwargs):
		context = super(ISClassListView, self).get_context_data(*args,**kwargs)
		teachers = User.objects.filter(profile__islamic_studies_class=self.request.user.profile.islamic_studies_class, profile__role='Teacher')
		context['teachers'] = teachers
		return context

class QuranPostListView(LoginRequiredMixin, ListView):
	model = QuranPost
	template_name = 'quran_post_list.html'
	def get_queryset(self):
		return QuranPost.objects.filter(class_level=self.request.user.profile.quran_class).order_by('-posted_date')

class QuranPostDetailView(LoginRequiredMixin, DetailView):
	model = QuranPost
	template_name = 'quran_post_detail.html'

	def get_context_data(self,*args,**kwargs):
		if self.object in self.request.user.profile.unread_quran_posts.all():
			self.request.user.profile.unread_quran_posts.remove(self.object)

		for comment in self.request.user.profile.unread_quran_comments.all():
			if comment.post == self.object:
				self.request.user.profile.unread_quran_comments.remove(comment)

		return super(QuranPostDetailView, self).get_context_data(*args,**kwargs)


class QuranCreatePostView(LoginRequiredMixin, CreateView):
	model = QuranPost
	redirect_field_name = '/quran_post_detail.html'
	form_class = QuranPostForm
	template_name = 'quran_post_form.html'

	def form_valid(self,form):
		self.object = form.save(commit=False)
		self.object.author = self.request.user
		self.object.class_level = self.request.user.profile.quran_class
		self.object.save()
		user_profiles = Profile.objects.filter(quran_class=self.object.class_level)
		for profile in user_profiles:
			if profile.user != self.request.user:
				profile.unread_quran_posts.add(self.object)
		return super().form_valid(form)


@login_required
def add_comment_to_quran_post(request, pk):
	post = get_object_or_404(QuranPost, pk=pk)
	if request.method == "POST":
		form = QuranCommentForm(request.POST)
		if form.is_valid():
			comment = form.save(commit=False)
			comment.post = post
			comment.author = request.user
			comment.save()
			user_profiles = Profile.objects.filter(quran_class=post.class_level)
			print(len(user_profiles))
			for profile in user_profiles:
				if profile.user != request.user:
					profile.unread_quran_comments.add(comment)
			return redirect('quran_post_detail', pk=post.pk)
	else:
		form = QuranCommentForm()
	return render(request, 'quran_comment_form.html', {'form': form})


class IslamicStudiesPostListView(LoginRequiredMixin, ListView):
	model = IslamicStudiesPost
	template_name = 'islamic_studies_post_list.html'
	def get_queryset(self):
		return IslamicStudiesPost.objects.filter(class_level=self.request.user.profile.islamic_studies_class).order_by('-posted_date')

class IslamicStudiesPostDetailView(LoginRequiredMixin, DetailView):
	model = IslamicStudiesPost
	template_name = 'islamic_studies_post_detail.html'

	def get_context_data(self,*args,**kwargs):
		if self.object in self.request.user.profile.unread_islamic_studies_posts.all():
			self.request.user.profile.unread_islamic_studies_posts.remove(self.object)

		for comment in self.request.user.profile.unread_islamic_studies_comments.all():
			if comment.post == self.object:
				self.request.user.profile.unread_islamic_studies_comments.remove(comment)

		return super(IslamicStudiesPostDetailView, self).get_context_data(*args,**kwargs)



class IslamicStudiesCreatePostView(LoginRequiredMixin, CreateView):
	model = IslamicStudiesPost
	redirect_field_name = '/islamic_studies_post_detail.html'
	form_class = IslamicStudiesPostForm
	template_name = 'islamic_studies_post_form.html'

	def form_valid(self,form):
		self.object = form.save(commit=False)
		self.object.author = self.request.user
		self.object.class_level = self.request.user.profile.islamic_studies_class
		self.object.save()
		user_profiles = Profile.objects.filter(islamic_studies_class=self.object.class_level)
		for profile in user_profiles:
			if profile.user != self.request.user:
				profile.unread_islamic_studies_posts.add(self.object)
		return super().form_valid(form)


@login_required
def add_comment_to_islamic_studies_post(request, pk):
	post = get_object_or_404(IslamicStudiesPost, pk=pk)
	if request.method == "POST":
		form = IslamicStudiesCommentForm(request.POST)
		if form.is_valid():
			comment = form.save(commit=False)
			comment.post = post
			comment.author = request.user
			comment.save()
			user_profiles = Profile.objects.filter(islamic_studies_class=post.class_level)
			for profile in user_profiles:
				if profile.user != request.user:
					profile.unread_islamic_studies_comments.add(comment)
			return redirect('islamic_studies_post_detail', pk=post.pk)
	else:
		form = IslamicStudiesCommentForm()
	return render(request, 'islamic_studies_comment_form.html', {'form': form})

class QuranTeacherStudentList(LoginRequiredMixin, ListView):
	model = User
	template_name = 'teachers/teacher_quran_student_list.html'

	def get_queryset(self):
		return User.objects.filter(profile__quran_class=self.request.user.profile.quran_class).exclude(profile__role='Teacher')


class QuranExamScoreAdd(LoginRequiredMixin, CreateView):
	model = QuranExam
	form_class = QuranExamForm
	template_name = 'teachers/quran_score_add.html'

	def get_context_data(self,*args,**kwargs):
		context = super(QuranExamScoreAdd,self).get_context_data(*args,**kwargs)
		student = self.kwargs['student']
		userobj = User.objects.filter(username__iexact=student).first()
		context['full_name'] = userobj.first_name+' '+userobj.last_name
		context['userobj'] = userobj
		return context

	def form_valid(self,form):
		try:
			self.object = form.save(commit=False)
			context = self.get_context_data()
			# student = self.kwargs['student']
			# userobj = User.objects.filter(username__iexact=student).first()
			self.object.student = context['userobj']
			self.object.class_level = self.request.user.profile.quran_class
			self.object.save()
			messages.success(self.request, f"Successfully posted Exam {self.object.exam_number} score for {self.object.student.first_name} {self.object.student.last_name}")
			self.object.student.profile.unseen_quran_exams.add(self.object)

		except IntegrityError as e:
				messages.error(self.request, f"You already posted an Exam {self.object.exam_number} score for {self.object.student.first_name} {self.object.student.last_name}")
				return redirect('quran_student_list')

		return super().form_valid(form)

class QuranExamScoreUpdate(LoginRequiredMixin,UpdateView):
	model = QuranExam
	form_class = QuranExamForm
	template_name = 'teachers/quran_score_update.html'

	def get_context_data(self,*args,**kwargs):
		context = super(QuranExamScoreUpdate,self).get_context_data(*args,**kwargs)
		student = self.kwargs['student']
		userobj = User.objects.filter(username__iexact=student).first()
		context['full_name'] = userobj.first_name+' '+userobj.last_name
		context['userobj'] = userobj
		return context

	def form_valid(self,form):
		self.object = form.save(commit=False)
		self.object.posted_date = timezone.now()
		self.object.save()
		context = self.get_context_data()
		context['userobj'].profile.unseen_quran_exams.add(self.object)
		return super().form_valid(form)


class IslamicStudiesTeacherStudentList(LoginRequiredMixin, ListView):
	model = User
	template_name = 'teachers/teacher_islamic_studies_student_list.html'

	def get_queryset(self):
		return User.objects.filter(profile__islamic_studies_class=self.request.user.profile.quran_class).exclude(profile__role='Teacher')


class IslamicStudiesExamScoreAdd(LoginRequiredMixin, CreateView):
	model = IslamicStudiesExam
	form_class = IslamicStudiesExamForm
	template_name = 'teachers/islamic_studies_score_add.html'

	def get_context_data(self,*args,**kwargs):
		context = super(IslamicStudiesExamScoreAdd,self).get_context_data(*args,**kwargs)
		student = self.kwargs['student']
		userobj = User.objects.filter(username__iexact=student).first()
		context['full_name'] = userobj.first_name+' '+userobj.last_name
		context['userobj'] = userobj
		return context

	def form_valid(self,form):
		try:
			self.object = form.save(commit=False)
			context = self.get_context_data()
			# student = self.kwargs['student']
			# userobj = User.objects.filter(username__iexact=student).first()
			self.object.student = context['userobj']
			self.object.class_level = self.request.user.profile.islamic_studies_class
			self.object.save()
			messages.success(self.request, f"Successfully posted Exam {self.object.exam_number} score for {self.object.student.first_name} {self.object.student.last_name}")
			context['userobj'].profile.unseen_islamic_studies_exams.add(self.object)

		except IntegrityError as e:
			messages.error(self.request, f"Error: You already posted an Exam {self.object.exam_number} score for {self.object.student.first_name} {self.object.student.last_name}!")
			return redirect('islamic_studies_student_list')
		
		return super().form_valid(form)

class IslamicStudiesExamScoreUpdate(LoginRequiredMixin,UpdateView):
	model = IslamicStudiesExam
	form_class = IslamicStudiesExamForm
	template_name = 'teachers/islamic_studies_score_update.html'

	def get_context_data(self,*args,**kwargs):
		context = super(IslamicStudiesExamScoreUpdate,self).get_context_data(*args,**kwargs)
		student = self.kwargs['student']
		userobj = User.objects.filter(username__iexact=student).first()
		context['full_name'] = userobj.first_name+' '+userobj.last_name
		context['userobj'] = userobj
		return context

	def form_valid(self,form):
		self.object = form.save(commit=False)
		self.object.posted_date = timezone.now()
		self.object.save()
		context = self.get_context_data()
		context['userobj'].profile.unseen_islamic_studies_exams.add(self.object)
		return super().form_valid(form)


class StudentDetail(LoginRequiredMixin,DetailView):
	template_name = 'student_detail.html'

	def get_object(self):
		username = self.kwargs.get('username')
		if not username:
			raise Http404
		return get_object_or_404(User, username__iexact=username, profile__role='Student')


	def get_context_data(self,*args,**kwargs):
		context = super(StudentDetail,self).get_context_data(*args,**kwargs)
		student = self.kwargs['username']
		userobj = User.objects.filter(username__iexact=student).first()

		quran_results = userobj.quran_exam_scores.all()
		if quran_results.exists():
			quran_average = 0
			for result in quran_results:
				quran_average += result.exam_score
			quran_average = quran_average/len(quran_results)
			context['quran_average'] = quran_average
		
		islamic_studies_results = userobj.islamic_studies_exam_scores.all()
		if islamic_studies_results.exists():
			islamic_studies_average = 0
			for result in islamic_studies_results:
				islamic_studies_average += result.exam_score
			islamic_studies_average = islamic_studies_average/len(islamic_studies_results)
			context['islamic_studies_average'] = islamic_studies_average

		quran_attendance_absent = userobj.quran_attendance.filter(attendance='Absent').count()
		quran_attendance_present = userobj.quran_attendance.filter(attendance='Present').count()
		quran_attendance_tardy = userobj.quran_attendance.filter(attendance='Tardy').count()
		total_quran_attendance = quran_attendance_present + quran_attendance_absent + quran_attendance_tardy

		if total_quran_attendance > 0:

			quran_attendance_average = ( ( quran_attendance_present + quran_attendance_tardy - (quran_attendance_tardy//2) ) / total_quran_attendance ) * 100
			print(quran_attendance_average)
			context['quran_attendance_average'] = quran_attendance_average

		islamic_studies_attendance_absent = userobj.islamic_studies_attendance.filter(attendance='Absent').count()
		islamic_studies_attendance_present = userobj.islamic_studies_attendance.filter(attendance='Present').count()
		islamic_studies_attendance_tardy = userobj.islamic_studies_attendance.filter(attendance='Tardy').count()
		total_islamic_studies_attendance = islamic_studies_attendance_present + islamic_studies_attendance_absent + islamic_studies_attendance_tardy

		if total_islamic_studies_attendance > 0:

			islamic_studies_attendance_average = ( ( islamic_studies_attendance_present + islamic_studies_attendance_tardy - (islamic_studies_attendance_tardy//2) ) / total_islamic_studies_attendance ) * 100

			context['islamic_studies_attendance_average'] = islamic_studies_attendance_average


		if len(quran_results) == 3 and len(islamic_studies_results) == 3:
			quran_overall_average = 0
			for result in quran_results:
				if result.exam_number == 1:
					quran_overall_average+=(0.25*result.exam_score)
				elif result.exam_number == 2:
					quran_overall_average+=(0.30*result.exam_score)
				else:
					quran_overall_average+=(0.35*result.exam_score)
			quran_overall_average+=(.1*quran_attendance_average)

			islamic_studies_overall_average = 0
			for result in islamic_studies_results:
				if result.exam_number == 1:
					islamic_studies_overall_average+=(0.25*result.exam_score)
				elif result.exam_number == 2:
					islamic_studies_overall_average+=(0.30*result.exam_score)
				else:
					islamic_studies_overall_average+=(0.35*result.exam_score)
			islamic_studies_overall_average+=(.1*islamic_studies_attendance_average)

			overall_average = (quran_overall_average+islamic_studies_overall_average)/2

			context['overall_average'] = overall_average




		if self.request.user.profile.role == 'Student':
			for exam in self.request.user.profile.unseen_quran_exams.all():
				self.request.user.profile.unseen_quran_exams.remove(exam)

			for exam in self.request.user.profile.unseen_islamic_studies_exams.all():
				self.request.user.profile.unseen_islamic_studies_exams.remove(exam)

		return context
	# 	context['full_name'] = userobj.first_name+' '+userobj.last_name
	# 	class_results_exam1 = QuranExam.objects.filter(class_level=userobj.profile.quran_class, exam_number=1)


	# 	context['exam1_average'] = exam1average
	# 	context['exam2_average'] = exam2average
	# 	context['exam3_average'] = exam3average

	# 	return context

	# def get_queryset(self):
	# 	student = self.kwargs['student']
	# 	userobj = User.objects.filter(username__iexact=student).first()
	# 	return QuranExam.objects.filter(student__username=userobj.username).order_by('posted_date')


class TeacherDetail(LoginRequiredMixin,DetailView):
	template_name = 'teacher_detail.html'

	def get_object(self):
		username = self.kwargs.get('username')
		if not username:
			raise Http404
		return get_object_or_404(User, username__iexact=username, profile__role='Teacher')


	def get_context_data(self,*args,**kwargs):

		context = super(TeacherDetail, self).get_context_data(*args,**kwargs)

		if self.request.user.profile.quran_class:

			quran_results = QuranExam.objects.filter(class_level=self.request.user.profile.quran_class)

			if quran_results.exists():
				quran_average = 0
				for result in quran_results:
					quran_average += result.exam_score
				quran_average = quran_average/len(quran_results)
				context['quran_average'] = quran_average


			quran_attendance_present = QuranAttendance.objects.filter(class_level=self.request.user.profile.quran_class,attendance='Present').count()
			quran_attendance_tardy = QuranAttendance.objects.filter(class_level=self.request.user.profile.quran_class,attendance='Tardy').count()
			quran_attendance_absent = QuranAttendance.objects.filter(class_level=self.request.user.profile.quran_class,attendance='Absent').count()
			total_quran_attendance = quran_attendance_present + quran_attendance_absent + quran_attendance_tardy

			if total_quran_attendance > 0:

				quran_attendance_average = ( quran_attendance_present + quran_attendance_tardy - (quran_attendance_tardy//2) ) / total_quran_attendance

				context['quran_attendance_average'] = quran_attendance_average*100

			quran_exam1_results = QuranExam.objects.filter(class_level=self.request.user.profile.quran_class, exam_number=1).order_by('exam_score')
			quran_exam2_results = QuranExam.objects.filter(class_level=self.request.user.profile.quran_class, exam_number=2).order_by('exam_score')
			quran_exam3_results = QuranExam.objects.filter(class_level=self.request.user.profile.quran_class, exam_number=3).order_by('exam_score')
			
			if quran_exam1_results.exists():
				context['quran_exam1_results'] = quran_exam1_results
			if quran_exam2_results.exists():
				context['quran_exam2_results'] = quran_exam2_results	
			if quran_exam3_results.exists():
				context['quran_exam3_results'] = quran_exam3_results	


		if self.request.user.profile.islamic_studies_class:

			islamic_studies_results = IslamicStudiesExam.objects.filter(class_level=self.request.user.profile.islamic_studies_class)

			if islamic_studies_results.exists():
				islamic_studies_average = 0
				for result in islamic_studies_results:
					islamic_studies_average += result.exam_score
				islamic_studies_average = islamic_studies_average/len(islamic_studies_results)
				context['islamic_studies_average'] = islamic_studies_average



			islamic_studies_attendance_present = IslamicStudiesAttendance.objects.filter(class_level=self.request.user.profile.islamic_studies_class,attendance='Present').count()
			islamic_studies_attendance_tardy = IslamicStudiesAttendance.objects.filter(class_level=self.request.user.profile.islamic_studies_class,attendance='Tardy').count()
			islamic_studies_attendance_absent = IslamicStudiesAttendance.objects.filter(class_level=self.request.user.profile.islamic_studies_class,attendance='Absent').count()
			total_islamic_studies_attendance = islamic_studies_attendance_present + islamic_studies_attendance_absent + islamic_studies_attendance_tardy

			if total_islamic_studies_attendance > 0:

				islamic_studies_attendance_average = ( islamic_studies_attendance_present + islamic_studies_attendance_tardy - (islamic_studies_attendance_tardy//2) ) / total_islamic_studies_attendance

				context['islamic_studies_attendance_average'] = islamic_studies_attendance_average*100


			islamic_studies_exam1_results = IslamicStudiesExam.objects.filter(class_level=self.request.user.profile.islamic_studies_class, exam_number=1).order_by('exam_score')
			islamic_studies_exam2_results = IslamicStudiesExam.objects.filter(class_level=self.request.user.profile.islamic_studies_class, exam_number=2).order_by('exam_score')
			islamic_studies_exam3_results = IslamicStudiesExam.objects.filter(class_level=self.request.user.profile.islamic_studies_class, exam_number=3).order_by('exam_score')
			
			if islamic_studies_exam1_results.exists():
				context['islamic_studies_exam1_results'] = islamic_studies_exam1_results
			if islamic_studies_exam2_results.exists():
				context['islamic_studies_exam2_results'] = islamic_studies_exam2_results	
			if islamic_studies_exam3_results.exists():
				context['islamic_studies_exam3_results'] = islamic_studies_exam3_results

		return context


class QuranSchoolWeeksView(LoginRequiredMixin, ListView):
	model = SchoolWeek
	template_name = 'quran_school_weeks.html'
	# def get_queryset(self):
	# 	return Schoo.objects.filter(class_level=self.request.user.profile.quran_class).order_by('-posted_date')

class QuranAttendanceList(LoginRequiredMixin, ListView):
	model = QuranAttendance
	template_name = 'teachers/quran_attendance_list.html'

	def get_context_data(self,*args,**kwargs):
		# print(**kwargs)
		context = super(QuranAttendanceList,self).get_context_data(*args,**kwargs)
		week_id = self.kwargs['pk']
		week = SchoolWeek.objects.filter(pk=week_id).first()
		context['week_number'] = week.week_number
		context['week_date'] = week.date
		return context


	def get_queryset(self):
		return QuranAttendance.objects.filter(student__profile__quran_class=self.request.user.profile.quran_class, week__pk=self.kwargs['pk'])




class QuranAttendanceUpdate(LoginRequiredMixin,UpdateView):

	model = QuranAttendance
	template_name = 'teachers/quran_attendance_update.html'
	form_class = QuranAttendanceForm

	def get_context_data(self,*args,**kwargs):
		context = super(QuranAttendanceUpdate,self).get_context_data(*args,**kwargs)
		student = self.kwargs['student']
		userobj = User.objects.filter(username__iexact=student).first()
		attd_id = self.kwargs['pk']
		week = QuranAttendance.objects.filter(pk=attd_id).first().week
		context['week_number'] = week.week_number
		context['week_date'] = week.date
		context['full_name'] = userobj.first_name+' '+userobj.last_name
		context['userobj'] = userobj
		return context

	def form_valid(self,form):
		context = self.get_context_data()
		self.object = form.save(commit=False)
		self.object.class_level = context['userobj'].profile.quran_class
		self.object.save()
		context['userobj'].profile.unseen_quran_attendance.add(self.object)
		return super().form_valid(form)



class QuranAttendanceStudentView(LoginRequiredMixin, ListView):

	model = QuranAttendance
	template_name = 'students/quran_attendance.html'

	def get_queryset(self):
		for attendance in self.request.user.profile.unseen_quran_attendance.all():
			self.request.user.profile.unseen_quran_attendance.remove(attendance)

		return QuranAttendance.objects.filter(student=self.request.user)



class IslamicStudiesSchoolWeeksView(LoginRequiredMixin, ListView):
	model = SchoolWeek
	template_name = 'islamic_studies_school_weeks.html'
	# def get_queryset(self):
	# 	return Schoo.objects.filter(class_level=self.request.user.profile.quran_class).order_by('-posted_date')


class IslamicStudiesAttendanceList(LoginRequiredMixin, ListView):
	model = IslamicStudiesAttendance
	template_name = 'teachers/islamic_studies_attendance_list.html'

	def get_context_data(self,*args,**kwargs):
		# print(**kwargs)
		context = super(IslamicStudiesAttendanceList,self).get_context_data(*args,**kwargs)
		week_id = self.kwargs['pk']
		week = SchoolWeek.objects.filter(pk=week_id).first()
		context['week_number'] = week.week_number
		context['week_date'] = week.date
		return context


	def get_queryset(self):
		return IslamicStudiesAttendance.objects.filter(student__profile__islamic_studies_class=self.request.user.profile.islamic_studies_class, week__pk=self.kwargs['pk'])




class IslamicStudiesAttendanceUpdate(LoginRequiredMixin,UpdateView):

	model = IslamicStudiesAttendance
	template_name = 'teachers/islamic_studies_attendance_update.html'
	form_class = IslamicStudiesAttendanceForm

	def get_context_data(self,*args,**kwargs):
		context = super(IslamicStudiesAttendanceUpdate,self).get_context_data(*args,**kwargs)
		student = self.kwargs['student']
		userobj = User.objects.filter(username__iexact=student).first()
		attd_id = self.kwargs['pk']
		week = IslamicStudiesAttendance.objects.filter(pk=attd_id).first().week
		context['week_number'] = week.week_number
		context['week_date'] = week.date
		context['full_name'] = userobj.first_name+' '+userobj.last_name
		context['userobj'] = userobj
		return context

	def form_valid(self,form):
		context = self.get_context_data()
		self.object = form.save(commit=False)
		self.object.class_level = context['userobj'].profile.islamic_studies_class
		self.object.save()
		context['userobj'].profile.unseen_islamic_studies_attendance.add(self.object)
		return super().form_valid(form)



class IslamicStudiesAttendanceStudentView(LoginRequiredMixin, ListView):

	model = IslamicStudiesAttendance
	template_name = 'students/islamic_studies_attendance.html'

	def get_queryset(self):
		for attendance in self.request.user.profile.unseen_islamic_studies_attendance.all():
			self.request.user.profile.unseen_islamic_studies_attendance.remove(attendance)

		return IslamicStudiesAttendance.objects.filter(student=self.request.user)


class QuranExamStudentView(LoginRequiredMixin, ListView):

	model = QuranExam
	template_name = 'students/quran_exam_scores.html'

	def get_queryset(self):
		for exam in self.request.user.profile.unseen_quran_exams.all():
			self.request.user.profile.unseen_quran_exams.remove(exam)

		return QuranExam.objects.filter(student=self.request.user)


class IslamicStudiesExamStudentView(LoginRequiredMixin, ListView):

	model = IslamicStudiesExam
	template_name = 'students/islamic_studies_exam_scores.html'

	def get_queryset(self):
		for exam in self.request.user.profile.unseen_islamic_studies_exams.all():
			self.request.user.profile.unseen_islamic_studies_exams.remove(exam)

		return IslamicStudiesExam.objects.filter(student=self.request.user)











