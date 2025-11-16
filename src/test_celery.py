#!/usr/bin/env python
"""
Script to test Celery worker configuration and task execution
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from contact.tasks import send_contact_email_task
from contact.models import ContactMessage
from celery import current_app
import time

print("=" * 60)
print("CELERY DIAGNOSTICS")
print("=" * 60)

# 1. Check Celery configuration
print("\n1. Celery Configuration:")
print(f"   Broker URL: {current_app.conf.broker_url}")
print(f"   Result Backend: {current_app.conf.result_backend}")
print(f"   Task Serializer: {current_app.conf.task_serializer}")

# 2. Check registered tasks
print("\n2. Registered Tasks:")
tasks = list(current_app.tasks.keys())
contact_tasks = [t for t in tasks if 'contact' in t.lower()]
print(f"   Total registered tasks: {len(tasks)}")
print(f"   Contact tasks: {contact_tasks}")

# 3. Test task dispatch
print("\n3. Testing Task Dispatch:")
pending_msgs = ContactMessage.objects.filter(status='pending').order_by('id')[:1]

if pending_msgs.exists():
    msg = pending_msgs.first()
    print(f"   Using message ID: {msg.id}")
    print(f"   Status before: {msg.status}")

    # Dispatch task
    result = send_contact_email_task.delay(msg.id)
    print(f"   Task ID: {result.id}")
    print(f"   Task dispatched successfully!")

    # Wait a bit for worker to process
    print("   Waiting 5 seconds for worker to process...")
    time.sleep(5)

    # Check result
    msg.refresh_from_db()
    print(f"   Status after: {msg.status}")

    if msg.status == 'sent':
        print("   ✅ SUCCESS! Worker processed the task!")
    elif msg.status == 'failed':
        print(f"   ❌ FAILED! Error: {msg.error_message}")
    else:
        print("   ⚠️  WARNING! Task still pending - worker might not be running or processing tasks")
        print("\n   SOLUTION:")
        print("   1. Stop the current Celery worker (Ctrl+C)")
        print("   2. Restart it with: celery -A core worker -l info")
        print("   3. Run this test again")
else:
    print("   No pending messages to test")

print("\n" + "=" * 60)
print("DIAGNOSTIC COMPLETE")
print("=" * 60)
