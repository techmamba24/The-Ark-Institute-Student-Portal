from django.shortcuts import render, get_object_or_404, redirect, HttpResponse, render_to_response, Http404
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin, AccessMixin
from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.models import User
from profiles.models import QuranPost, QuranComment, IslamicStudiesPost,IslamicStudiesComment, Profile, QuranExam, IslamicStudiesExam, SchoolWeek, QuranAttendance, IslamicStudiesAttendance
from profiles.forms import QuranPostForm, QuranCommentForm, IslamicStudiesPostForm, IslamicStudiesCommentForm, QuranExamForm, IslamicStudiesExamForm, QuranAttendanceForm, IslamicStudiesAttendanceForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.db.models import Q
from itertools import chain
from operator import attrgetter
from django.db import IntegrityError
from django.utils import timezone
from django.contrib import messages
from django.core.urlresolvers import reverse, reverse_lazy



User = get_user_model()

quran_classes = [1,2,4,6,7,8,9,10]

islamic_studies_classes = [1,2,3,4,5,6,7,8,9,10]

class QuranRosterClasses(LoginRequiredMixin,PermissionRequiredMixin, TemplateView):
	template_name = 'administrator/quranrosterclasses.html'

	def get_context_data(self,*args,**kwargs):
		context = super(QuranRosterClasses,self).get_context_data(*args,**kwargs)
		context['quran_classes'] = quran_classes
		return context

	def has_permission(self):
		return self.request.user.is_staff


class QuranRosterClassList(LoginRequiredMixin, PermissionRequiredMixin, ListView):
	template_name = 'administrator/quranstudentlist.html'

	def get_queryset(self):
		class_level = self.kwargs.get('level')
		return User.objects.filter(profile__quran_class=class_level, profile__role='Student')

	def get_context_data(self,*args,**kwargs):
		context = super(QuranRosterClassList,self).get_context_data(*args,**kwargs)
		class_level = self.kwargs.get('level')
		context['class_level'] = class_level
		teachers = User.objects.filter(profile__quran_class=class_level, profile__role='Teacher')
		context['teachers'] = teachers
		return context

	def has_permission(self):
		return self.request.user.is_staff

class IslamicStudiesRosterClasses(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
	template_name = 'administrator/islamicstudiesrosterclasses.html'

	def get_context_data(self,*args,**kwargs):
		context = super(IslamicStudiesRosterClasses,self).get_context_data(*args,**kwargs)
		context['islamic_studies_classes'] = islamic_studies_classes
		return context

	def has_permission(self):
		return self.request.user.is_staff


class IslamicStudiesRosterClassList(LoginRequiredMixin, PermissionRequiredMixin,ListView):
	template_name = 'administrator/islamicstudiesstudentlist.html'

	def get_queryset(self):
		class_level = self.kwargs.get('level')
		return User.objects.filter(profile__islamic_studies_class=class_level, profile__role='Student')

	def get_context_data(self,*args,**kwargs):
		context = super(IslamicStudiesRosterClassList,self).get_context_data(*args,**kwargs)
		class_level = self.kwargs.get('level')
		context['class_level'] = class_level
		teachers = User.objects.filter(profile__islamic_studies_class=class_level, profile__role='Teacher')
		context['teachers'] = teachers
		return context

	def has_permission(self):
		return self.request.user.is_staff



class QuranPostsList(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
	template_name = 'administrator/quranpostslist.html'

	def get_context_data(self,*args,**kwargs):
		context = super(QuranPostsList,self).get_context_data(*args,**kwargs)
		context['quran_classes'] = quran_classes
		return context

	def has_permission(self):
		return self.request.user.is_staff


class QuranClassPostListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
	model = QuranPost
	template_name = 'administrator/quranclasspostslist.html'

	def get_queryset(self):
		class_level = self.kwargs.get('level')
		return QuranPost.objects.filter(class_level=class_level).order_by('-posted_date')

	def get_context_data(self,*args,**kwargs):
		context = super(QuranClassPostListView,self).get_context_data(*args,**kwargs)
		class_level = self.kwargs.get('level')
		context['class_level'] = class_level
		return context

	def has_permission(self):
		return self.request.user.is_staff


class IslamicStudiesPostsList(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
	template_name = 'administrator/islamicstudiespostslist.html'

	def get_context_data(self,*args,**kwargs):
		context = super(IslamicStudiesPostsList,self).get_context_data(*args,**kwargs)
		context['islamic_studies_classes'] = islamic_studies_classes
		return context

	def has_permission(self):
		return self.request.user.is_staff



class IslamicStudiesClassPostListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
	model = IslamicStudiesPost
	template_name = 'administrator/islamicstudiesclasspostslist.html'

	def get_queryset(self):
		class_level = self.kwargs.get('level')
		return IslamicStudiesPost.objects.filter(class_level=class_level).order_by('-posted_date')

	def get_context_data(self,*args,**kwargs):
		context = super(IslamicStudiesClassPostListView,self).get_context_data(*args,**kwargs)
		class_level = self.kwargs.get('level')
		context['class_level'] = class_level
		return context

	def has_permission(self):
		return self.request.user.is_staff


class QuranClassesExamList(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
	template_name = 'administrator/quranclassesexamlist.html'

	def get_context_data(self,*args,**kwargs):
		context = super(QuranClassesExamList,self).get_context_data(*args,**kwargs)
		context['quran_classes'] = quran_classes
		return context

	def has_permission(self):
		return self.request.user.is_staff


class QuranClassExamScores(LoginRequiredMixin, PermissionRequiredMixin, ListView):

	template_name = 'administrator/quranclassexamscores.html'

	def get_queryset(self):
		class_level = self.kwargs.get('level')
		return User.objects.filter(profile__quran_class=class_level,profile__role='Student')

	def get_context_data(self,*args,**kwargs):
		context = super(QuranClassExamScores,self).get_context_data(*args,**kwargs)
		class_level = self.kwargs.get('level')
		context['class_level'] = class_level
		return context

	def has_permission(self):
		return self.request.user.is_staff

class QuranExamScoreAdd(LoginRequiredMixin, PermissionRequiredMixin, CreateView):

	model = QuranExam
	form_class = QuranExamForm
	template_name = 'administrator/quran_exam_score_add.html'
	# success_url = '/administrator/quran-class-exams/'


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
			self.object.student = context['userobj']
			self.object.class_level = self.kwargs['level']
			self.object.save()
			messages.success(self.request, f"Successfully posted Exam {self.object.exam_number} score for {self.object.student.first_name} {self.object.student.last_name}")
			context['userobj'].profile.unseen_quran_exams.add(self.object)

		except IntegrityError as e:
			messages.error(self.request, f"Error: You already posted an Exam {self.object.exam_number} score for {self.object.student.first_name} {self.object.student.last_name}!")
			return redirect('administrator:quran_classes_exams')
		
		return super().form_valid(form)


	def get_success_url(self):
		return reverse_lazy('administrator:quran_class_exam_scores',kwargs={'level':self.kwargs['level']})

	def has_permission(self):
		return self.request.user.is_staff


class IslamicStudiesClassesExamList(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
	template_name = 'administrator/islamicstudiesclassesexamlist.html'

	def get_context_data(self,*args,**kwargs):
		context = super(IslamicStudiesClassesExamList,self).get_context_data(*args,**kwargs)
		context['islamic_studies_classes'] = islamic_studies_classes
		return context

	def has_permission(self):
		return self.request.user.is_staff


class IslamicStudiesClassExamScores(LoginRequiredMixin, PermissionRequiredMixin, ListView):

	template_name = 'administrator/islamicstudiesclassexamscores.html'

	def get_queryset(self):
		class_level = self.kwargs.get('level')
		return User.objects.filter(profile__islamic_studies_class=class_level,profile__role='Student')

	def get_context_data(self,*args,**kwargs):
		context = super(IslamicStudiesClassExamScores,self).get_context_data(*args,**kwargs)
		class_level = self.kwargs.get('level')
		context['class_level'] = class_level
		return context

	def has_permission(self):
		return self.request.user.is_staff


class IslamicStudiesExamScoreAdd(LoginRequiredMixin, PermissionRequiredMixin, CreateView):

	model = IslamicStudiesExam
	form_class = IslamicStudiesExamForm
	template_name = 'administrator/islamic_studies_exam_score_add.html'
	# success_url = reverse("administrator:islamic_studies_classes_exams")
	# success_url = '/administrator/islamic-studies-class-exams/'


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
			self.object.student = context['userobj']
			self.object.class_level = self.kwargs['level']
			self.object.save()
			messages.success(self.request, f"Successfully posted Exam {self.object.exam_number} score for {self.object.student.first_name} {self.object.student.last_name}")
			context['userobj'].profile.unseen_islamic_studies_exams.add(self.object)

		except IntegrityError as e:
			messages.error(self.request, f"Error: You already posted an Exam {self.object.exam_number} score for {self.object.student.first_name} {self.object.student.last_name}!")
			return redirect('administrator:islamic_studies_classes_exams')
		
		return super().form_valid(form)


	def get_success_url(self):
		return reverse_lazy('administrator:quran_class_exam_scores',kwargs={'level':self.kwargs['level']})

	def has_permission(self):
		return self.request.user.is_staff


class QuranClassesAttendanceList(LoginRequiredMixin,PermissionRequiredMixin,TemplateView):

	template_name = 'administrator/quranclassesattendancelist.html'

	def get_context_data(self,*args,**kwargs):
		context = super(QuranClassesAttendanceList,self).get_context_data(*args,**kwargs)
		context['quran_classes'] = quran_classes
		return context

	def has_permission(self):
		return self.request.user.is_staff


class QuranClassWeeksList(LoginRequiredMixin,PermissionRequiredMixin,ListView):

	model = SchoolWeek
	template_name = 'administrator/quranclassweekslist.html'

	def get_context_data(self,*args,**kwargs):
		context = super(QuranClassWeeksList,self).get_context_data(*args,**kwargs)
		class_level = self.kwargs.get('level')
		context['class_level'] = class_level
		return context

	def has_permission(self):
		return self.request.user.is_staff

class QuranClassWeekAttendance(LoginRequiredMixin,PermissionRequiredMixin,ListView):

	template_name = 'administrator/quranclassweekattendance.html'

	def get_queryset(self):
		week_number = self.kwargs.get('week')
		class_level = self.kwargs.get('level')
		return QuranAttendance.objects.filter(week__week_number=week_number,class_level=class_level)

	def get_context_data(self,*args,**kwargs):
		context = super(QuranClassWeekAttendance,self).get_context_data(*args,**kwargs)
		class_level = self.kwargs.get('level')
		week_number = self.kwargs.get('week')
		context['class_level'] = class_level
		context['week_number'] = week_number
		return context

	def has_permission(self):
		return self.request.user.is_staff

class QuranClassWeekAttendanceUpdate(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):

	model = QuranAttendance
	template_name = 'administrator/quran_attendance_update.html'
	form_class = QuranAttendanceForm

	def get_context_data(self,*args,**kwargs):
		context = super(QuranClassWeekAttendanceUpdate,self).get_context_data(*args,**kwargs)
		student = self.kwargs['student']
		userobj = User.objects.filter(username__iexact=student).first()
		attd_id = self.kwargs['pk']
		week = QuranAttendance.objects.filter(pk=attd_id).first().week
		context['week_number'] = week.week_number
		context['week_date'] = week.date
		context['full_name'] = userobj.first_name+' '+userobj.last_name
		context['userobj'] = userobj
		class_level = self.kwargs.get('level')
		week_number = self.kwargs.get('week')
		context['class_level'] = class_level
		context['week_number'] = week_number
		return context

	def form_valid(self,form):
		context = self.get_context_data()
		self.object = form.save(commit=False)
		self.object.class_level = context['userobj'].profile.quran_class
		self.object.save()
		context['userobj'].profile.unseen_quran_attendance.add(self.object)
		return super().form_valid(form)

	def get_success_url(self):
		return reverse_lazy('administrator:quran_week_attendance', kwargs={'level':self.kwargs.get('level'), 'week':self.kwargs.get('week')})

	def has_permission(self):
		return self.request.user.is_staff


class IslamicStudiesClassesAttendanceList(LoginRequiredMixin,PermissionRequiredMixin,TemplateView):

	template_name = 'administrator/islamicstudiesclassesattendancelist.html'

	def get_context_data(self,*args,**kwargs):
		context = super(IslamicStudiesClassesAttendanceList,self).get_context_data(*args,**kwargs)
		context['islamic_studies_classes'] = islamic_studies_classes
		return context

	def has_permission(self):
		return self.request.user.is_staff


class IslamicStudiesClassWeeksList(LoginRequiredMixin,PermissionRequiredMixin,ListView):

	model = SchoolWeek
	template_name = 'administrator/islamicstudiesclassweekslist.html'

	def get_context_data(self,*args,**kwargs):
		context = super(IslamicStudiesClassWeeksList,self).get_context_data(*args,**kwargs)
		class_level = self.kwargs.get('level')
		context['class_level'] = class_level
		return context

	def has_permission(self):
		return self.request.user.is_staff

class IslamicStudiesClassWeekAttendance(LoginRequiredMixin,PermissionRequiredMixin,ListView):

	template_name = 'administrator/islamicstuidesclassweekattendance.html'

	def get_queryset(self):
		week_number = self.kwargs.get('week')
		class_level = self.kwargs.get('level')
		return IslamicStudiesAttendance.objects.filter(week__week_number=week_number,class_level=class_level)

	def get_context_data(self,*args,**kwargs):
		context = super(IslamicStudiesClassWeekAttendance,self).get_context_data(*args,**kwargs)
		class_level = self.kwargs.get('level')
		week_number = self.kwargs.get('week')
		context['class_level'] = class_level
		context['week_number'] = week_number
		return context

	def has_permission(self):
		return self.request.user.is_staff

class IslamicStudiesClassWeekAttendanceUpdate(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):

	model = IslamicStudiesAttendance
	template_name = 'administrator/islamic_studies_attendance_update.html'
	form_class = IslamicStudiesAttendanceForm

	def get_context_data(self,*args,**kwargs):
		context = super(IslamicStudiesClassWeekAttendanceUpdate,self).get_context_data(*args,**kwargs)
		student = self.kwargs['student']
		userobj = User.objects.filter(username__iexact=student).first()
		attd_id = self.kwargs['pk']
		week = IslamicStudiesAttendance.objects.filter(pk=attd_id).first().week
		context['week_number'] = week.week_number
		context['week_date'] = week.date
		context['full_name'] = userobj.first_name+' '+userobj.last_name
		context['userobj'] = userobj
		class_level = self.kwargs.get('level')
		week_number = self.kwargs.get('week')
		context['class_level'] = class_level
		context['week_number'] = week_number
		return context

	def form_valid(self,form):
		context = self.get_context_data()
		self.object = form.save(commit=False)
		self.object.class_level = context['userobj'].profile.islamic_studies_class
		self.object.save()
		context['userobj'].profile.unseen_islamic_studies_attendance.add(self.object)
		return super().form_valid(form)

	def get_success_url(self):
		return reverse_lazy('administrator:islamic_studies_week_attendance', kwargs={'level':self.kwargs.get('level'), 'week':self.kwargs.get('week')})

	def has_permission(self):
		return self.request.user.is_staff



