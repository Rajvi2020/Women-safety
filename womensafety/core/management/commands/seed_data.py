from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from core.models import User, VerifiedService, Job, Scholarship, Resource, FAQ, Mentor

class Command(BaseCommand):
    help = 'Seeds database with initial data for SheShield AI'

    def handle(self, *args, **kwargs):
        # Create Admin (.com)
        if not User.objects.filter(username='admin@sheshield.com').exists():
            User.objects.create_superuser(
                username='admin@sheshield.com',
                email='admin@sheshield.com',
                password='admin123',
                first_name='SheShield',
                last_name='Admin',
                role='admin',
                phone='1234567890'
            )
            self.stdout.write(self.style.SUCCESS('Admin created (admin@sheshield.com / admin123)'))

        # Create Admin (.ai)
        if not User.objects.filter(username='admin@sheshield.ai').exists():
            User.objects.create_superuser(
                username='admin@sheshield.ai',
                email='admin@sheshield.ai',
                password='Admin@12345',
                first_name='SheShield',
                last_name='Admin',
                role='admin',
                phone='1234567890'
            )
            self.stdout.write(self.style.SUCCESS('Admin created (admin@sheshield.ai / Admin@12345)'))

        # Create Demo User (.com)
        if not User.objects.filter(username='user@sheshield.com').exists():
            User.objects.create_user(
                username='user@sheshield.com',
                email='user@sheshield.com',
                password='user1234',
                first_name='Rajvi',
                last_name='Sharma',
                role='user',
                phone='9876543210',
                city='Mumbai'
            )
            self.stdout.write(self.style.SUCCESS('Demo user created (user@sheshield.com / user1234)'))

        # Create Demo User (.ai)
        if not User.objects.filter(username='demo@sheshield.ai').exists():
            User.objects.create_user(
                username='demo@sheshield.ai',
                email='demo@sheshield.ai',
                password='Demo@12345',
                first_name='Rajvi',
                last_name='Sharma',
                role='user',
                phone='9876543210',
                city='Mumbai'
            )
            self.stdout.write(self.style.SUCCESS('Demo user created (demo@sheshield.ai / Demo@12345)'))

        # Create Demo Mentor (.com)
        if not User.objects.filter(username='mentor@sheshield.com').exists():
            mentor_user = User.objects.create_user(
                username='mentor@sheshield.com',
                email='mentor@sheshield.com',
                password='mentor1234',
                first_name='Ananya',
                last_name='Iyer',
                role='mentor',
                phone='9998887776',
                city='Bangalore'
            )
            Mentor.objects.create(
                user=mentor_user,
                title='Senior Software Engineer',
                company='Google',
                experience=8,
                bio='Passionate about guiding women in tech.',
                fee='Free',
                is_verified=True,
                is_online=True,
                rating=4.9,
                review_count=12,
                sessions_count=24
            )
            self.stdout.write(self.style.SUCCESS('Demo mentor created (mentor@sheshield.com / mentor1234)'))

        # Create Demo Mentor (.ai)
        if not User.objects.filter(username='mentor@sheshield.ai').exists():
            mentor_user = User.objects.create_user(
                username='mentor@sheshield.ai',
                email='mentor@sheshield.ai',
                password='Mentor@12345',
                first_name='Ananya',
                last_name='Iyer',
                role='mentor',
                phone='9998887776',
                city='Bangalore'
            )
            Mentor.objects.create(
                user=mentor_user,
                title='Senior Software Engineer',
                company='Google',
                experience=8,
                bio='Passionate about guiding women in tech.',
                fee='Free',
                is_verified=True,
                is_online=True,
                rating=4.9,
                review_count=12,
                sessions_count=24
            )
            self.stdout.write(self.style.SUCCESS('Demo mentor created (mentor@sheshield.ai / Mentor@12345)'))

        # Verified Services
        services = [
            {'name': 'National Women Helpline', 'number': '1091', 'icon': '📞', 'availability': '24x7'},
            {'name': 'Police Control Room', 'number': '112', 'icon': '🚓', 'availability': '24x7'},
            {'name': 'Ambulance Service', 'number': '102', 'icon': '🚑', 'availability': '24x7'},
            {'name': 'Domestic Abuse Helpline', 'number': '181', 'icon': '🛡️', 'availability': '24x7'},
        ]
        for s in services:
            VerifiedService.objects.get_or_create(name=s['name'], defaults=s)

        # Jobs
        jobs = [
            {
                'title': 'Frontend Engineer (React)',
                'company': 'Tech Solutions',
                'location': 'Remote / Mumbai',
                'salary': '₹12,0,000 - ₹18,0,000',
                'description': 'We are looking for a Frontend Engineer with experience in React and tailwind.',
                'category': 'STEM',
                'type': 'full-time',
                'is_women_friendly': True,
                'is_active': True,
            },
            {
                'title': 'Data Analyst',
                'company': 'FinAnalytics',
                'location': 'Bangalore',
                'salary': '₹8,0,000 - ₹11,0,000',
                'description': 'Join our growing team to handle financial data analysis using SQL and Python.',
                'category': 'Finance',
                'type': 'full-time',
                'is_women_friendly': True,
                'is_active': True,
            }
        ]
        for j in jobs:
            Job.objects.get_or_create(title=j['title'], company=j['company'], defaults=j)

        # Scholarships
        scholarships = [
            {
                'name': 'Women in Technology Scholarship 2025',
                'provider': 'Google India',
                'description': 'Supports women pursuing Computer Science or Engineering degrees. Includes mentorship and internship opportunities.',
                'amount': '₹1,00,000/year',
                'category': 'STEM',
                'level': 'Undergraduate',
                'deadline': timezone.now().date() + timezone.timedelta(days=60),
                'icon': '🎓',
                'apply_url': 'https://buildyourfuture.withgoogle.com/scholarships/generation-google-scholarship-apac/',
                'is_active': True,
            },
            {
                'name': 'Inspire Scholarship for Medical Sciences',
                'provider': 'Govt. of India – DST',
                'description': 'Government scholarship for women pursuing MBBS, BDS, or allied health science programs.',
                'amount': '₹80,000/year',
                'category': 'Medicine',
                'level': 'Postgraduate',
                'deadline': timezone.now().date() + timezone.timedelta(days=90),
                'icon': '💊',
                'apply_url': 'https://online-inspire.gov.in/',
                'is_active': True,
            }
        ]
        for s in scholarships:
            Scholarship.objects.get_or_create(name=s['name'], defaults=s)

        # FAQs
        faqs = [
            {'question': 'How does the Live Location feature work?', 'answer': 'You can start location sharing, and a secure real-time map link is shared with your selected emergency contacts.'},
            {'question': 'Are the mentors verified?', 'answer': 'Yes, all mentors on SheShield AI undergo document and profile verification before being listed.'},
        ]
        for f in faqs:
            FAQ.objects.get_or_create(question=f['question'], defaults=f)

        # Resources
        resources = [
            {
                'title': 'Know Your Safety Rights',
                'description': 'A comprehensive handbook of legal safety and workplace harassment prevention laws in India.',
                'category': 'legal',
                'url': 'https://www.advocatekhoj.com',
            },
            {
                'title': 'Self-Defense Basics Video',
                'description': 'Learn simple and highly effective self-defense techniques from professional trainers.',
                'category': 'video',
                'url': 'https://youtube.com',
            }
        ]
        for r in resources:
            Resource.objects.get_or_create(title=r['title'], defaults=r)

        self.stdout.write(self.style.SUCCESS('Successfully seeded database!'))
