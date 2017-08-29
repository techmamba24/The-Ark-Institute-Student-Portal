"""arkportal URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from django.views.generic.base import TemplateView
from administrator.views import QuranRosterClasses, QuranRosterClassList, IslamicStudiesRosterClasses, IslamicStudiesRosterClassList, QuranPostsList,IslamicStudiesPostsList,QuranClassPostListView,IslamicStudiesClassPostListView,QuranClassExamScores,QuranClassesExamList,IslamicStudiesClassExamScores, IslamicStudiesClassesExamList, QuranClassWeekAttendance, QuranClassesAttendanceList, QuranClassWeeksList, IslamicStudiesClassWeekAttendance, IslamicStudiesClassesAttendanceList, IslamicStudiesClassWeeksList

urlpatterns = [
    url(r'^quran-class-rosters/$', QuranRosterClasses.as_view(),name='qrosters'),
    url(r'^quran-class-rosters/(?P<level>([1-9]|10))/$', QuranRosterClassList.as_view(),name='quranstudentlist'),
    url(r'^islamic-studies-class-rosters/$', IslamicStudiesRosterClasses.as_view(),name='isrosters'),
    url(r'^islamic-studies-class-rosters/(?P<level>([1-9]|10))/$', IslamicStudiesRosterClassList.as_view(),name='islamicstudiesstudentlist'),
    url(r'^quran-class-posts/$', QuranPostsList.as_view(),name='quran_posts_list'),
    url(r'^islamic-studies-class-posts/$', IslamicStudiesPostsList.as_view(),name='islamic_studies_posts_list'),
    url(r'^quran-class-posts/(?P<level>([1-9]|10))/$', QuranClassPostListView.as_view(),name='quranclassposts'),
    url(r'^islamic-studies-class-posts/(?P<level>([1-9]|10))/$', IslamicStudiesClassPostListView.as_view(),name='islamicstudiesclassposts'),
    url(r'^quran-class-exams/$', QuranClassesExamList.as_view(),name='quran_classes_exams'),
    url(r'^quran-class-exams/(?P<level>([1-9]|10))/$', QuranClassExamScores.as_view(),name='quran_class_exam_scores'),
    url(r'^islamic-studies-class-exams/$', IslamicStudiesClassesExamList.as_view(),name='islamic_studies_classes_exams'),
    url(r'^islamic-studies-class-exams/(?P<level>([1-9]|10))/$', IslamicStudiesClassExamScores.as_view(),name='islamic_studies_class_exam_scores'),
    url(r'^quran-class-attendance/$', QuranClassesAttendanceList.as_view(),name='quran_attendance_list'),
    url(r'^quran-class-attendance/(?P<level>([1-9]|10))/$', QuranClassWeeksList.as_view(),name='quran_weeks_list'),
    url(r'^quran-class-attendance/(?P<level>([1-9]|10))/(?P<week>\d+)/$', QuranClassWeekAttendance.as_view(),name='quran_week_attendance'),
    url(r'^islamic-studies-class-attendance/$', IslamicStudiesClassesAttendanceList.as_view(),name='islamic_studies_attendance_list'),
    url(r'^islamic-studies-class-attendance/(?P<level>([1-9]|10))/$', IslamicStudiesClassWeeksList.as_view(),name='islamic_studies_weeks_list'),
    url(r'^islamic-studies-class-attendance/(?P<level>([1-9]|10))/(?P<week>\d+)/$', IslamicStudiesClassWeekAttendance.as_view(),name='islamic_studies_week_attendance'),



]
