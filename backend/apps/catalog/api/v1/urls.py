from rest_framework.routers import DefaultRouter
from .views import BookViewSet, AuthorViewSet, CategoryViewSet, PublisherViewSet

router = DefaultRouter()
router.register('books', BookViewSet)
router.register('authors', AuthorViewSet)
router.register('categories', CategoryViewSet)
router.register('publishers', PublisherViewSet)

urlpatterns = router.urls
