from django.urls import path
from . import views

app_name = 'papers'

urlpatterns = [
    path('', views.PaperListView.as_view(), name='list'),
    path('upload/', views.PaperUploadView.as_view(), name='upload'),
    path('<int:pk>/', views.PaperDetailView.as_view(), name='detail'),
    path('<int:pk>/edit/', views.PaperEditView.as_view(), name='edit'),
    path('<int:pk>/delete/', views.PaperDeleteView.as_view(), name='delete'),
    path('<int:pk>/bookmark/', views.bookmark_paper, name='bookmark'),
    path('<int:pk>/rate/', views.rate_paper, name='rate'),
    path('<int:pk>/view-pdf/', views.view_paper_pdf, name='view_pdf'),
    path('<int:pk>/download/', views.download_paper, name='download'),
    path('bookmarks/', views.BookmarkListView.as_view(), name='bookmarks'),
    path('my-papers/', views.MyPapersView.as_view(), name='my_papers'),
    path('categories/', views.CategoryListView.as_view(), name='categories'),
    path('categories/<int:pk>/', views.CategoryDetailView.as_view(), name='category_detail'),
    path('pending-approval/', views.PendingApprovalView.as_view(), name='pending_approval'),
    path('<int:pk>/approve/', views.approve_paper, name='approve'),
    path('<int:pk>/reject/', views.reject_paper, name='reject'),
    path('recommendations/', views.get_recommendations, name='recommendations'),
    path('admin-manage/', views.AdminPaperListView.as_view(), name='admin_paper_manage'),
    path('<int:pk>/summary/', views.PaperSummaryView.as_view(), name='summary'),
    
]
