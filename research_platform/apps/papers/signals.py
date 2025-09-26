# apps/papers/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Paper
from .background import executor
from ml_models.bart_summarizer_lambda import summarize_text_from_pdf


def process_summary(paper_id, pdf_file):
    from .models import Paper
    try:
        summary = summarize_text_from_pdf(pdf_file)
        Paper.objects.filter(id=paper_id).update(summary=summary)
    except Exception as e:
        # Log or print the error instead of failing silently
        print(f"[ERROR] Failing to generate summary for Paper {paper_id}: {e}")


@receiver(post_save, sender=Paper)
def generate_summary(sender, instance, created, **kwargs):
    if created and instance.pdf_path:
        # Run in background thread
        executor.submit(process_summary, instance.id, instance.pdf_path)
