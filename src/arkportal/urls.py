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
from django.conf.urls import url
from django.contrib import admin
from django.views.generic.base import TemplateView
from django.contrib.auth.views import LoginView, LogoutView
from profiles.views import DashboardView, QuranClassListView, ISClassListView, QuranPostListView, QuranPostDetailView, QuranCreatePostView, add_comment_to_quran_post, IslamicStudiesPostListView, IslamicStudiesPostDetailView, IslamicStudiesCreatePostView, add_comment_to_islamic_studies_post, QuranTeacherStudentList, QuranExamScoreAdd, StudentDetail, QuranExamScoreUpdate, IslamicStudiesExamScoreAdd, IslamicStudiesTeacherStudentList, IslamicStudiesExamScoreUpdate,QuranSchoolWeeksView, QuranAttendanceList, QuranAttendanceUpdate, QuranAttendanceStudentView, IslamicStudiesSchoolWeeksView, IslamicStudiesAttendanceList, IslamicStudiesAttendanceUpdate, IslamicStudiesAttendanceStudentView

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', TemplateView.as_view(template_name='home.html'), name='home'),
    url(r'^login/$', LoginView.as_view(template_name='registration/login.html'),name='login'),
    url(r'^logout/$', LogoutView.as_view(),name='logout'),
    url(r'^dashboard/$', DashboardView.as_view(),name='dashboard'),
    url(r'^students/(?P<username>[\w-]+)/$', StudentDetail.as_view(),name='student_detail'),
    url(r'^quran-class-roster/$', QuranClassListView.as_view(),name='qroster'),
    url(r'^islamic-studies-class-roster/$', ISClassListView.as_view(),name='isroster'),
    url(r'^quran-class-students/$', QuranTeacherStudentList.as_view(),name='quran_student_list'),
    url(r'^quran-class-student/exam-scores-add/(?P<student>[\w-]+)/$', QuranExamScoreAdd.as_view(),name='quran_score_add'),
    url(r'^quran-class-student/exam-scores-add/(?P<student>[\w-]+)/(?P<pk>\d+)/$', QuranExamScoreUpdate.as_view(),name='quran_score_update'),
    url(r'^islamic-studies-class-students/$', IslamicStudiesTeacherStudentList.as_view(),name='islamic_studies_student_list'),
    url(r'^islamic-studies-class-student/exam-scores-add/(?P<student>[\w-]+)/$', IslamicStudiesExamScoreAdd.as_view(),name='islamic_studies_score_add'),
    url(r'^islamic-studies-class-student/exam-scores-add/(?P<student>[\w-]+)/(?P<pk>\d+)/$', IslamicStudiesExamScoreUpdate.as_view(),name='islamic_studies_score_update'),
    url(r'^quran-class-posts/$', QuranPostListView.as_view(),name='quran_post_list'),
    url(r'^quran-class-posts/create/$', QuranCreatePostView.as_view(),name='quran_post_new'),
    url(r'^quran-class-posts/(?P<pk>\d+)/$', QuranPostDetailView.as_view(),name='quran_post_detail'),
    url(r'^quran-class-posts/(?P<pk>\d+)/comment/$', add_comment_to_quran_post,name='comment_quran_post'),
    url(r'^islamic-studies-class-posts/$', IslamicStudiesPostListView.as_view(),name='islamic_studies_post_list'),
    url(r'^islamic-studies-class-posts/create/$', IslamicStudiesCreatePostView.as_view(),name='islamic_studies_post_new'),
    url(r'^islamic-studies-class-posts/(?P<pk>\d+)/$', IslamicStudiesPostDetailView.as_view(),name='islamic_studies_post_detail'),
    url(r'^islamic-studies-class-posts/(?P<pk>\d+)/comment/$', add_comment_to_islamic_studies_post,name='comment_islamic_studies_post'),
    url(r'^quran-class-students/attendance/$', QuranSchoolWeeksView.as_view(),name='quran_school_weeks'),
    url(r'^quran-class-students/attendance/(?P<pk>\d+)/student-list/$', QuranAttendanceList.as_view(),name='quran_attendance_list'),
    url(r'^quran-class-students/attendance/student-list/(?P<student>[\w-]+)/(?P<pk>\d+)$', QuranAttendanceUpdate.as_view(),name='quran_attendance_update'),
    url(r'^quran-class/attendance/$', QuranAttendanceStudentView.as_view(),name='student_quran_attendance'),
    url(r'^islamic-studies-class-students/attendance/$', IslamicStudiesSchoolWeeksView.as_view(),name='islamic_studies_school_weeks'),
    url(r'^islamic-studies-class-students/attendance/(?P<pk>\d+)/student-list/$', IslamicStudiesAttendanceList.as_view(),name='islamic_studies_attendance_list'),
    url(r'^islamic-studies-class-students/attendance/student-list/(?P<student>[\w-]+)/(?P<pk>\d+)$', IslamicStudiesAttendanceUpdate.as_view(),name='islamic_studies_attendance_update'),
    url(r'^islamic-studies-class/attendance/$', IslamicStudiesAttendanceStudentView.as_view(),name='student_islamic_studies_attendance'),
]
