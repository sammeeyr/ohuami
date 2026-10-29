import json
from django.shortcuts import get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.views.decorators.http import require_POST
from apps.catalog.models import Product
from .models import Review
from .forms import ReviewForm


@require_POST
def submit_review(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_active=True)

    is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.content_type == 'application/json'

    if request.content_type == 'application/json':
        try:
            data = json.loads(request.body)
            form = ReviewForm(data)
        except Exception as e:
            return JsonResponse({'success': False, 'error': f"Invalid JSON payload: {str(e)}"}, status=400)
    else:
        form = ReviewForm(request.POST)

    if form.is_valid():
        review = form.save(commit=False)
        review.product = product
        if request.user.is_authenticated:
            review.user = request.user
            if not review.customer_name:
                review.customer_name = request.user.get_full_name() or request.user.email.split('@')[0]
        review.is_moderated = True
        review.save()

        msg = f"Thank you! Your {review.rating}-star review for '{product.name}' has been posted."
        messages.success(request, msg)

        if is_ajax:
            return JsonResponse({
                'success': True,
                'message': msg,
                'review': {
                    'id': review.id,
                    'customer_name': review.customer_name,
                    'rating': review.rating,
                    'title': review.title,
                    'comment': review.comment,
                    'created_at': review.created_at.strftime("%b %d, %Y"),
                }
            })
        return redirect('catalog:product_detail', slug=product.slug)
    else:
        errors = form.errors.as_text()
        messages.error(request, f"Please correct the errors in your review: {errors}")
        if is_ajax:
            return JsonResponse({'success': False, 'errors': form.errors}, status=400)
        return redirect('catalog:product_detail', slug=product.slug)
