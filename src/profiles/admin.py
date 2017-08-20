from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from .models import Profile, QuranPost,QuranComment, IslamicStudiesPost, IslamicStudiesComment,QuranExam,IslamicStudiesExam, QuranAttendance, SchoolWeek, IslamicStudiesAttendance

class ProfileInline(admin.StackedInline):
	model = Profile
	can_delete = False
	verbose_name_plural = 'Profile'
	fk_name = 'user'

class CustomUserAdmin(UserAdmin):
	# list_display = UserAdmin.list_display + ('is_active',)
	inlines = (ProfileInline, )
	list_display = ('username','first_name','last_name','get_role','get_q_class','get_is_class','is_superuser')

	def get_role(self,instance):
		return instance.profile.role

	get_role.short_description = 'Role'

	def get_q_class(self,instance):
		return instance.profile.quran_class

	get_q_class.short_description = 'Quran Class'

	def get_is_class(self,instance):
		return instance.profile.islamic_studies_class

	get_is_class.short_description = 'Islamic Studies Class'


	def get_inline_instances(self, request, obj=None):
		if not obj:
			return list()
		return super(CustomUserAdmin, self).get_inline_instances(request, obj)


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
admin.site.register(QuranPost)
admin.site.register(QuranComment)
admin.site.register(IslamicStudiesPost)
admin.site.register(IslamicStudiesComment)
admin.site.register(QuranExam)
admin.site.register(IslamicStudiesExam)
admin.site.register(QuranAttendance)
admin.site.register(IslamicStudiesAttendance)
admin.site.register(SchoolWeek)



