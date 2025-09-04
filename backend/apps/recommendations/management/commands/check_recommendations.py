"""
Management command để kiểm tra status của recommendation system
Usage: python manage.py check_recommendations
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.recommendations.services import recommendation_engine
from django.db import connection


class Command(BaseCommand):
    help = 'Check status of recommendation system'

    def handle(self, *args, **options):
        """Check recommendation system status"""
        self.stdout.write(
            self.style.HTTP_INFO('🔍 Checking recommendation system status...\n')
        )
        
        # Get build info
        build_info = recommendation_engine.get_build_info()
        
        if build_info['status'] == 'not_built':
            self.stdout.write(
                self.style.WARNING('❌ TF-IDF matrix not built yet')
            )
            self.stdout.write('   Run: python manage.py build_recommendations')
        else:
            self.stdout.write(
                self.style.SUCCESS('✅ TF-IDF matrix is ready')
            )
            self.stdout.write(f'   📊 {build_info["message"]}')
            self.stdout.write(f'   📈 Matrix shape: {build_info["matrix_shape"]}')
            self.stdout.write(f'   📚 Books indexed: {build_info["num_books"]}')
            self.stdout.write(f'   📝 Vocabulary size: {build_info["vocabulary_size"]}')
            
            if build_info['build_time']:
                time_since = timezone.now() - build_info['build_time']
                self.stdout.write(f'   ⏰ Built: {time_since} ago')
        
        # Check data availability
        self.stdout.write('\n📊 Data availability:')
        
        try:
            with connection.cursor() as cursor:
                # Check books
                cursor.execute("SELECT COUNT(*) FROM book WHERE Stock > 0")
                book_count = cursor.fetchone()[0]
                self.stdout.write(f'   📚 Books in stock: {book_count}')
                
                # Check user activities
                cursor.execute("SELECT COUNT(*) FROM useractivity")
                activity_count = cursor.fetchone()[0]
                self.stdout.write(f'   👥 User activities: {activity_count}')
                
                # Check unique users with activities
                cursor.execute("SELECT COUNT(DISTINCT CustomerID) FROM useractivity")
                users_with_activity = cursor.fetchone()[0]
                self.stdout.write(f'   🙋 Active users: {users_with_activity}')
                
                # Recent activities (last 7 days)
                cursor.execute("""
                    SELECT COUNT(*) FROM useractivity 
                    WHERE ActivityTime >= DATE_SUB(NOW(), INTERVAL 7 DAY)
                """)
                recent_activities = cursor.fetchone()[0]
                self.stdout.write(f'   🔥 Recent activities (7 days): {recent_activities}')
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'   ❌ Error checking database: {str(e)}')
            )
        
        # Performance test if system is ready
        if build_info['status'] == 'ready':
            self.stdout.write('\n⚡ Performance test:')
            
            try:
                # Find a user with activities
                with connection.cursor() as cursor:
                    cursor.execute("""
                        SELECT CustomerID, COUNT(*) as activity_count
                        FROM useractivity 
                        GROUP BY CustomerID 
                        ORDER BY activity_count DESC 
                        LIMIT 1
                    """)
                    test_user_data = cursor.fetchone()
                
                if test_user_data:
                    test_user_id, activity_count = test_user_data
                    
                    start_time = timezone.now()
                    recommendations = recommendation_engine.get_content_recommendations(
                        user_id=test_user_id, k=10
                    )
                    response_time = (timezone.now() - start_time).total_seconds() * 1000
                    
                    self.stdout.write(f'   👤 Test user: {test_user_id} ({activity_count} activities)')
                    self.stdout.write(f'   📋 Recommendations: {len(recommendations)}')
                    self.stdout.write(f'   ⏱️  Response time: {response_time:.2f}ms')
                    
                    if response_time > 150:
                        self.stdout.write(
                            self.style.WARNING(f'   ⚠️  Response time > 150ms target')
                        )
                    else:
                        self.stdout.write(
                            self.style.SUCCESS(f'   ✅ Response time within target (<150ms)')
                        )
                else:
                    self.stdout.write('   ⚠️  No users with activities found for testing')
                    
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'   ❌ Performance test failed: {str(e)}')
                )
        
        # Show recommendations
        self.stdout.write('\n💡 Recommendations:')
        if build_info['status'] == 'not_built':
            self.stdout.write('   1. Run: python manage.py build_recommendations')
            self.stdout.write('   2. Test API: GET /api/v1/recommendations/content')
        else:
            self.stdout.write('   • System is ready for production')
            self.stdout.write('   • Consider daily rebuilds for fresh data')
            self.stdout.write('   • Monitor response times and accuracy')
