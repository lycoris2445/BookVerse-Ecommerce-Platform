"""
Management command để build TF-IDF recommendations artifacts offline
Usage: python manage.py build_recommendations [--force]
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.recommendations.services import recommendation_engine
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Build TF-IDF recommendation artifacts offline'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force rebuild even if artifacts exist',
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Show detailed build information',
        )

    def handle(self, *args, **options):
        """Main command execution"""
        self.stdout.write(
            self.style.SUCCESS('Starting TF-IDF recommendations build...')
        )
        
        start_time = timezone.now()
        
        try:
            # Check if force rebuild is needed
            if options['force']:
                self.stdout.write('Force rebuild requested...')
                # Clear existing artifacts
                recommendation_engine.tfidf_matrix = None
                recommendation_engine.book_id_mapping = {}
                recommendation_engine.reverse_mapping = {}
                recommendation_engine.last_build_time = None
                
                # Clear cache
                if hasattr(recommendation_engine, 'get_books_content_data'):
                    recommendation_engine.get_books_content_data.cache_clear()
            
            # Check if rebuild is needed
            elif recommendation_engine.last_build_time:
                # Check if data is stale (older than 24 hours)
                time_since_build = timezone.now() - recommendation_engine.last_build_time
                if time_since_build.total_seconds() < 24 * 3600:  # 24 hours
                    self.stdout.write(
                        self.style.WARNING(
                            f'TF-IDF matrix was built {time_since_build} ago. '
                            'Use --force to rebuild anyway.'
                        )
                    )
                    return
            
            # Build TF-IDF matrix
            self.stdout.write('Building TF-IDF matrix from book content...')
            
            success = recommendation_engine.build_tfidf_matrix()
            
            if success:
                build_time = (timezone.now() - start_time).total_seconds()
                
                # Display build statistics
                matrix_shape = f"{len(recommendation_engine.tfidf_matrix)}x{len(recommendation_engine.vocabulary)}"
                num_books = len(recommendation_engine.book_id_mapping)
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✅ TF-IDF matrix built successfully in {build_time:.2f}s'
                    )
                )
                self.stdout.write(f'📊 Matrix shape: {matrix_shape}')
                self.stdout.write(f'📚 Books indexed: {num_books}')
                self.stdout.write(f'📝 Vocabulary size: {len(recommendation_engine.vocabulary)}')
                
                if options['verbose']:
                    self.stdout.write('\nBuild details:')
                    self.stdout.write(f'  - Build time: {recommendation_engine.last_build_time}')
                    self.stdout.write(f'  - Processing time: {build_time:.3f} seconds')
                    
                    # Show sample vocabulary
                    vocab_sample = recommendation_engine.vocabulary[:10]
                    self.stdout.write(f'  - Sample vocabulary: {vocab_sample}')
                
                # Test recommendation for validation
                self.stdout.write('\nValidating recommendation engine...')
                
                # Try to get recommendations for a test user (if any activities exist)
                from django.db import connection
                with connection.cursor() as cursor:
                    cursor.execute("SELECT DISTINCT CustomerID FROM useractivity LIMIT 1")
                    test_user = cursor.fetchone()
                
                if test_user:
                    test_user_id = test_user[0]
                    test_recs = recommendation_engine.get_content_recommendations(
                        user_id=test_user_id, 
                        k=5
                    )
                    
                    if test_recs:
                        self.stdout.write(
                            self.style.SUCCESS(
                                f'✅ Validation passed: Generated {len(test_recs)} recommendations for user {test_user_id}'
                            )
                        )
                        
                        if options['verbose']:
                            self.stdout.write('  Sample recommendations:')
                            for i, rec in enumerate(test_recs[:3], 1):
                                self.stdout.write(
                                    f'    {i}. {rec["title"]} (score: {rec["score"]:.4f})'
                                )
                    else:
                        self.stdout.write(
                            self.style.WARNING(
                                f'⚠️  User {test_user_id} has no recommendations (cold start)'
                            )
                        )
                else:
                    self.stdout.write(
                        self.style.WARNING('⚠️  No user activities found for validation')
                    )
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f'\n🎉 Recommendation system ready! Total time: {build_time:.2f}s'
                    )
                )
                
            else:
                self.stdout.write(
                    self.style.ERROR('❌ Failed to build TF-IDF matrix')
                )
                return
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error during build: {str(e)}')
            )
            logger.error(f'Error building recommendations: {str(e)}', exc_info=True)
            return
        
        # Show next steps
        self.stdout.write('\n📋 Next steps:')
        self.stdout.write('  1. Start Django server: python manage.py runserver')
        self.stdout.write('  2. Test API endpoint: GET /api/v1/recommendations/content?k=10')
        self.stdout.write('  3. Schedule daily rebuild: Add to cron/celery')
        self.stdout.write('\n💡 Tip: Use --verbose for detailed build information')
